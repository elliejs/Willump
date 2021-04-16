import aiohttp
from aiohttp import web
import asyncio
import json
from collections import defaultdict
import logging
import ssl
import socket

from .subscription import Event_Code, EventSubscription
from .proc_utils import parse_cmdline_args, find_LCU_process

class Willump:
    _headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'}

    @staticmethod
    async def start(start_nunu=False, start_websocket=True, **kwargs):
        self = Willump()
        self.nunu_alive = False
        self.websocket_alive = False

        nunu_loading = None
        if start_nunu:
            nunu_loading = asyncio.create_task(self.start_nunu(Allow_Origin = kwargs['Allow_Origin'], ssl_key_path = kwargs['ssl_key_path'], port=kwargs.get('port', None), host=kwargs.get('host', None)))

        self.process = None
        while not self.process:
            self.process = find_LCU_process()
            logging.warn("couldn't find LCUx process yet. Re-searching process list...")
            await asyncio.sleep(0.5)

        logging.info("found LCUx process", str(self.process))

        process_args = parse_cmdline_args(self.process.cmdline())

        self._port = int(process_args['app-port'])
        self._auth_key = process_args['remoting-auth-token']

        self.https_session = aiohttp.ClientSession(auth=aiohttp.BasicAuth('riot', self._auth_key), headers=self._headers)

        while True:
            try:
                resp = await self.request('get', '/riotclient/ux-state')
                if resp.status == 200:
                    logging.info("connected to LCUx server", str(resp.status))
                else:
                    logging.warning("connected to LCUx https server, but got an invalid response for a known uri. Response status code:", str(resp.status))
                break
            except aiohttp.client_exceptions.ClientConnectorError:
                logging.warn("can't connect to LCUx server. Retrying...") #this might be too much log spam
                await asyncio.sleep(0.5)
                pass

        if start_websocket:
            await self.start_websocket()

        if nunu_loading:
            await nunu_loading

        logging.info("Willump is fully connected")
        return self

    async def start_websocket(self):
        async def begin_ws_loop(self):
            async for msg in self.ws_client:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    if not msg.data:
                        logging.info('got websocket message containing no data, probably just server confirming subscription success')
                    else:
                        data = json.loads(msg.data)

                        subscriptions = self.ws_subscriptions[data[1]]
                        for subscription in subscriptions:
                            self.subscription_tasks += subscription.tasks(data[2])

                        if self.subscription_tasks:
                            done, pending = await asyncio.wait(self.subscription_tasks, timeout=0)
                            for task in done:
                                _ = await task
                                self.subscription_tasks.remove(task)

                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logging.warning('received websocket message ERROR, ending listening loop')
                    break
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    logging.info('received websocket message CLOSE, ending listening loop')
                    break

        self.ws_session = aiohttp.ClientSession(auth=aiohttp.BasicAuth('riot', self._auth_key), headers=self._headers)
        self.ws_client = await self.ws_session.ws_connect(f'wss://127.0.0.1:{self._port}', ssl=False)
        self.ws_subscriptions = defaultdict(list)
        self.subscription_tasks = []
        self.ws_loop_task = asyncio.create_task(begin_ws_loop(self))
        self.start_websocket = True
        logging.info("began LCUx websocket loop")

    async def start_nunu(self, Allow_Origin, ssl_key_path, port=None, host=None):
        _nunu_headers = {
            'Access-Control-Allow-Origin': Allow_Origin,
            'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }

        def get_ip():
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(('10.255.255.255', 1))
                IP = s.getsockname()[0]
            except Exception:
                IP = '127.0.0.1'
            finally:
                s.close()
            return IP

        async def router(req):
            logging.info(str(req.method) + str(req.rel_url))
            if req.method == 'OPTIONS':
                return web.Response(headers = _nunu_headers)

            data = await req.json() if req.can_read_body else None

            resp = await self.request(req.method, req.rel_url, data=data)
            resp_json = await resp.json()
            return web.json_response(resp_json, headers = _nunu_headers)

        self.nunu_app = web.Application()
        self.nunu_app.add_routes([web.route('*', '/{tail:.*}', router)])

        ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(ssl_key_path)

        self.nunu_task = asyncio.create_task(web._run_app(self.nunu_app, host=host or get_ip(), port=port or 8989, ssl_context=ssl_context))

        self.nunu_alive = True
        return self

        #FIXME: make SSL work ya chump
    async def request(self, method, endpoint, **kwargs):
        if kwargs.get('data', None):
            kwargs['data'] = json.dumps(kwargs['data'])

        return await self.https_session.request(method, f'https://127.0.0.1:{self._port}{endpoint}', ssl=False, **kwargs)

    async def subscribe(self, event, default_handler=None, subscription=None):
        if default_handler and subscription:
            logging.warn("passed in pre-existing subscription and a default handler for a new subscription. default_handler will be ignored in favour of the existing subscription")

        if not self.ws_subscriptions[event]:
            await self.ws_client.send_json([Event_Code.SUBSCRIBE.value, event])

        if not subscription:
            subscription = EventSubscription(default_handler)

        self.ws_subscriptions[event].append(subscription)
        return subscription

    def get_subscriptions(self, event):
        return self.ws_subscriptions[event]

    def subscription_filter_endpoint(self, subscription, endpoint, handler):
        subscription.filter_endpoint(endpoint, handler)

    def subscription_unfilter_endpoint(self, subscription, endpoint):
        subscription.unfilter_endpoint(endpoint)

    # def event_from_endpoint(self, endpoint):
    #     pass #TODO

    async def unsubscribe(self, event, subscription=None):
        if not subscription:
            await self.ws_client.send_json([Event_Code.UNSUBSCRIBE.value, event])
            del self.ws_subscriptions[event]
        else:
            self.ws_subscriptions[event].remove(subscription)
            if not self.ws_subscriptions:
                await self.ws_client.send_json([Event_Code.UNSUBSCRIBE.value, event])

    async def close(self):
        await self.https_session.close()
        if self.websocket_alive:
            await self.close_websocket()
        if self.nunu_alive:
            await self.close_nunu()

    async def close_websocket(self):
        await self.ws_client.close()
        await self.ws_session.close()
        await self.ws_loop_task
        await asyncio.gather(*self.subscription_tasks)
        self.websocket_alive = False

    async def close_nunu(self):
        await self.nunu_app.shutdown()
        await self.nunu_app.cleanup()
        await self.nunu_task
        self.nunu_alive = False
