# SPDX-FileCopyrightText: 2021 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""SPI Class for Generic MicroPython"""
from machine import SPI as _SPI

# pylint: disable=protected-access, no-self-use
class SPI:
    """SPI Class for Generic MicroPython"""

    MSB = _SPI.MSB
    LSB = _SPI.LSB

    def __init__(self, portId, baudrate=100000):
        self._frequency = baudrate
        self._spi = _SPI(portId)

    # pylint: disable=too-many-arguments,unused-argument
    def init(
        self,
        baudrate=1000000,
        polarity=0,
        phase=0,
        bits=8,
        firstbit=_SPI.MSB,
    ):
        pass
    
# SPDX-FileCopyrightText: 2021 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""SPI Class for RP2040"""
from machine import SPI as _SPI
from machine import Pin
from microcontroller.pin import spiPorts

# pylint: disable=protected-access, no-self-use
class SPI:

    MSB = _SPI.MSB

    def __init__(self, port, clock, MOSI=None, MISO=None, *, baudrate=1000000):
        self._frequency = baudrate
        _SPI(
                port,
                sck=Pin(clock),
                mosi=Pin(MOSI),
                miso=Pin(MISO),
                baudrate=baudrate,
            )

    @property
    def frequency(self):
        """Return the current frequency"""
        return self._frequency

    def write(self, buf, start=0, end=None):
        """Write data from the buffer to SPI"""
        self._spi.write(buf)

    def readinto(self, buf, start=0, end=None, write_value=0):
        """Read data from SPI and into the buffer"""
        self._spi.readinto(buf)

    # pylint: disable=too-many-arguments
    def write_readinto(
        self, buffer_out, buffer_in, out_start=0, out_end=None, in_start=0, in_end=None
    ):
        """Perform a half-duplex write from buffer_out and then
        read data into buffer_in
        """
        self._spi.write_readinto(
            buffer_out,
            buffer_in,
            out_start=out_start,
            out_end=out_end,
            in_start=in_start,
            in_end=in_end,
        )

    # pylint: enable=too-many-arguments

        """Initialize the Port"""
        self._frequency = baudrate
        self._spi.init(
            baudrate=baudrate,
            polarity=polarity,
            phase=phase,
            bits=bits,
            firstbit=firstbit,
            mode=_SPI.MASTER,
        )

    # pylint: enable=too-many-arguments

    @property
    def frequency(self):
        """Return the current frequency"""
        return self._frequency

    def write(self, buf, start=0, end=None):
        """Write data from the buffer to SPI"""
        self._spi.write(buf)

    def readinto(self, buf, start=0, end=None, write_value=0):
        """Read data from SPI and into the buffer"""
        self._spi.readinto(buf)

    # pylint: disable=too-many-arguments
    def write_readinto(
        self, buffer_out, buffer_in, out_start=0, out_end=None, in_start=0, in_end=None
    ):
        """Perform a half-duplex write from buffer_out and then
        read data into buffer_in
        """
        self._spi.write_readinto(
            buffer_out,
            buffer_in,
            out_start=out_start,
            out_end=out_end,
            in_start=in_start,
            in_end=in_end,
        )

    # pylint: enable=too-many-arguments
