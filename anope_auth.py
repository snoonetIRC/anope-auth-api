import os
import ssl
from xmlrpc.client import ServerProxy

from flask import jsonify, request, abort
from flask.app import Flask

XMLRPC_ENDPOINT = os.getenv('XMLRPC_ENDPOINT') or "https://127.0.0.1:8443/xmlrpc"

ctx = ssl.create_default_context()
# most likely connecting over localhost, so ignore cert names
ctx.check_hostname = False

xmlrpc_client = ServerProxy(XMLRPC_ENDPOINT, context=ctx)

app = Flask(__name__)


@app.route('/login', methods=['POST'])
def check_auth():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    if not username.strip() or not password.strip():
        abort(400)

    data = xmlrpc_client.checkAuthentication(username, password)
    error = data.get('error')
    if error:
        return jsonify({'error': error})

    return jsonify({
        'account': data['account'],
        'result': data['result'],
    })


if __name__ == '__main__':
    app.run()
