import uasyncio as asyncio
import gc
from ..state import update

async def main():
    gc.threshold(100000)
    while True:
        await update('RAM', 'free',  gc.mem_free())
        await update('RAM', 'alloc', gc.mem_alloc())
        gc.collect()
        await asyncio.sleep(60)
