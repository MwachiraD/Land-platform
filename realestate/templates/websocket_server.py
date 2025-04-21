import asyncio
import websockets

async def echo(websocket, path):
    async for message in websocket:
        await websocket.send(message)  # Echo the received message

start_server = websockets.serve(echo, "127.0.0.1", 8765)  # Local WebSocket server

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
