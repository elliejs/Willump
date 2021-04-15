#for cutting edge github import
from willump.willump import Willump

#this works with willump>=1.2.0
#import willump

import asyncio

async def main():
    global wllp
    wllp = await (await Willump.start()).nunu(Allow_Origin='https://your.origin.here.com', ssh_key_path='/path/to/server.pem')

    while True:
        await asyncio.sleep(100)

if __name__ == '__main__':
    logging.basicConfig(level=logging.NOTSET)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
       loop.run_until_complete(wllp.close())
       print()
