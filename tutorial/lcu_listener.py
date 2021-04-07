################################################################################################
# Willump event listener.
#
# This file shows you how to create an event listener
# to help you figure out what you need to be listening
# for in your final project.
#
# Run the program to begin listening, and use keyboard interrupt
# to end the program and stop listening.
#
# Q: What are events?
# A: Events are server side concepts. There are a many events you can subscribe to.
#    They are names for many different api updates that fall under their umbrella.
#    Use - request('get', '/help') - to get a JSON blob with a list of all possible events to subscribe to.
#    When events are triggered, they send the new data to willump.
#    Each update is of an endpoint underneath Event umbrella.
#    TL;DR
#       Events are names for groups of endpoints.
#       when an endpoint in an event changes, you get sent the new data for that endpoint.
#
# Q: How do I use events?
# A: Subscribe to an event to begin receiving its messages. The default_handler argument
#    runs every time a message is received and not otherwise handled. You don't need to
#    supply a default_handler. If you don't the automatic behavior is to log it as info.
#
# Q: How do I interact with messages coming from events?
# A: Messages come from endpoints. To catch an endpoint for special processing,
#    use subscription_filter_endpoint from willump, or filter_endpoint from the subscription.
#    these methods make the 'handler' argument run instead of the event's default handler.
#
#	REMEMBER TO MAKE EVENT HANDLER METHODS ASYNC
################################################################################################

import willump
import json
import asyncio
from functools import partial

import logging

#let's make a dummy default just to see what unfiltered messages do
async def default_message_handler(data):
	print('I got data, and it was not otherwise processed')
	#uncomment this if it's not too much data (it probably is)
	#print(json.dumps(data, indent=4, sort_keys=True))

#an event message handler takes data (which is the content of the message)
async def printing_listener(data):
	#let's just print everything we receive into this handler
	print(json.dumps(data, indent=4, sort_keys=True))


async def main():
	global wllp
	wllp = await willump.start()

	################
	#
	# Uncomment this block to print /help and see what it provides
	# resp_data = await wllp.request('get', '/help')
	# resp_json = await resp_data.json()
	# print(json.dumps(resp_json, indent=4, sort_keys=True))
	#				#use resp_json['events'] to see only the names of events
	################

	#creates a subscription to the server event OnJsonApiEvent (which is all Json updates)
	all_events_subscription = await wllp.subscribe('OnJsonApiEvent', default_handler=default_message_handler)
	#let's add an endpoint filter, and print when we get messages from this endpoint with our printing listener
	wllp.subscription_filter_endpoint(all_events_subscription, '/lol-summoner/v1/', handler=printing_listener)

	while True:
		await asyncio.sleep(10)

if __name__ == '__main__':
	# uncomment this line if you want to see willump complain (debug log)
	# logging.basicConfig(level=logging.NOTSET)
	loop = asyncio.get_event_loop()
	try:
		loop.run_until_complete(main())
	except KeyboardInterrupt:
		loop.run_until_complete(wllp.close())
		print()
