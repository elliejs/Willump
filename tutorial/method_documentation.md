# Willump Methods
- `async start() -> None`
- `async request(self, method: str, endpoint: str, **kwargs) -> ClientResponse`
- `async subscribe(self, event: str, default_handler=None: _(data: json) -> None, subscription=None: EventSubscription) -> EventSubscription`
- `get_subscriptions(self, event: str) -> list(EventSubscription)`
- `subscription_filter_endpoint(self, subscription: EventSubscription, endpoint: str, handler: _(data: json) -> None)`
- `subscription_unfilter_endpoint(self, subscription: EventSubscription, endpoint: str)`
- `def unsubscribe(self, event, subscription=None)`


# EventSubscription Methods

# EventCode Enum
```py
class Event_Code(Enum):
    SUBSCRIBE = 5
    UNSUBSCRIBE = 6
    RESPONSE = 8
```
