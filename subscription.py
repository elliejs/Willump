from enum import Enum
import asyncio
import logging
import json

class Event_Code(Enum):
    SUBSCRIBE = 5
    UNSUBSCRIBE = 6
    RESPONSE = 8

class EventSubscription:
    async def _default_behavior(self, data):
        logging.info('EventSubscription default handler got event:')
        logging.info(json.dumps(data, indent=4, sort_keys=True))

    def __init__(self, default_behavior=None):
        self._registered_uris = {}
        self._registered_paths = {}

        if default_behavior:
            self._default_behavior = default_behavior

    def filter_endpoint(self, endpoint, handler=_default_behavior):
        if endpoint.endswith('/'):
            self._registered_paths[endpoint] = handler
        else:
            self._registered_uris[endpoint] = handler

    def unfilter_endpoint(self, endpoint):
        if endpoint.endswith('/'):
            del self._registered_paths[endpoint]
        else:
            del self._registered_uris[endpoint]

    def tasks(self, data):
        tasks = []

        for path_key, path_handler in self._registered_paths.items():
            if data['uri'].startswith(path_key):
                tasks.append(asyncio.create_task(path_handler(data)))

        uri_handler = self._registered_uris.get(data['uri'], None if tasks else self._default_behavior)
        if uri_handler:
            hasHandler = True
            tasks.append(asyncio.create_task(uri_handler(data)))

        return tasks
