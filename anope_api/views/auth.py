from flask import Blueprint, current_app
from flask import jsonify, request, abort
from werkzeug.exceptions import BadRequest, InternalServerError, Unauthorized, Forbidden

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


@auth_bp.route('/login', methods=['POST'])
def check_auth():
    check_api_key()
    if request.content_type == 'application/json':
        request_data = request.json
    else:
        request_data = request.form

    if not request_data:
        return abort(BadRequest("Missing request data"))

    try:
        username = request_data['username']
        password = request_data['password']
    except KeyError as e:
        return abort(BadRequest("Missing {!r} field".format(e.args[0])))

    if not username.strip() or not password.strip():
        return abort(BadRequest("Username or password is empty"))

    try:
        data = current_app.xmlrpc_client.checkAuthentication(username, password)
    except ConnectionRefusedError:
        return abort(InternalServerError(
            "Unable to connect to authentication backend"
        ))

    error = data.get('error')
    if error:
        error_msg = ERROR_MAP.get(error, "other")
        account = None
        message = error
    else:
        error_msg = None
        account = data['account']
        message = data['result']

    return jsonify({
        'account': account,
        'error': error_msg,
        'message': message,
    })
