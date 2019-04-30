import requests
from flask import abort, Blueprint, current_app, jsonify, request, Response
from werkzeug.exceptions import BadRequest, default_exceptions, Forbidden, HTTPException, Unauthorized

from ..api_keys import KEYS

auth_bp = Blueprint('auth', __name__)

ERROR_MAP = {
    "Invalid password": "no_auth",
}


def check_api_key():
    try:
        auth_header = request.headers['Authorization']
    except KeyError:
        raise Unauthorized()

    auth_type, data = auth_header.split(None, 1)
    if auth_type.lower() != 'bearer':
        raise Unauthorized()

    key = KEYS.get(data)
    if not key:
        raise Unauthorized()

    if not key['active']:
        raise Forbidden()

    return key['name']


def get_request_data():
    if request.content_type == 'application/json':
        request_data = request.json
    else:
        request_data = request.form

    if not request_data:
        raise BadRequest("Missing request data")

    return request_data


def get_params(*args):
    data = get_request_data()
    out = {}
    try:
        for arg in args:
            out[arg] = data[arg]
    except KeyError as e:
        raise BadRequest("Missing {!r} value".format(e.args[0]))

    return out


def do_request(endpoint, *args):
    key_name = check_api_key()
    request_data = get_params(*args)
    request_data['client_id'] = key_name

    with requests.post(
            current_app.config['API_URL'] + endpoint, data=request_data,
            headers={'X-Real-IP': request.access_route[0]},
    ) as response:
        status = response.status_code
        response_data = response.json()

    response = jsonify(response_data)  # type: Response
    response.status_code = status

    return response


@auth_bp.route('/login', methods=['POST'])
def login():
    return do_request('/login', 'username', 'password')


@auth_bp.route('/logout', methods=['POST'])
def logout():
    return do_request('/logout', 'session')


@auth_bp.route('/register', methods=['POST'])
def register():
    return do_request('/register', 'username', 'password', 'email', 'source')


@auth_bp.route('/confirm', methods=['POST'])
def confirm():
    return do_request('/confirm', 'session', 'code')


@auth_bp.app_errorhandler(HTTPException)
@auth_bp.errorhandler(HTTPException)
def error_handler(error):
    if isinstance(error, HTTPException):
        response = jsonify(message=error.description)
        response.status_code = error.code
    else:
        response = jsonify(message="Unknown error")
        response.status_code = 500

    return response


for code, v in default_exceptions.items():
    auth_bp.app_errorhandler(code)(error_handler)
    auth_bp.errorhandler(code)(error_handler)
