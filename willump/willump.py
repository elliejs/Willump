import aiohttp
import asyncio
import json
from collections import defaultdict
import logging

from .subscription import Event_Code, EventSubscription
from .proc_utils import parse_cmdline_args, find_LCU_process
from .live_events import LiveEvents
from .nunu import Nunu

class Willump:
    _headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    @staticmethod
    async def start(with_nunu=False, with_websocket=True, **kwargs):
        self = Willump()
        self.rest_alive = False
        self.nunu_alive = False
        self.websocket_alive = False
        self.live_events_alive = False

        lcu_process = None
        while not lcu_process:
            lcu_process = find_LCU_process()
            logging.warn("couldn't find LCUx process yet. Re-searching process list...")
            await asyncio.sleep(0.5)

        logging.info("found LCUx process " + lcu_process.name())
        process_args = parse_cmdline_args(lcu_process.cmdline())
        self._port = int(process_args['app-port'])
        self._auth_key = process_args['remoting-auth-token']

        self.start_rest()

        while True:
            try:
                resp = await self.request('get', '/riotclient/ux-state')
                if resp.status == 200:
                    logging.info("connected to LCUx server, status: " + str(resp.status))
                else:
                    logging.warning("connected to LCUx https server, but got an invalid response for a known uri. Response status code: " + str(resp.status))
                break
            except aiohttp.client_exceptions.ClientConnectorError:
                logging.warn("can't connect to LCUx server. Retrying...") #this might be too much log spam
                await asyncio.sleep(0.5)

        if with_websocket:
            await self.start_websocket()

        if with_nunu:
            #is this Allow_Origin ethical......
            self.start_nunu(Allow_Origin = kwargs.get('Allow_Origin', '*'), sslCert = kwargs.get('sslCert', None), sslKey = kwargs.get('sslKey', None), forceNew = kwargs.get('forceNew', False),  port=kwargs.get('port', 8989), host=kwargs.get('host', None))

        logging.info("Willump is fully connected")
        return self

    def start_rest(self):
        if self.rest_alive:
            logging.warn('rest is already started. dropping out. rest will continue running')
            return self

        self.https_session = aiohttp.ClientSession(auth=aiohttp.BasicAuth('riot', self._auth_key), headers=self._headers)
        self.rest_alive = True
        return self

    async def start_websocket(self):
        if self.websocket_alive:
            logging.warn('websocket is already started. dropping out. websocket will continue running')
            return self
        # TODO: catch exceptions that I'm sure fall out of these IO calls
        self.ws_session = aiohttp.ClientSession(auth=aiohttp.BasicAuth('riot', self._auth_key), headers=self._headers)
        self.ws_client = await self.ws_session.ws_connect(f'wss://127.0.0.1:{self._port}', ssl=False)

        self.ws_subscriptions = defaultdict(list)
        self.subscription_tasks = []

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

        self.ws_loop_task = asyncio.create_task(begin_ws_loop(self))
        self.websocket_alive = True
        logging.info("began LCUx websocket loop")

    def start_nunu(self, Allow_Origin='*', sslCert=None, sslKey=None, forceNew=False, port=8989, host=None):
        if self.nunu_alive:
            logging.warn('nunu is already started. dropping out. Nunu will continue running')
            return self

        self.nunu = Nunu(self, Allow_Origin, sslCert, sslKey, forceNew, port, host)
        self.nunu_alive = True

    async def start_live_events(self, port=None, default_behavior=None, retry_policy=False):
            if self.live_events_alive:
                logging.warn('live events is already started. dropping out. live events will continue running')
                return self

            self.live_events = await LiveEvents.start(port, default_behavior)
            if not self.live_events and not retry_policy:
                logging.warn("can't connect to live event server")
                return self

            while not self.live_events:
                await asyncio.sleep(0.5)
                logging.warn("retrying connection to live event server")
                self.live_events = await LiveEvents.start(port, default_behavior)

            self.live_events_alive = True
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

    async def unsubscribe(self, event, subscription=None):
        if not subscription:
            await self.ws_client.send_json([Event_Code.UNSUBSCRIBE.value, event])
            del self.ws_subscriptions[event]
        else:
            self.ws_subscriptions[event].remove(subscription)
            if not self.ws_subscriptions:
                await self.ws_client.send_json([Event_Code.UNSUBSCRIBE.value, event])

    async def close(self):
        if self.rest_alive:
            await self.close_rest()
        if self.websocket_alive:
            await self.close_websocket()
        if self.nunu_alive:
            await self.close_nunu()
        if self.live_events_alive:
            await self.close_live_events()

    async def close_rest(self):
        await self.https_session.close()
        self.rest_alive = False

    async def close_websocket(self):
        await self.ws_client.close()
        await self.ws_session.close()
        await self.ws_loop_task
        await asyncio.gather(*self.subscription_tasks)
        self.websocket_alive = False

    async def close_nunu(self):
        await self.nunu.close()
        self.nunu_alive = False

    async def close_live_events(self):
        await self.live_events.close()
        self.live_events_alive = False
