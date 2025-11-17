# Forged Python Client

This package is a client to interface with the forged.dev manufacturing/provisioning service.

When used in the automated Forged provisioner UI, uploading data blocks can be accomplished as
simply as:

```py
import forged

def main():
    # Upload a single block value for the current device.
    forged.upload_value("my_block_name", 10.0)
```

Forged also supports async code natively:
```py
from forged import Forged

async def main():
    await Forged.upload_value("my_block", 10.0)
    blocks = await Forged.blocks()
    assert blocks["my_block"] == 10.0
```
