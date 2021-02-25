# Willump
Willump is a Python3 helper for the League of Legends LCU API. Willump is asynchronous and can communicate on both HTTPS and WSS channels.

## Installing Willump
Willump can be installed through pip
```
pip install willump
```
Or `pip3` if using python3 pip

## Starting Willump
Starting Willump is as easy as:
```py
from willump import Willump
import asyncio

willump = await Willump.start()
```
This starts willump's http and websocket clients, and blocks until willump can connect to the League Client Ux process and server

## Using HTTP methods
Willump can can make http requests to any LCU endpoint
```py
response = await willump.request('get', '/lol-summoner/v1/current-summoner')
#request can be used to execute 'get', as well as any other http method
print(await response.json())
```

## Subscribing to websocket events
Willump's websocket can subscribe to LCU events. Willump can attach a user defined `default_handler` to an event subscription which will be fired any time willump receives a websocket message pertaining to the event and the message is not otherwise handled. `default_handler` is a function which accepts json formatted data as its sole argument and returns None, or a disposable value.
```py
async def un_default_event_handler(data):
  print("user defined default event handler")
  print(json.dumps(data, indent=4, sort_keys=True))

my_first_subscription = await willump.subscribe('OnJsonApiEvent', default_handler=un_default_event_handler)
```

You can add subscriptions to an event by resubscribing to the same event
```py
new_subscription = await willump.subscribe('OnJsonApiEvent')
```

If you want to attach an already made subscription to another event, you can pass it to the subscription handler:
```py
same_as_new_subscription = await willump.subscribe('OnJsonApiEvent_patcher_v1_status', subscription=new_subscription)
print(same_subscription_as_new_subscription is new_subscription) #subscription is shallow copied so this should print true
```

You can get the attached subscriptions to an event:
```py
all_subscriptions = willump.get_subscriptions('OnJsonApiEvent')
```

Willump can also unsubscribe from events to stop listening for them entirely, or can remove a subscription from an event:
```py
await willump.unsubscribe('OnJsonApiEvent', my_first_subscription) #new_subscription is still active
await willump.unsubscribe('OnJsonApiEvent') #This removes new_subscription, as well as any other subscriptions on 'OnJsonApiEvent'
```

## Attaching endpoint filters to event subscriptions
Willump's subscriptions contain two further kinds of filters on websocket events -- uri filters and path filters. These are collectively known as endpoint filters. An endpoint filter is a function that runs when a certain endpoint is specified by the event response. A subscription can have multiple endpoint handlers attached to it. Path filters end in '/', and run when the specified endpoint is any sub-endpoint of the path. Uri filters run when the endpoint is the same as the filter's uri. You can attach endpoint filters through the subscription itself, or via Willump with the subscription instance. Endpoint handlers take the same signature as `default_handler`. They must take in json formatted data and return None, or a disposable value. Uri handlers and path handlers will both fire if they overlap. If an endpoint filter is fired, the subscription's `default_handler` will not fire. Attaching two endpoint handlers to the same endpoint will overwrite the pre-existing endpoint handler.

```py
async def custom_uri_handler(data):
  print('current-summoner uri got triggered. This is custom_uri_handler')

async def custom_path_handler(data):
  print('/lol-summoner/ path got triggered. This is custom_path_handler')
  print('full triggered uri is:', data['uri'])

#adding uri endpoint filter via subscription instance
my_first_subscription.filter_endpoint('/lol-summoner/v1/current-summoner',
                                      custom_uri_handler)

#adding path endpoint filter via subscription instance through Willump
willump.subscription_filter_endpoint(my_first_subscription, '/lol-summoner/',
                                 custom_path_handler)

#unfiltering endpoints
willump.subscription_unfilter_endpoint(my_first_subscription, '/lol-summoner/')
my_first_subscription.unfilter_endpoint('/lol-summoner/v1/current-summoner')
```

## Closing willump
Closing willump attempts to close the http and ws connections, gather outstanding subscription tasks, and gracefully exit.
```py
await willump.close()
```

*Willump isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games, and all associated properties are trademarks or registered trademarks of Riot Games, Inc.*
