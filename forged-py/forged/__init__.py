#!/usr/bin/python3
import asyncio

from forged.client import Forged


def upload_value(*args, **kwargs):
    """Upload a value to a forged block."""
    asyncio.run(Forged.upload_value(*args, **kwargs))


def blocks(*args, **kwargs):
    """Get block results from the current forged device."""
    return asyncio.run(Forged.blocks(*args, **kwargs))
