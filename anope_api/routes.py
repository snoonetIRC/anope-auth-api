import os
import ssl
from xmlrpc.client import ServerProxy

from flask import jsonify, request, abort
from werkzeug.exceptions import BadRequest, InternalServerError

from . import app

XMLRPC_ENDPOINT = os.getenv('XMLRPC_ENDPOINT') or "https://127.0.0.1:8443/xmlrpc"

ctx = ssl.create_default_context()
# most likely connecting over localhost, so ignore cert names
ctx.check_hostname = False

xmlrpc_client = ServerProxy(XMLRPC_ENDPOINT, context=ctx)

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
        data = xmlrpc_client.checkAuthentication(username, password)
    except ConnectionRefusedError:
        return abort(InternalServerError("Unable to connect to authentication backend"))

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
