import requests
from flask import Blueprint, current_app, jsonify, request, Response
from werkzeug.exceptions import default_exceptions, HTTPException

from anope_api.api_keys import KEYS

auth_bp = Blueprint('auth', __name__)


class APIError(HTTPException):
    def __init__(self, error_id, description=None, response=None):
        super().__init__(description=description, response=response)
        self.id = error_id


class NoAuthService(APIError):
    code = 502

    def __init__(self):
        super().__init__('no_backend', "Unable to connect to authentication service")


class NoKey(APIError):
    code = 401

    def __init__(self):
        super().__init__('no_key', "No valid API key supplied")


class NoAccess(APIError):
    code = 403

    def __init__(self):
        super().__init__('no_access', "You do not have permission to access this resource")


class NoData(APIError):
    code = 400

    def __init__(self):
        super().__init__('no_data', "No request parameters have been supplied")


class NoEmail(APIError):
    code = 400

    def __init__(self):
        super().__init__('missing_email', "Email required")


class BadEmail(APIError):
    code = 400

    def __init__(self):
        super().__init__('bad_email', "Email address not verified")


class MissingParameter(APIError):
    code = 400

    def __init__(self, param):
        super().__init__(
            'missing_parameter', "Missing {!r} parameter".format(param)
        )


def check_api_key():
    try:
        auth_header = request.headers['Authorization']
    except KeyError:
        raise NoKey()

    auth_type, data = auth_header.split(None, 1)
    if auth_type.lower() != 'bearer':
        raise NoKey()

    key = KEYS.get(data)
    if not key:
        raise NoKey()

    if not key['active']:
        raise NoAccess()

    return key['name']


BLOCK_PARAMS = [
    'force_confirm',
]


def get_request_data():
    if request.content_type == 'application/json':
        request_data = request.json
    else:
        request_data = request.form

    if not request_data:
        raise NoData()

    return {
        k: request_data[k] for k in request_data
        if k.lower() not in BLOCK_PARAMS
    }


def do_request(endpoint, **extra_params):
    key_name = check_api_key()
    request_data = dict(get_request_data())
    request_data['client_id'] = key_name
    request_data.update(extra_params)
    verify = current_app.config['API_TLS_VERIFY']

    try:
        with requests.post(
                current_app.config['API_URL'] + endpoint,
                data=request_data,
                headers={'X-Real-IP': request.access_route[0]},
                verify=verify,
        ) as response:
            status = response.status_code
            response_data = response.json()
    except requests.ConnectionError as e:
        raise NoAuthService() from e

    response = jsonify(response_data)  # type: Response
    response.status_code = status

    return response


@auth_bp.route('/login', methods=['POST'])
def login():
    return do_request('/login')


@auth_bp.route('/logout', methods=['POST'])
def logout():
    return do_request('/logout')


def check_email(email, user):
    api_url = current_app.config['OAUTH_EMAIL_API']
    if not api_url:
        return False

    params = {
        'email': email,
        'user': user,
    }

    try:
        with requests.get(api_url, params=params) as response:
            response.raise_for_status()
            response_data = response.json()
    except (requests.ConnectionError, requests.RequestException):
        return False

    return response_data['verified']


@auth_bp.route('/register', methods=['POST'])
def register():
    check_api_key()
    data = get_request_data()
    if 'oauth' in data:
        if 'email' not in data:
            raise NoEmail()

        if 'username' not in data:
            raise MissingParameter('username')

        if not check_email(data['email'], data['username']):
            raise BadEmail()

        return do_request('/register', force_confirm='1')

    return do_request('/register')


@auth_bp.route('/confirm', methods=['POST'])
def confirm():
    return do_request('/confirm')


@auth_bp.route('/resetpass', methods=['POST'])
def resetpass():
    return do_request('/resetpass')


@auth_bp.route('/resetpass/confirm', methods=['POST'])
def resetpass_confirm():
    return do_request('/resetpass/confirm')


@auth_bp.route('/user/set/password', methods=['POST'])
def user_set_password():
    return do_request('/user/set/password')


@auth_bp.route('/user/token/add', methods=['POST'])
def user_token_add():
    return do_request('/user/token/add')


@auth_bp.route('/user/token/delete', methods=['POST'])
def user_token_delete():
    return do_request('/user/token/delete')


@auth_bp.route('/user/token/list', methods=['POST'])
def user_token_list():
    return do_request('/user/token/list')


@auth_bp.route('/user/token/ping', methods=['POST'])
def user_token_ping():
    return do_request('/user/token/ping')


@auth_bp.route('/user/tags/add', methods=['POST'])
def user_tags_add():
    return do_request('/user/tags/add')


@auth_bp.route('/user/tags/delete', methods=['POST'])
def user_tags_delete():
    return do_request('/user/tags/delete')


@auth_bp.route('/user/tags/list', methods=['POST'])
def user_tags_list():
    return do_request('/user/tags/list')


@auth_bp.app_errorhandler(HTTPException)
@auth_bp.errorhandler(HTTPException)
def error_handler(error):
    if isinstance(error, APIError):
        error_data = {
            'message': error.description,
            'id': error.id,
        }
        status_code = error.code
    elif isinstance(error, HTTPException):
        message = error.description
        status_code = error.code
        error_data = {'message': message, 'id': "internal", 'code': status_code}
    else:
        message = "Unknown error"
        status_code = 500
        error_data = {'message': message, 'id': "internal", 'code': status_code}

    response = jsonify(status='error', error=error_data)
    response.status_code = status_code

    return response


for code, _ in default_exceptions.items():
    auth_bp.app_errorhandler(code)(error_handler)
    auth_bp.errorhandler(code)(error_handler)
