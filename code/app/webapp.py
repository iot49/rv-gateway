import uasyncio as asyncio
import json, sys
from micropython import const

from utilities import config, format_error
from . import state


FATAL = const("FATAL")
ERROR = const("ERROR")
WARNING = const("WARNING")
INFO = const("INFO")
DEBUG = const("DEBUG")

_REPORT_TRANSACTIONS = True


class _Handlers:
    """Handle for web requests. The method name is the message tag."""

    def __init__(self, send):
        self.send = send

    async def config_get(self, path=[]):
        await self.send({ 'tag': 'config_put', 'value': config.get(*path), 'path': path })

    async def config_put(self, value, path=[]):
        try:
            config.set(*path, value)
        except Exception as e:
            print(f"***** config_put", e)

    async def state_get_all(self):
        await state.send_current_state(self)

    async def history_get(self, eid):
        try:
            data = state.get(eid).history
            await self.send({ 'tag': 'history_put', 'eid': eid, 'data': data })
        except:
            await self.info(WARNING, f"No history for {eid}")       

    async def test_get(self):
        await self.info(INFO,  "test A message from app.main!")
        await self.info(ERROR, "testing webapp.info with ValueError", ValueError("what value?"))
        await self.info(ERROR, "testing webapp.info")
        await self.discovered({ "test discovered a device": { "name": "bogus", "key": "some key" } })

    async def test_all(self):
        from . import testing
        return testing.run_all()

    async def close(self):
        print("connection closed")

    async def ping(self):
        await self.send({ "tag": "pong" })

    async def pong(self):
        pass


class _Channel:

    # list of current connections
    _channels = []

    def __init__(self, channel):
        self._handlers = _Handlers(self.send)
        self._channel = channel
        self._lock = asyncio.Lock()
        self._discovered = set()

    async def _run(self):
        try:
            self._channels.append(self)
            print(f"+  {len(self._channels)} CHANNELS OPEN ({self._channel})")
            await asyncio.gather(self._receiver_task())
        except asyncio.TimeoutError:
            print("catch TimeoutError - let finally close channel")
        finally:
            self._channels.remove(self)
            print(f"-  {len(self._channels)} CHANNELS OPEN ({self._channel})")
        await state.update('webapp', 'gateway-connections', len(self._channels))

    async def send(self, msg):
        """Send message to this channel."""
        async with self._lock:
            try:
                if _REPORT_TRANSACTIONS: print(f"webapp.send {json.dumps(msg)}")
                await self._channel.send(json.dumps(msg))
            except OSError:
                # channel closed
                self._channel.close()

    @classmethod
    async def send_all(cls, msg):
        """Send message to all open channels."""
        # copy ... in case _channels gets modified (a channel closes)
        for c in cls._channels.copy():
            await c.send(msg)

    @classmethod
    async def discovered(cls, device):
        """Notify of newly discovered entity

        Example:
            discoved({
                "a4:c1:38:26:8c:84": {
                    "name": "MQTT",
                    "key": "8aasff8edcacd31dsf46efa7"
                }
            })
        """
        assert device and isinstance(device, dict)
        did = next(iter(device))
        for ch in cls._channels:
            if did in ch._discovered: return
            ch._discovered.add(did)
            print({ 'tag': 'discovered', 'device': device })
            await ch.send({ 'tag': 'discovered', 'device': device })

    async def info(self, category, msg, exception=None):
        """Send information"""
        msg = { 'tag': 'info', 'category': category, 'msg': format_error(msg, exception) }
        await self.send(msg)

    async def _receiver_task(self):
        channel = self._channel
        ping_interval = float(config.get('app', 'ping-interval') or 15)
        while not channel.closed:
            try:
                msg = await asyncio.wait_for(channel.receive(), timeout=max(5*ping_interval, 60))
                msg = json.loads(msg).get("data", {})
                if _REPORT_TRANSACTIONS: print(f"RECEIVER got {msg}")
            except asyncio.TimeoutError:
                # lost connection propagate error to run to close the channel
                raise
            except ValueError:
                continue
            except (OSError, asyncio.CancelledError):
                break
            except Exception as e:
                await self.info(ERROR, "Receiver: unknown error - ignored", e)
                return
            try:
                tag = msg["tag"] 
                method = getattr(self._handlers, tag)
            except KeyError:
                await self.info(ERROR, f"request has no tag attribute: {msg}")
                return
            except AttributeError:
                await self.info(ERROR, f"no handler for message {tag}: {msg}")
                return
            try:
                del msg["tag"]
                await method(**msg)
            except Exception as e:
                await self.info(ERROR, f"Receiver: {msg}", e)


async def send_all(msg):
    """Send message to all presently connected channels"""
    await _Channel.send_all(msg)

async def info(category, msg, exception=None):
    """Send message to all channels"""
    msg = { 'tag': 'error', 'category': category, 'msg': format_error(msg, exception) }
    await _Channel.send_all(msg)
    # print(f"webapp.info: {msg}")

async def discovered(device):
    """New device discovered"""
    await _Channel.discovered(device)


async def serve(channel):
    """Serve content to a single channel.
    :param channel: object with coroutines `send` and `receive`.
    """
    ch = _Channel(channel)
    await ch._run()
