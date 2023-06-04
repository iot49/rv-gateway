import uasyncio as asyncio
import os, json
from json import dumps, loads
from microdot_asyncio import Microdot
from microdot_asyncio_websocket import with_websocket

from utilities import config
from .. import webapp
    

app = Microdot()

# rest api: https://apiguide.readthedocs.io/en/latest/index.html

@app.get('/')
async def hello(request):
    return "RV app"

@app.get('config')
async def get_config(request):
    """Config as json"""
    return config.get()

@app.get('state_get_all')
async def state_get_all(request):
    from io import StringIO
    from ..state import get_current_state

    s = StringIO()
    de = 'device name: entity name'
    s.write(f"{'eid':30} {de:40} {'type':8} {'value':24} {'unit':6} {'icon':12} {'filter':12}\n\n")

    for eid, ev in get_current_state().items():
        cfg = config.get_entity_config(eid)
        name = f"{cfg.get('device_name')}: {cfg.get('name')}"
        icon = cfg.get('icon')
        unit = cfg.get('unit')
        filter = cfg.get('filter', [])
        value = ev.value
        type_ = type(value).__name__
        if isinstance(value, float):  value = f"{value:<20.5}"
        s.write(f"{eid:30} {name:40} {type_:8} {str(value):24} {unit:6} {icon:12} {filter}\n")
    return s.getvalue()

@app.get('test')
async def test(request):
    from .. import testing
    return testing.run_all()

@app.get('ping')
async def test(request):
    return "pong"

@app.get('/ws')
@with_websocket
async def websocket(request, ws):
    await webapp.serve(ws)


async def main(host='0.0.0.0', port=80, debug=False):
    await app.start_server(host=host, port=port, debug=debug)

