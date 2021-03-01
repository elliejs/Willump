from willump import Willump
from random import randint
import asyncio
import json

async def un_default_event_handler(data):
  print("user defined default event handler")
  print(json.dumps(data, indent=4, sort_keys=True))

async def main():
    # icon_num = randint(50, 78)
    wllp = await Willump.start()
    # # await willump.start()
    # resp = await wllp.request('put', '/lol-summoner/v1/current-summoner/icon',
    #                         data={"profileIconId": icon_num})
    # if resp.status == 201:
    #     print('success')
    # else:
    #     print(resp)
    #

    sub = await wllp.subscribe("OnJsonApiEvent", default_handler=un_default_event_handler)
    sub.filter_endpoint('/endpoiint')
    sub2 = await wllp.subscribe("OnJsonApiEvent_patcher_v1_status", subscription=sub)
    sub2.filter_endpoint('/endpoiiiiiint')

    # print(willump.ws_subscriptions)

    for k, s in wllp.ws_subscriptions.items():
        print(k)
        for _s in s:
            print(_s._registered_uris)

    await wllp.close()

if __name__ == '__main__':
    asyncio.run(main())



#
# await willump.request('post', '/riotclient/unload')
# unloaded_state = await willump.request('get', '/riotclient/ux-state')
# await willump.request('post', '/riotclient/ux-show')
#
# print(await unloaded_state.text())
# print(await unloaded_state.read())

# resp = await willump.request('post', '/help')
# resp_json = await resp.json()
# print(json.dumps(resp_json, indent=4, sort_keys=True))
# resp = await willump.request('post', '/subscribe', params={'eventName': 'OnJsonApiEvent'})
# resp = await willump.request('post', '/WebSocketFormat')
# resp = await willump.request('get', '/swagger/v3/openapi.json')
# print(resp)

# async def main():
#     willump = Pix()
#     await willump.start()
#
#     await willump.subscribe("OnJsonApiEvent")
#     await asyncio.sleep(10)
#     await willump.unsubscribe("OnJsonApiEvent")
#
#     await willump.close()
#     return True
#
# if __name__ == "__main__":
#     asyncio.run(main())
