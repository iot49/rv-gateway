import uasyncio as asyncio
from machine import Pin

try:
    from xiao_s3 import LED

    print("MCU: Xiao S3")
    async def main(half_period_ms):
        led = Pin(LED, mode=Pin.OUT)
        while True:
            led.value(1)
            await asyncio.sleep_ms(half_period_ms)
            led.value(0)
            await asyncio.sleep_ms(half_period_ms)


except ImportError:

    from pros3 import RGB_DATA, LDO2
    from neopixel import NeoPixel

    print("MCU: TinyMaker S3")

    RED   = 0
    GREEN = 1
    BLUE  = 2

    _Color = (0, 5, 0)

    def set_color(color, brightness=5):
        global RED, _Color
        if color < 0 or color > 2:
            color = RED
        _Color = [0]*3
        _Color[color] = brightness
        _Color = tuple(_Color)

    set_color(GREEN, 5)

    async def main(half_period_ms):
        global _Color
        
        # enable power
        # ldo2 = Pin(LDO2, Pin.OUT)
        # ldo2.value(1)

        # configure neopixel
        np = NeoPixel(Pin(RGB_DATA, Pin.OUT), 1)
        
        while True:
            np[0] = _Color
            np.write()
            await asyncio.sleep_ms(half_period_ms)
            np[0] = (0, 0, 0)
            np.write()
            await asyncio.sleep_ms(half_period_ms)
