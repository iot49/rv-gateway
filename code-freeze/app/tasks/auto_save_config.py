import uasyncio as asyncio
from time import time

from utilities import config
from .. import webapp


async def main():
    """Save config every `interval` seconds if changed."""
    while True:
        if config.modified():
            config.save()
            # update all connected clients
            await webapp.send_all({ 'tag': 'config_put', 'value': config.get() })
            # wait a bit before the next save ...
            await asyncio.sleep(10) 
        # check once a second
        await asyncio.sleep(1)
