from json import dumps, dump
import sys

import requests
from requests import exceptions as req_exceptions

from PyQt5.QtCore import QObject


class ConnectionHandler(QObject):

    def __init__(self, flask_app):
        super(QObject, self).__init__()
        self.flask_app = flask_app

    def start_server(self):
        self.register_to_server()
        print('Starting server')
        self.flask_app.run(
                debug=True,
                use_reloader=False,
                port=12345
        )

    def register_to_server(self):
        print('registering')
        headers = {'content-type': 'application/json'}
        try:
            response = requests.post(
                    'http://localhost:5000/clipboard/register',
                    headers=headers,
                    json={'url': 'http://localhost:12345/'},
                    timeout=5
            )
        except req_exceptions.ConnectionError as e:
            print('Connection refused by remote server')
            sys.exit(1)
        try:
            response.raise_for_status()
            print('okay')
        except req_exceptions.HTTPError as e:
            print('Remote server responded with statuscode {}'.format(
                response.status_code
            ))
            print('Message from server: {}'.format(response.text))
            sys.exit(1)
