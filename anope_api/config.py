import os

_BOOL_MAP = {
    'true': True,
    'yes': True,
    'y': True,
    'on': True,
    'enable': True,
    '1': True,

    'false': False,
    'no': False,
    'n': False,
    'off': False,
    'disable': False,
    '0': False,
}


def get_bool(text):
    return _BOOL_MAP[text]


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'you-will-never-guess'

    XMLRPC_URI = os.getenv('XMLRPC_URI') or os.getenv('XMLRPC_ENDPOINT')
    XMLRPC_TLS_CHECK_HOSTNAME = get_bool(os.getenv('XMLRPC_TLS_CHECK_HOSTNAME') or 'true')
