import uasyncio as asyncio

import busio
from adafruit_lsm6ds.lsm6ds3trc import LSM6DS3TRC
from adafruit_lsm6ds import Rate, AccelRange, GyroRange

from ..state import update


class IMU:
    
    def __init__(self):
        i2c = busio.I2C(0, IMU_SCL, IMU_SDA)
        self._imu = imu = LSM6DS3TRC(i2c)

        imu.accelerometer_data_rate = Rate.RATE_12_5_HZ
        imu.accelerometer_range = AccelRange.RANGE_2G

        imu.gyro_data_rate = Rate.RATE_12_5_HZ
        imu.gyro_range = GyroRange.RANGE_125_DPS
   
    async def run(self, rate: float):
        imu = self._imu
        while True:
            a = imu.acceleration
            r = imu.gyro
            await update('imu', 'accel-x', a[0])
            await update('imu', 'accel-y', a[1])
            await update('imu', 'accel-z', a[2])
            await update('imu', 'rate-x',  r[0])
            await update('imu', 'rate-y',  r[1])
            await update('imu', 'rate-z',  r[2])
            await asyncio.sleep(rate)
            

async def main(rate: float = 5.0):
    try:
        imu = IMU()
        await imu.run(rate)
    except Exception as e:
        print(f"***** IMU task: {e}")
    

try:
    from xiao_s3 import IMU_SDA, IMU_SCL
except ImportError:
    print("IMU not available")
    
    async def main(rate):
        pass