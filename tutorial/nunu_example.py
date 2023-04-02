#this project works with willump>=1.2.0
import willump

import asyncio
import logging

async def main():
    global wllp
    wllp = await willump.start(with_nunu=True, Allow_Origin="https://eleanor.sh")

    while True:
        await asyncio.sleep(100)

if __name__ == '__main__':
    # uncomment this line if you want to see nunu complain (debug log)
    # logging.getLogger().setLevel(level=logging.DEBUG)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
       asyncio.run(wllp.close())
