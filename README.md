# Pix
Pix is a Python3 helper for the League of Legends LCU API. Pix is asynchronous and can communicate on both HTTPS and WSS channels.

## How to use Pix in your project
```py
import asyncio            #import asyncio to support async event loops, a pre-requisite for pix usage
from pix import Pix       #import pix into your project

async def main():
  pix = await Pix.start() #start the pix service.
                          #this starts both a HTTPS and WS client, though they are mostly inactive
  
  response = await pix.request('get', '/lol-summoner/v1/current-summoner')
                          #request can be used to execute 'get', as well as any other http method
                          
  print(await response.json())
                          #view the response


                          #subscribing to a websocket event
  my_first_subscription = await pix.subscribe('OnJsonApiEvent')
  
  my_second_subscription = await pix.subscribe('OnJsonApiEvent', un_default_event_handler)
                          #you can set your own default handler for the event subscription
                          #re-subscribing to an event overrides the initial subscription with the new one
  
                          #there are three ways to add endpoint handlers to subscriptions
  my_second_subscription.filter_endpoint('/lol-summoner/v1/current-summoner', 
                                        custom_endpoint_handler_current_summoner)
                          #as a member of the suscription
                          
  pix.subscription_filter_endpoint(my_second_subscription, '/lol-summoner/v1/current-summoner', 
                                   custom_endpoint_handler_current_summoner)
                          #by giving pix the subscription to modify
                          
  pix.subscription_filter_endpoint('OnJsonApiEvent', '/lol-summoner/v1/current-summoner', 
                                   custom_endpoint_handler_current_summoner)
                          #by giving pix the event name of the subscription to modify
                          #this method always uses the currently bound subscription for the event.
  
async def un_default_event_handler(data):
  print("user defined default event handler")
  print(json.dumps(data, indent=4, sort_keys=True))
  
  
async def custom_endpoint_handler_current_summoner(data):
  print("user defined subscription behavior when the endpoint current-summoner is triggered")
  print(json.dumps(data, indent=4, sort_keys=True))


if __name__ == '__main__':
  asyncio.run(main())
```

*Pix isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games, and all associated properties are trademarks or registered trademarks of Riot Games, Inc.*
