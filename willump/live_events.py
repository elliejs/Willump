import asyncio
import logging

class LiveEvents:
    _port = 34243

    @staticmethod
    async def start(port=None, default_behavior=None):
        self = LiveEvents()
        self._port = port or self._port
        self._default_behavior = default_behavior or self._default_behavior

        try:
            self.reader, self.writer = await asyncio.open_connection('127.0.0.1', self._port)
        except Exception as e:
            logging.warning(e)
            return None

        self.listening_task = asyncio.create_task(self.listening_loop())
        return self

    async def _default_behavior(self, data):
        dump = data.decode()
        print('Received: ' + dump)

    async def listening_loop(self):
        while True:
            print('ready to read')
            data = await self.reader.readline()
            print(data)
            print('read')
            self._default_behavior(data)
            if not data:
                print('breaking')
                break

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()
        await self.listening_task


#HOW TO USE:
# in a separate file:
#from live_events import LiveEvents
#le = await LiveEvents.start()
#and this starts dumping incoming packets until you do:
#le.close()
