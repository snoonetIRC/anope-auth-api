KEYS = {
    'ExampleApiKey': {
        # Whether the core should check this key
        'enabled': False,

        # This data is not currently used by the core
        # Use it for organizing keys
        'name': 'Example',
        'SomeInfo': 'ArbitraryValue',
    }
}

try:
    from local_api_config import *
except ImportError:
    pass
