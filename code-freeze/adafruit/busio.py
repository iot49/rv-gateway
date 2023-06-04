# SPDX-FileCopyrightText: 2021 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`busio` - Bus protocol support like I2C and SPI
=================================================

See `CircuitPython:busio` in CircuitPython for more details.

* Author(s): cefn
"""

try:
    import threading
except ImportError:
    threading = None

# pylint: disable=unused-import
from adafruit_blinka import Enum, Lockable, agnostic

# pylint: disable=import-outside-toplevel,too-many-branches,too-many-statements
# pylint: disable=too-many-arguments,too-many-function-args,too-many-return-statements


class I2C(Lockable):
    """
    Busio I2C Class for CircuitPython Compatibility. Used
    for both MicroPython and Linux.
    """

    def __init__(self, port, scl, sda, frequency=100000):
        self.init(port, scl, sda, frequency)

    def init(self, port, scl, sda, frequency):
        """Initialization"""
        self.deinit()
        from adafruit_blinka.microcontroller.generic_micropython.i2c import I2C as _I2C
        self._i2c = _I2C(port, scl, sda, freq=frequency)

    def deinit(self):
        """Deinitialization"""
        try:
            del self._i2c
        except AttributeError:
            pass

    def __enter__(self):
        if threading is not None:
            self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if threading is not None:
            self._lock.release()
        self.deinit()

    def scan(self):
        """Scan for attached devices"""
        return self._i2c.scan()

    def readfrom_into(self, address, buffer, *, start=0, end=None):
        """Read from a device at specified address into a buffer"""
        if start != 0 or end is not None:
            if end is None:
                end = len(buffer)
            buffer = memoryview(buffer)[start:end]
        stop = True  # remove for efficiency later
        return self._i2c.readfrom_into(address, buffer, stop=stop)

    def writeto(self, address, buffer, *, start=0, end=None, stop=True):
        """Write to a device at specified address from a buffer"""
        if isinstance(buffer, str):
            buffer = bytes([ord(x) for x in buffer])
        if start != 0 or end is not None:
            if end is None:
                return self._i2c.writeto(address, memoryview(buffer)[start:], stop=stop)
            return self._i2c.writeto(address, memoryview(buffer)[start:end], stop=stop)
        return self._i2c.writeto(address, buffer, stop=stop)

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
        """ "Write to a device at specified address from a buffer then read
        from a device at specified address into a buffer
        """
        if out_end:
            self.writeto(address, buffer_out[out_start:out_end], stop=stop)
        else:
            self.writeto(address, buffer_out[out_start:], stop=stop)

        if not in_end:
            in_end = len(buffer_in)
        read_buffer = memoryview(buffer_in)[in_start:in_end]
        self.readfrom_into(address, read_buffer)



class SPI(Lockable):
    """
    Busio SPI Class for CircuitPython Compatibility. Used
    for both MicroPython and Linux.
    """

    def __init__(self, clock, MOSI=None, MISO=None):
        self.deinit()
        from adafruit_blinka.microcontroller.generic_micropython.spi import SPI as _SPI

        if self._locked:
            # TODO check if #init ignores MOSI=None rather than unsetting, to save _pinIds attribute
            self._spi.init(
                baudrate=baudrate,
                polarity=polarity,
                phase=phase,
                bits=bits,
                firstbit=_SPI.MSB,
            )
        else:
            raise RuntimeError("First call try_lock()")

    def deinit(self):
        """Deinitialization"""
        self._spi = None
        self._pinIds = None

    @property
    def frequency(self):
        """Return the baud rate if implemented"""
        try:
            return self._spi.frequency
        except AttributeError as error:
            raise NotImplementedError(
                "Frequency attribute not implemented for this platform"
            ) from error

    def write(self, buf, start=0, end=None):
        """Write to the SPI device"""
        return self._spi.write(buf, start, end)

    def readinto(self, buf, start=0, end=None, write_value=0):
        """Read from the SPI device into a buffer"""
        return self._spi.readinto(buf, start, end, write_value=write_value)

    def write_readinto(
        self, buffer_out, buffer_in, out_start=0, out_end=None, in_start=0, in_end=None
    ):
        """Write to the SPI device and read from the SPI device into a buffer"""
        return self._spi.write_readinto(
            buffer_out, buffer_in, out_start, out_end, in_start, in_end
        )


class UART(Lockable):
    """
    Busio UART Class for CircuitPython Compatibility. Used
    for MicroPython and a few other non-Linux boards.
    """

    class Parity(Enum):
        """Parity Enumeration"""

        pass  # pylint: disable=unnecessary-pass

    Parity.ODD = Parity()
    Parity.EVEN = Parity()

    def __init__(
        self,
        tx,
        rx,
        baudrate=9600,
        bits=8,
        parity=None,
        stop=1,
        timeout=1000,
        receiver_buffer_size=64,
        flow=None,
    ):
        from machine import UART as _UART

        from microcontroller.pin import uartPorts

        self.baudrate = baudrate

        if flow is not None:  # default 0
            raise NotImplementedError(
                "Parameter '{}' unsupported on {}".format("flow", agnostic.board_id)
            )

        # translate parity flag for Micropython
        if parity is UART.Parity.ODD:
            parity = 1
        elif parity is UART.Parity.EVEN:
            parity = 0
        elif parity is None:
            pass
        else:
            raise ValueError("Invalid parity")

        # check tx and rx have hardware support
        for portId, portTx, portRx in uartPorts:  #
            if portTx == tx and portRx == rx:
                self._uart = _UART(
                    portId,
                    baudrate,
                    bits=bits,
                    parity=parity,
                    stop=stop,
                    timeout=timeout,
                    read_buf_len=receiver_buffer_size,
                )
                break
        else:
            raise ValueError(
                "No Hardware UART on (tx,rx)={}\nValid UART ports: {}".format(
                    (tx, rx), uartPorts
                )
            )

    def deinit(self):
        """Deinitialization"""
        self._uart = None

    def read(self, nbytes=None):
        """Read from the UART"""
        return self._uart.read(nbytes)

    def readinto(self, buf, nbytes=None):
        """Read from the UART into a buffer"""
        return self._uart.readinto(buf, nbytes)

    def readline(self):
        """Read a line of characters up to a newline character from the UART"""
        return self._uart.readline()

    def write(self, buf):
        """Write to the UART from a buffer"""
        return self._uart.write(buf)
