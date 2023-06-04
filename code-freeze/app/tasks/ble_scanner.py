# !cp -a $IOT_PROJECTS/micropython-lib/micropython/bluetooth/aioble/aioble/ $IOT_PROJECTS/code/lib/aioble

import uasyncio as asyncio
import aioble
import re
from struct import unpack
from ucryptolib import aes

from utilities import config
from ..state import update
from ..webapp import discovered


# Victron device state codes
_VICTRON_STATE = {
    0: 'off',
    1: 'low power',
    3: 'fault',
    3: 'bulk',
    4: 'absorption',
    5: 'float'
}


async def parse_victron(data, dev, key):

    def pad(data):
        n = 16-len(data)
        return data + bytes([n])*n

    if data[0] != 0x10: return
    mac = dev.device.addr_hex().lower()
    prefix, model_id, model, iv = unpack('<HHBH', data)
    
    cipher = aes(key, 6, iv.to_bytes(16, 'little'))
    decrypted = cipher.decrypt(pad(data[8:]))

    if model == 0x1:
        # Solar charger
        state, error, v, i, y, p, ext = unpack('<BBhhHHH', decrypted)
        await update(mac, 'RSSI', dev.rssi)
        await update(mac, 'state', _VICTRON_STATE.get(state, str(state)))
        await update(mac, 'Voltage', v/100)
        await update(mac, 'Current', i/10)
        await update(mac, 'Energy', y*10.0)
        await update(mac, 'Power', p)

    elif model == 0x2:
        # Battery SOC monitor
        ttg, v, alarm, aux, i2, i0, consumed, soc = unpack('<HHHHHbHH', decrypted)
        ttg = float('inf') if ttg == 0xffff else ttg/60
        c = i0 << 16 | i2
        i = (c>>2)/1000
        T = aux/100 - 273.15 if c & 0b11 == 2 else float('nan')
        soc = ((soc & 0x3fff) >>4) / 10

        await update(mac, 'RSSI', dev.rssi)
        await update(mac, 'Time to go', ttg)
        await update(mac, 'Voltage', v/100)
        await update(mac, 'Current', c)
        await update(mac, 'Energy', consumed/10)
        await update(mac, 'SOC', soc)
        await update(mac, 'Temperature', T)


async def parse_govee(data: bytes, dev, key):
    if len(data) != 7: return
    _, temp, humi, batt = unpack('<BhHB', data)
    did = dev.device.addr_hex()
    await update(did, 'Temperature', temp/100)
    await update(did, 'Humidity', humi/100)
    await update(did, 'Battery', batt)
    await update(did, 'RSSI', dev.rssi)


_PARSER = {
    0xEC88: (parse_govee, { 'name': 'Govee' }),
    0x02E1: (parse_victron, { 'name': 'Victron', 'key': '00112233445566778899aabbccddeeff' }),
}


async def main():
    # get list of registered ble devices

    # match - microcopython does not support {} in re
    mac = re.compile(r'^[\da-f][\da-f]:[\da-f][\da-f]:[\da-f][\da-f]:[\da-f][\da-f]:[\da-f][\da-f]:[\da-f][\da-f]$')

    # registered BLE devices
    # mac address -> key or None
    registered = {}

    for did, v in config.get('devices').items():
        did = did.lower()
        if mac.match(did):
            try:
                key = bytes.fromhex(v.get('key'))
            except:
                key = None
            registered[did] = key

    # scan for ble devices
    while True:
        async with aioble.scan(duration_ms=1000, active=True) as scanner:
            async for dev in scanner:
                # print("Scan", dev)
                for manufacturer, data in dev.manufacturer():
                    parser = _PARSER.get(manufacturer)
                    if parser:
                        address = dev.device.addr_hex().lower()
                        if address in registered:
                            key = registered.get(address)
                            await parser[0](data, dev, key)
                        else:
                            await discovered({ address: parser[1] })
