import aiohttp
import asyncio
import json
from subscription import *
from proc_utils import *


class Pix:
    """docstring for Pix."""

    _headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'}

    async def start(self):
        self.process = None
        while not self.process:
            self.process = find_LCU_process()
            print("couldn't find LCUx process")
            asyncio.sleep(0.5)

        print("found LCUx process\n", self.process)

        process_args = parse_cmdline_args(self.process.cmdline())

        # self._lcu_pid = self.process.pid
        # self._pid = int(process_args['app-pid'])
        self._port = int(process_args['app-port'])
        self._auth_key = process_args['remoting-auth-token']

        self.https_session = aiohttp.ClientSession(auth=aiohttp.BasicAuth('riot', self._auth_key), headers=self._headers)

        while True:
            try:
                resp = await self.request('get', '/riotclient/ux-state')
                print("connected to LCUx server\n", resp)
                break
            except aiohttp.client_exceptions.ClientConnectorError:
                print("can't connect to LCUx server")
                await asyncio.sleep(0.5)
                pass

        self.ws_session = aiohttp.ClientSession(auth=aiohttp.BasicAuth('riot', self._auth_key), headers=self._headers)
        self.ws_client = await self.ws_session.ws_connect(f'wss://127.0.0.1:{self._port}', ssl=False)
        self.ws_subscriptions = {}
        self.ws_loop_task = asyncio.create_task(self.begin_ws_loop())
        print("began LCUx websocket loop")
        print("connected")
        return self


    async def begin_ws_loop(self):
        self.ws_client_tasks = []

        async for msg in self.ws_client:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if not msg.data:
                    print('msg contains no data. continuing...')
                    continue
                else:
                    data = json.loads(msg.data)
                    if data[0] != Event_Code.RESPONSE.value:
                        print('message is not a response (Event_Code.RESPONSE). breaking...')
                        break

                    subscription = self.ws_subscriptions.get(data[1]) #If this raises KeyError, it oughta.
                    self.ws_client_tasks += subscription.tasks(data[2])

                    if self.ws_client_tasks:
                        done, pending = await asyncio.wait(self.ws_client_tasks, timeout=0)
                        for task in done:
                            _ = await task
                            self.ws_client_tasks.remove(task)

            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('received websocket message ERROR. breaking...')
                break
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                print('received websocket message CLOSE. breaking...')
                break

            await asyncio.gather(*self.ws_client_tasks)

        #FIXME: make SSL work ya chump
    async def request(self, method, endpoint, **kwargs):
        if kwargs.get('data', None):
            kwargs['data'] = json.dumps(kwargs['data'])

        return await self.https_session.request(method, f'https://127.0.0.1:{self._port}{endpoint}', ssl=False, **kwargs)

    async def subscribe(self, event, default_behavior=None):
        print("subscribing to: " + event)
        subscription = EventSubscription(default_behavior)
        self.ws_subscriptions[event] = subscription
        await self.ws_client.send_json([Event_Code.SUBSCRIBE.value, event])
        return subscription

    def subscriptionFilterEndpoint(self, event, endpoint, behavior):
        subscription = self.ws_subscriptions[event]
        subscription.filter_endpoint(endpoint, behavior)

    def subscriptionUnfilterEndpoint(self, event, endpoint):
        subscription = self.ws_subscriptions[event]
        subscription.unfilter_endpoint(endpoint, behavior)

    def event_from_endpoint(self, endpoint):
        pass #TODO

    async def unsubscribe(self, event):
        print("unsubscribing from: " + event)
        await self.ws_client.send_json([Event_Code.UNSUBSCRIBE.value, event])
        del self.ws_subscriptions[event]

    async def close(self):
        await self.https_session.close()
        await self.ws_client.close()
        await self.ws_session.close()
        await self.ws_loop_task
