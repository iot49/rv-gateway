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

