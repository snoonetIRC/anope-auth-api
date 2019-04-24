import requests
from flask import abort, Blueprint, current_app, jsonify, request
from werkzeug.exceptions import BadRequest, Forbidden, Unauthorized

from ..api_keys import KEYS

auth_bp = Blueprint('auth', __name__)

ERROR_MAP = {
    "Invalid password": "no_auth",
}


def check_api_key():
    try:
        auth_header = request.headers['Authorization']
    except KeyError:
        return abort(Unauthorized())

    auth_type, data = auth_header.split(None, 1)
    if auth_type.lower() != 'bearer':
        return abort(Unauthorized())

    key = KEYS.get(data)
    if not key:
        return abort(Unauthorized())

    if not key['active']:
        return abort(Forbidden())

    return True


def get_request_data():
    if request.content_type == 'application/json':
        request_data = request.json
    else:
        request_data = request.form

    if not request_data:
        return abort(BadRequest("Missing request data"))

    return request_data


def get_params(*args):
    data = get_request_data()
    out = {}
    try:
        for arg in args:
            out[arg] = data[arg]
    except KeyError:
        return abort(BadRequest("Missing {!r} value".format(e.args[0])))

    return out


def do_request(endpoint, *args):
    check_api_key()
    request_data = get_params(*args)

    with requests.post(
            current_app.config['API_URL'] + endpoint, data=request_data
    ) as response:
        response.raise_for_status()
        response_data = response.json()

    return jsonify(response_data)


@auth_bp.route('/login', methods=['POST'])
def login():
    return do_request('/login', 'username', 'password')


@auth_bp.route('/logout', methods=['POST'])
def logout():
    return do_request('/logout', 'session')


@auth_bp.route('/register', methods=['POST'])
def check_auth():
    return do_request('/register', 'username', 'password', 'email', 'source')


@auth_bp.route('/confirm', methods=['POST'])
def check_auth():
    return do_request('/confirm', 'session', 'code')
