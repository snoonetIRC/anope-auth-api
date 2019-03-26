from flask import jsonify, request, abort
from werkzeug.exceptions import BadRequest, InternalServerError

from . import app

ERROR_MAP = {
    "Invalid password": "no_auth",
}


@app.route('/login', methods=['POST'])
def check_auth():
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
        data = app.xmlrpc_client.checkAuthentication(username, password)
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
