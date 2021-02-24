# Pix
Pix is a Python3 helper for the League of Legends LCU API. Pix is asynchronous and can communicate on both HTTPS and WSS channels.

## Starting pix
Starting pix is as easy as:
```py
from pix import Pix
import asyncio

pix = await Pix.start()
```
This starts pix's http and websocket clients, and blocks until pix can connect to the league client Ux process and server

## Using HTTP methods
Pix can can make http requests to any LCU endpoint
```py
response = await pix.request('get', '/lol-summoner/v1/current-summoner')
#request can be used to execute 'get', as well as any other http method
print(await response.json())
```

## Subscribing to websocket events
Pix's websocket can subscribe to LCU events. Pix can attach a user defined `default_event_handler` to an event subscription which will be fired any time pix receives a websocket message pertaining to the event.
```py
#subscription = pix.subscribe('event', default_event_handler)
#default_event_handler is a function which accepts json formatted data as its sole argument and returns None, or a disposable value.
#attaching a specialized default event handler to the subscription
async def un_default_event_handler(data):
  print("user defined default event handler")
  print(json.dumps(data, indent=4, sort_keys=True))

my_first_subscription = await pix.subscribe('OnJsonApiEvent', un_default_event_handler)
#if you don't want to attach your own default event handler, it can be omitted
#my_first_subscription = await pix.subscribe('OnJsonApiEvent')
```
re-subscribing to an event invalidates the first subscription.
```py
old_subscription = await pix.subscribe('OnJsonApiEvent', un_default_event_handler)
new_subscription = await pix.subscribe('OnJsonApiEvent')
```
When pix receives an `'OnJsonApiEvent'`, the default_event_handler will be fired instead of the user defined `un_default_event_handler`, because pix respects `new_subscription` as the driver for the event


Pix can also attach a further kind of filter on websocket event subscriptions -- endpoint filters. An endpoint filter is a function that runs when a certain endpoint is specified by the event response. There are two kinds of endpoint filters. path filters end in '/', and run when the specified endpoint is any sub-endpoint of the path, and uri filters, which run when the endpoint is the same as the filter. You can attach endpoint filters through the subscription itself, via Pix with the subscription instance, or via Pix by event name (as there is only ever one active subscription per event at a time). endpoint handlers take the same signature as default event handlers. They must take in json formatted data and return nothing, or a disposable value. uri handlers and path handlers will both fire if they overlap.
```py
async def custom_uri_handler_1(data):
  print('current-summoner uri got triggered. This is custom_uri_handler_1')

async def custom_uri_handler_2(data):
  print('status uri got triggered. This is custom_uri_handler_2')

async def custom_path_handler(data):
  print('/lol-summoner/ path got triggered. This is custom_path_handler')
  print('full triggered uri is:', data['uri'])

#adding uri endpoint filter via subscription instance
my_first_subscription.filter_endpoint('/lol-summoner/v1/current-summoner',
                                      custom_uri_handler_1)
#adding uri endpoint filter via subscription instance through Pix
pix.subscription_filter_endpoint(my_second_subscription, '/lol-summoner/v1/status',
                                 custom_uri_handler_2)

#adding path endpoint filter via event name through Pix
pix.subscription_filter_endpoint('OnJsonApiEvent', '/lol-summoner/',
                                 custom_path_handler)
```

*Pix isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games, and all associated properties are trademarks or registered trademarks of Riot Games, Inc.*
