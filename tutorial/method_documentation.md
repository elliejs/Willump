# Willump Methods
- `async start(): Willump`
- `async request(self, method: str, endpoint: str, **kwargs): ClientResponse`
- `async subscribe(self, event: str, default_handler=None: _(data: json): None, subscription=None: EventSubscription): EventSubscription`
- `get_subscriptions(self, event: str): list(EventSubscription)`
- `subscription_filter_endpoint(self, subscription: EventSubscription, endpoint: str, handler: _(data: json): None): None`
- `subscription_unfilter_endpoint(self, subscription: EventSubscription, endpoint: str): None`
- `async unsubscribe(self, event: str, subscription=None: EventSubscription): None`
- `async close(self): None`

# Nunu Methods
- `async nunu(self, Allow_Origin: str, ssh_key_path: str, port=8989: int, host=None: ip_addr): Willump`


# EventSubscription Methods
- `filter_endpoint(self, endpoint: str, handler=_default_behavior: _(data: json) -> None) -> None`
- `unfilter_endpoint(self, endpoint: str) -> None`

# EventCode Enum
```py
class Event_Code(Enum):
    SUBSCRIBE = 5
    UNSUBSCRIBE = 6
    RESPONSE = 8
```
