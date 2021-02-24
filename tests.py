from Pix import Pix
from random import randint
import asyncio

async def main():
    icon_num = randint(50, 78)
    pix = await Pix.start()
    # # await pix.start()
    # resp = await pix.request('put', '/lol-summoner/v1/current-summoner/icon',
    #                         data={"profileIconId": icon_num})
    # if resp.status == 201:
    #     print('success')
    # else:
    #     print(resp)
    #

    await pix.subscribe("OnJsonApiEvent")
    await asyncio.sleep(10)
    # await pix.unsubscribe("OnJsonApiEvent")
    await pix.close()

if __name__ == '__main__':
    asyncio.run(main())



#
# await pix.request('post', '/riotclient/unload')
# unloaded_state = await pix.request('get', '/riotclient/ux-state')
# await pix.request('post', '/riotclient/ux-show')
#
# print(await unloaded_state.text())
# print(await unloaded_state.read())

# resp = await pix.request('post', '/help')
# resp_json = await resp.json()
# print(json.dumps(resp_json, indent=4, sort_keys=True))
# resp = await pix.request('post', '/subscribe', params={'eventName': 'OnJsonApiEvent'})
# resp = await pix.request('post', '/WebSocketFormat')
# resp = await pix.request('get', '/swagger/v3/openapi.json')
# print(resp)

# async def main():
#     pix = Pix()
#     await pix.start()
#
#     await pix.subscribe("OnJsonApiEvent")
#     await asyncio.sleep(10)
#     await pix.unsubscribe("OnJsonApiEvent")
#
#     await pix.close()
#     return True
#
# if __name__ == "__main__":
#     asyncio.run(main())
