# SPDX-FileCopyrightText: 2021 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""I2C Class for Generic MicroPython"""

import machine


class I2C:
    """I2C Class for Generic MicroPython"""

    MASTER = 0

    def __init__(self, port, scl, sda, freq=100000):
        self._i2c = machine.I2C(port, scl=machine.Pin(scl), sda=machine.Pin(sda), freq=freq)

    def scan(self):
        """Perform an I2C Device Scan"""
        return self._i2c.scan()

    def writeto(self, address, buffer, *, stop=True):
        """Write the data from the buffer to the address"""
        return self._i2c.writeto(address, buffer)

    def readfrom_into(self, address, buffer, *, stop=True):
        """Read data from an address and into the buffer"""
        return self._i2c.readfrom_into(address, buffer)

    def writeto_then_readfrom(
        self,
        address,
        buffer_out,
        buffer_in,
        *,
        out_start=0,
        out_end=None,
        in_start=0,
        in_end=None,
        stop=False,
    ):
        """Write data from buffer_out to an address and then
        read data from an address and into buffer_in
        """
        self._i2c.writeto_then_readfrom(
            address,
            buffer_out,
            buffer_in,
            out_start=out_start,
            out_end=out_end,
            in_start=in_start,
            in_end=in_end,
        )

    # pylint: enable=unused-argument
