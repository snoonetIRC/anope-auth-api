def create_xmlrpc_client(instance):
    from xmlrpc.client import ServerProxy

    def _setdefault(key, default=None):
        return instance.config.setdefault(key, default)

    import ssl
    ssl_context = ssl.create_default_context()

    ssl_context.check_hostname = _setdefault("XMLRPC_TLS_CHECK_HOSTNAME", True)

    uri = _setdefault("XMLRPC_URI", "https://127.0.0.1:8443/xmlrpc")

    return ServerProxy(uri, context=ssl_context)


def create_instance():
    from flask import Flask
    from .config import Config
    instance = Flask(__name__)

    instance.config.from_object(Config)

    instance.xmlrpc_client = create_xmlrpc_client(instance)

    return instance


app = create_instance()

from . import routes
