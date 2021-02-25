import aiohttp
import asyncio
import json
from collections import defaultdict
import logging

from .subscription import *
from .proc_utils import *

class Willump:
    _headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'}

    @staticmethod
    async def start():
        self = Willump()
        self.process = None
        while not self.process:
            self.process = find_LCU_process()
            logging.debug("couldn't find LCUx process yet. Re-searching process list...")
            await asyncio.sleep(0.5)

        logging.info("found LCUx process", self.process)

        process_args = parse_cmdline_args(self.process.cmdline())

        # self._lcu_pid = self.process.pid
        # self._pid = int(process_args['app-pid'])
        self._port = int(process_args['app-port'])
        self._auth_key = process_args['remoting-auth-token']

        self.https_session = aiohttp.ClientSession(auth=aiohttp.BasicAuth('riot', self._auth_key), headers=self._headers)

        while True:
            try:
                resp = await self.request('get', '/riotclient/ux-state')
                if resp.status == 200:
                    logging.info("connected to LCUx server", resp.status)
                else:
                    logging.warning("connected to LCUx https server, but got an invalid response for a known uri. Response status code:", resp.status)
                break
            except aiohttp.client_exceptions.ClientConnectorError:
                logging.warn("can't connect to LCUx server. Retrying...") #this might be too much log spam
                await asyncio.sleep(0.5)
                pass

        self.ws_session = aiohttp.ClientSession(auth=aiohttp.BasicAuth('riot', self._auth_key), headers=self._headers)
        self.ws_client = await self.ws_session.ws_connect(f'wss://127.0.0.1:{self._port}', ssl=False)
        self.ws_subscriptions = defaultdict(list)
        self.subscription_tasks = []
        self.ws_loop_task = asyncio.create_task(self.begin_ws_loop())
        logging.info("began LCUx websocket loop")
        logging.info("Pix is fully connected")
        return self


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

    def event_from_endpoint(self, endpoint):
        pass #TODO

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
        await self.ws_client.close()
        await self.ws_session.close()
        await self.ws_loop_task
        await asyncio.gather(*self.subscription_tasks)
