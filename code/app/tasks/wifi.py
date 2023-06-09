import uasyncio as asyncio
import network
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


def ip():
    return network.WLAN(network.STA_IF).ifconfig()[0]


async def main(interval: float):
    # check connection every interval seconds
    print("Starting wifi task ...")

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

                # verify that ssid is up
                for _ in range(3):
                    net = [ x for x in wlan.scan() if x[0] == ssid.encode() ]
                    if len(net) > 0:
                        net = net[0]
                        print(f"Found ssid '{ssid}' on channel {net[2]} with RSSI {net[3]} dBm")
                        break
                    else:
                        print(f"WARNING: ssid '{ssid}' not found. Deactivating and re-activating wlan.")
                        wlan.active(False)
                        await asyncio.sleep_ms(500)
                        wlan.active(True)

                # connect
                try:
                    wlan.connect(ssid, pwd)
                except OSError as e:
                    print(f"***** wlan.connect: {e}")
                # sometimes connection is quick (?), in this case no further output required
                if not wlan.isconnected():
                    print("Waiting for WiFi connection ", end="")
                    # wait for connection: 
                    # this can take a long time - don't give up early!
                    for i in range(1000):
                        if wlan.isconnected():
                            break
                        await asyncio.sleep_ms(100)
                        print(".", end="")
                print()
                if wlan.isconnected():
                    print(f"WiFi connected @", wlan.ifconfig())
    
            
            # verify that internet is reachable
            ip, _,  router_ip, __ = network.WLAN(network.STA_IF).ifconfig()
            await update('wifi', 'ip', ip)    # BLE connections (and successful wifi) see this
            try:
                quiet_ping = True
                if wlan.isconnected():
                    lan = ping(router_ip, quiet=quiet_ping)[1] > 0
                # retest - for flaky GL.iNet router ???
                if wlan.isconnected():
                    wan_ip = config.get('app', 'wifi', 'wan-check')
                    wan = wan_ip != None and ping(wan_ip, quiet=quiet_ping)[1] > 0
            except OSError as e:
                await webapp.info('ERROR', f"ping failed in wifi-task, wlan.is_connected={wlan.isconnected()}", e)

            # report status
            status = wlan.status()
            await update('wifi', 'wifi-status', _WLAN_STATUS.get(status, str(status)))
            await update('wifi', 'wifi-lan', lan)
            await update('wifi', 'wifi-wan', wan)

        await asyncio.sleep(interval)
  