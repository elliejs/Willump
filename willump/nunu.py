import asyncio
from aiohttp import web
import socket
import ssl

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
        return IP

class Nunu:
    def __init__(self, wllp, Allow_Origin, ssl_key_path, port=None, host=None):
        self._headers = {
            'Access-Control-Allow-Origin': Allow_Origin,
            'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }

        self.wllp = wllp
        self.web_app = web.Application()
        self.web_app.add_routes([web.get('/ws', self.websocket_handler), web.route('*', '/{tail:.*}', self.router)])

        ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(ssl_key_path)

        self.app_task = asyncio.create_task(web._run_app(self.web_app, host=host or get_local_ip(), port=port or 8989, ssl_context=ssl_context))

    # TODO: Make server return refused when Nunu is up but LCU isn't.
    async def router(self, req):
        logging.info(str(req.method) + str(req.rel_url))

        if req.method == 'OPTIONS':
            return web.Response(headers = _headers)
        #if not self.wllp.willump_alive:
        #   return 500 yeet
        data = await req.json() if req.can_read_body else None
        resp = await self.wllp.request(req.method, req.rel_url, data=data)
        return web.json_response(await resp.json(), headers = _headers)

    async def websocket_handler(self, request):

        ws = web.WebSocketResponse()
        await ws.prepare(request)

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    #wllp stuff here prolly
                    await ws.send_str(msg.data + '/answer')
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('ws connection closed with exception %s' %
                      ws.exception())

        print('websocket connection closed')

        return ws

    async def close(self):
        await self.web_app.shutdown()
        await self.web_app.cleanup()
        await self.app_task
