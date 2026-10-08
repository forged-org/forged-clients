#!/usr/bin/python3
"""
Forged client module

Author: Forged.dev

Description: Utilities for uploading data to forged.dev test runs from custom tests.
"""
import asyncio
import io
import logging
import os
import socket
from typing import Union, Dict
import json

import aiohttp
import gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportError, TransportQueryError

# The default endpoint to use when connecting to the cloud-based forged.dev service.
DEFAULT_FORGED_API_ENDPOINT = "https://api.forged.dev"

# Errors from talking to forged.dev that are logged and ignored by the upload helpers, so that a
# failed upload does not abort the test that is running.
UPLOAD_ERRORS = (TransportError, aiohttp.ClientError, asyncio.TimeoutError)


def _describe_error(error: Exception) -> str:
    """Describe an upload error for logging, keeping the line breaks in server error messages."""
    if isinstance(error, TransportQueryError) and error.errors:
        return "\n".join(str(entry.get("message", entry)) for entry in error.errors)
    return str(error)


class Forged:
    """The main method for creating a connection to forged.dev.

    Example:
    ```
    # Use a token automatically injected via the environment
    # Note: You can also pass the token here directly.
    with Forged() as client:
        # Assign the value of 3.5 to the block `test_data`
        client.upload_block("test_data", 3.5)
    ```
    """

    def __init__(self, token=None, url=DEFAULT_FORGED_API_ENDPOINT):
        """Configure the connection parameters.

        Args:
            * `token` - The token to use for authentication. If unspecified, the environment
              variable `FORGED_API_TOKEN` will be used instead.
            * `url` - The URL to connect to. The default value connects to forged.dev's cloud
              service.
        """
        if not token:
            token = os.environ.get("FORGED_API_TOKEN")

        # If there's a URL injected by the provisioner into the environment, use that URL instead of
        # the default.
        environment_url = os.environ.get("FORGED_API_URL")
        if environment_url:
            logging.info("Overriding provided URL to %s", environment_url)
            url = environment_url

        assert token is not None, "Please provide a forged API token"

        transport = AIOHTTPTransport(
            url=url, headers={"Authorization": f"Bearer {token}"}
        )
        self.client = gql.Client(transport=transport, fetch_schema_from_transport=True)
        self.session = None

    async def __aenter__(self, *args, **kwargs):
        return await ForgedSession._create(await self.client.__aenter__())

    async def __aexit__(self, *args, **kwargs):
        await self.client.__aexit__(*args, **kwargs)

    @classmethod
    async def upload_value(
        cls,
        name: str,
        value: Union[float, int, str],
        token=None,
        url=DEFAULT_FORGED_API_ENDPOINT,
    ):
        """Upload a singular value data block to the current run.

        Note:
            If no token is provided and one is not found in the environment, the block upload is
            silently ignored. Errors communicating with forged.dev are logged and ignored.

        Args:
            * `name` - The name of the block being uploaded.
            * `value` - The value to upload to the block.
            * `token` - The token to use for authentication. If unspecified, the environment
              variable `FORGED_API_TOKEN` will be used instead.
            * `url` - The URL to connect to. The default value connects to forged.dev's cloud
              service.
        """
        if token is None:
            token = os.environ.get("FORGED_API_TOKEN")

        logging.info(f"Uploading {name}={value}")

        if not token:
            logging.warning("No forged token was found. Skipping value upload")
            return

        try:
            async with cls(token, url) as client:
                await client.upload_value(name, value)
        except UPLOAD_ERRORS as error:
            logging.error("Failed to upload %s: %s", name, _describe_error(error))

    @classmethod
    async def upload_block(
        cls, name: str, data: Dict, token=None, url=DEFAULT_FORGED_API_ENDPOINT
    ):
        """Upload a block to the forged device.

        Args:
            * `name` - The name of the block being uploaded.
            * `data` - The data to upload to the forged API, properly formatted according to the
            schema.
            * `token` - The token to use for authentication. If unspecified, the environment
              variable `FORGED_API_TOKEN` will be used instead.
            * `url` - The URL to connect to. The default value connects to forged.dev's cloud
              service.

        Note:
            If no token is provided and one is not found in the environment, the block upload is
            silently ignored. Errors communicating with forged.dev are logged and ignored.
        """
        if token is None:
            token = os.environ.get("FORGED_API_TOKEN")

        logging.info(f"Uploading {name}={data}")

        if not token:
            logging.warning("No forged token was found. Skipping value upload")
            return
        try:
            async with cls(token, url) as client:
                await client.upload_block(name, data)
        except UPLOAD_ERRORS as error:
            logging.error("Failed to upload %s: %s", name, _describe_error(error))

    @classmethod
    async def upload_attachment(
        cls, file_path: str, token=None, url=DEFAULT_FORGED_API_ENDPOINT
    ):
        """Attach a file, such as a plot or a log, to the current run.

        Args:
            * `file_path` - The path of the file to attach. The file is attached under its base name.
            * `token` - The token to use for authentication. If unspecified, the environment
              variable `FORGED_API_TOKEN` will be used instead.
            * `url` - The URL to connect to. The default value connects to forged.dev's cloud
              service.

        Note:
            If no token is provided and one is not found in the environment, the attachment upload
            is silently ignored. Errors communicating with forged.dev are logged and ignored.
        """
        if token is None:
            token = os.environ.get("FORGED_API_TOKEN")

        logging.info(f"Attaching {file_path}")

        if not token:
            logging.warning("No forged token was found. Skipping attachment upload")
            return
        try:
            async with cls(token, url) as client:
                await client.upload_attachment(file_path)
        except UPLOAD_ERRORS as error:
            logging.error("Failed to attach %s: %s", file_path, _describe_error(error))

    @classmethod
    async def blocks(cls, token=None, url=DEFAULT_FORGED_API_ENDPOINT):
        """Get all of the blocks for the current device."""
        async with cls(token, url) as client:
            return await client.blocks()

    @classmethod
    def user_input(cls, message: str, request_response=True) -> str:
        """Request user input during a run execution.

        Args:
            * `message` - The prompt message to display to the user.

        Note: If there's no active forged run, this will use the built in `input()` function
        instead.
        """
        tcp_endpoint = os.environ.get("FORGED_INPUT_SOCKET")

        if tcp_endpoint:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            (host, port) = tcp_endpoint.split(":")
            sock.connect((host, int(port)))

            request = {"message": message, "response_requested": request_response}
            payload = json.dumps(request)
            sock.sendall(payload.encode("ascii"))

            response = json.loads(sock.recv(256).decode("ascii"))
            sock.close()
            return response["message"]
        else:
            return input(message)


