from willump.willump import Willump

import asyncio
import json
import socket

from aiohttp import web

import logging
import ssl



async def router(request):
    print("\n\n" + str(request.method) + str(request.rel_url) + "\n\n")
    data=None
    if request.can_read_body:
        data = await request.json()
        resp = await wllp.request(request.method, request.rel_url, data=data)
        resp_json = await resp.json()
        return web.json_response(resp_json, headers = {'Access-Control-Allow-Origin': 'https://zork.pw'})
    else:
        return web.Response(headers = {'Access-Control-Allow-Origin': 'https://zork.pw'})

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

async def main():
    global wllp
    wllp = await (await Willump.start()).nunu(Allow_Origin='*', ssh_key_path='/home/ellie/willump/tests/server.pem')

    # print(wllp._port + " " + wllp._auth_key)
    #
    # app = web.Application()
    # app.add_routes([web.route('*', '/{tail:.*}', router)])#web.get('/{tail:.*}', router)])
    #
    # ip = get_ip()
    # port = '6969'
    # ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
    # ssl_context.load_cert_chain('/home/ellie/willump/tests/server.pem')
    # await web._run_app(app, host=ip, port=port, ssl_context=ssl_context)#, host='192.168.0.10')
    # await wllp.close()

    # web.run_app(app)


    # await wllp.close()
    while True:
        await asyncio.sleep(100)
if __name__ == '__main__':
    logging.basicConfig(level=logging.NOTSET)

    # asyncio.run(main())
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
       loop.run_until_complete(wllp.close())
       print()
    # main()


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

# # # await willump.start()
# # resp = await wllp.request('put', '/lol-summoner/v1/current-summoner/icon',
# #                         data={"profileIconId": icon_num})
# # if resp.status == 201:
# #     print('success')
# # else:
# #     print(resp)
# #
#
# sub = await wllp.subscribe("OnJsonApiEvent", default_handler=un_default_event_handler)
# sub.filter_endpoint('/endpoiint')
# sub2 = await wllp.subscribe("OnJsonApiEvent_patcher_v1_status", subscription=sub)
# sub2.filter_endpoint('/endpoiiiiiint')
#
# # print(willump.ws_subscriptions)
#
# for k, s in wllp.ws_subscriptions.items():
#     print(k)
#     for _s in s:
#         print(_s._registered_uris)
