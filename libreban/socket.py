from libreban.app import *
from libreban.misc import *
from libreban.model import *
from sanic.websocket import ConnectionClosed

from asyncio import sleep
from collections import defaultdict

connections = defaultdict(set)

async def dispatch(id, msg):
    for conn in connections[id].copy():
        try:
            await conn.send(msg)
        except ConnectionClosed:
            connections[id].remove(ws)

@app.websocket('/board/<id:int>/updates')
async def board_updates(request, ws, id):
    connections[id].add(ws)
    while ws.open:
        try:
            await ws.recv()
        except ConnectionClosed:
            connections[id].remove(ws)