class ForgedSession:
    """An asynchronous connection with the forged.dev run."""

    @classmethod
    async def _create(cls, session):
        """Create the session from a graphQL connection."""
        provisioner_query = gql.gql(
            """
        query getRunData {
            currentProvisioner {
                projectId
            }
        }"""
        )
        provisioner = await session.execute(provisioner_query)
        project_id = provisioner["currentProvisioner"]["projectId"]
        return cls(session, project_id)

    def __init__(self, session, project_id: str):
        """Constructor"""
        self.session = session
        self.project_id = project_id

    async def blocks(self):
        blocks_query = gql.gql(
            """
        query getBlocks {
            currentProvisioner {
                currentRun {
                    blocks {
                        dataDecoded
                        schema {
                            name
                        }
                    }
                }
            }
        }
        """
        )

        query = await self.session.execute(blocks_query)

        blocks = {}
        for block in query["currentProvisioner"]["currentRun"]["blocks"]:
            data = block["dataDecoded"]
            blocks[block["schema"]["name"]] = block["dataDecoded"][list(data.keys())[0]]

        return blocks

    async def upload_value(self, name: str, value: Union[float, int, str]):
        """Upload a block that contains a single value."""
        try:
            upload = await self.upload_block(name, {"value": value})
        except TransportQueryError as error:
            logging.warning("Failed to upload %s: %s", name, _describe_error(error))

    async def upload_block(self, name: str, data: Dict):
        """Upload a block of data to the current run.

        Note:
            This uploads raw data to the block in an unformatted manner. The user is responsible for
            constructing the proper data format for the given schema. Use other upload methods if
            you would like to have the data structured for you.

        Args:
            * `name` - The name of the block being uploaded.
            * `data` - The data associated with the block.
        """
        block_mutation = gql.gql(
            """
        mutation CreateBlock($schemaName: String!, $data: JSON!) {
            blockCreate(schemaName: $schemaName, data: $data) {
                id
            }
        }"""
        )

        result = await self.session.execute(
            block_mutation, variable_values={"schemaName": name, "data": data}
        )

        return result["blockCreate"]["id"]

    async def upload_attachment(self, file_path: str):
        """Attach a file to the current run.

        Args:
            * `file_path` - The path of the file to attach. The file is attached under its base name
              rather than its full local path.

        Returns:
            The ID of the created attachment.
        """
        attachment_mutation = gql.gql(
            """
        mutation CreateAttachment($data: Upload!) {
            attachmentCreate(data: $data) {
                id
            }
        }"""
        )

        with open(file_path, "rb") as file:
            upload = io.BytesIO(file.read())

        # The multipart upload names the file after the stream's `name`, which would otherwise be
        # the full local path.
        upload.name = os.path.basename(file_path)

        result = await self.session.execute(
            attachment_mutation, variable_values={"data": upload}, upload_files=True
        )

        return result["attachmentCreate"]["id"]
