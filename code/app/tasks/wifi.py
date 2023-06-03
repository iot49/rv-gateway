import uasyncio as asyncio
import network, ntptime
from uping import ping

from utilities import config
from .. import webapp
from ..state import update


_WLAN_STATUS = {
    1000: "idle",
    1001: "connecting",
    1010: "connected",
     202: "wrong password",
     201: "no reply from ap",
     200: "beacon timeout",
     203: "assoc fail",
     204: "handsake timeout"
}

_IP = None

def ip():
    return _IP

async def main(interval: float):
    # check connection every interval seconds
    print("Starting wifi task ...")
    global _IP

    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        print("\nWiFi connected @", wlan.ifconfig())

    connection_attemps = 0
    while True:
        lan = wan = False
        
        # check if wifi is enabled
        ssid = config.get("app", "wifi", "ssid")
        pwd  = config.get("app", "wifi", "pwd")

        if ssid and pwd:

            # verify connection / connect
            network.hostname(config.get('app', 'wifi', 'hostname') or 'rv-logger')
            wlan.active(True)

            # apparently robert_hh recommends this?
            await asyncio.sleep_ms(100)
            
            # Try to connect. After reboot this may take quite some time ...
            if not wlan.isconnected():
                connection_attemps += 1
                await update('wifi', 'wifi-connection-attempts', connection_attemps)
                try:
                    wlan.connect(ssid, pwd)
                except OSError as e:
                    print(f"***** wlan.connect: {e}")
                # sometimes connection is quick (?), in this case no further output required
                if not wlan.isconnected():
                    print("Waiting for WiFi connection ", end="")
                    # wait for connection: 
                    # this can take a long time - don't give up early!
                    for i in range(200):
                        if wlan.isconnected():
                            break
                        await asyncio.sleep_ms(100)
                        print(".", end="")
                print("\nWiFi connected @", wlan.ifconfig())
    
            
            # verify that internet is reachable
            _IP = router_ip = network.WLAN(network.STA_IF).ifconfig()[2]
            await update('wifi', 'ip', _IP)    # BLE connections (and successful wifi) see this
            try:
                if wlan.isconnected():
                    lan = ping(router_ip, quiet=True)[1] > 0
                # retest - for flaky GL.iNet router ???
                if wlan.isconnected():
                    wan_ip = config.get('app', 'wifi', 'wan-check')
                    wan = wan_ip != None and ping(wan_ip, quiet=True)[1] > 0
            except OSError as e:
                await webapp.info('ERROR', f"ping failed in wifi-task, wlan.is_connected={wlan.isconnected()}", e)

            # report status
            if wlan.isconnected():
                status = wlan.status()
                await update('wifi', 'wifi-status', _WLAN_STATUS.get(status, str(status)))
                await update('wifi', 'wifi-lan', lan)
                await update('wifi', 'wifi-wan', wan)

        await asyncio.sleep(interval)
  