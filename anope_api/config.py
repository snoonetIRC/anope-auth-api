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

    API_URL = os.getenv('API_URL') or 'https://127.0.0.1:8888/api'
    API_TLS_VERIFY = get_bool(os.getenv('API_TLS_VERIFY') or 'true')
    OAUTH_EMAIL_API = os.getenv('OAUTH_EMAIL_API')
