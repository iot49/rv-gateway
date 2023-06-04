import uasyncio as asyncio
from esp32 import CAN

BAUDRATE_250k = 250000


"""
https://github.com/micropython/micropython/pull/9532

from https://github.com/FeroxTL/micropython-can/tree/esp32-can

https://github.com/micropython/micropython/compare/master...FeroxTL:micropython-can:esp32-can

"""
class RVC:
    
    def __init__(self):
        self._can = can = CAN(0, tx=CAN_TX, rx=CAN_RX, mode=CAN.NORMAL, baudrate=BAUDRATE_250k)
        can.setfilter(0, CAN.FILTER_ADDRESS, params=[0x0], extframe=True)  

   
    async def run(self):
        while True:
            # print("rvc info", self._can.info())
            if self._can.any():
                print("rvc got", self._can.recv()) 
            await asyncio.sleep(0)
            

async def main():
    rvc = RVC()
    await rvc.run()
    

try:
    from xiao_s3 import CAN_RX, CAN_TX
except ImportError:
    print("RVC not available")

    async def main():
        pass