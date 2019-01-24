from json import dumps, dump
import sys

from flask import request

import requests
from requests import exceptions as req_exceptions

from PyQt5.QtCore import QObject, pyqtSignal


class ConnectionHandler(QObject):

    new_item_signal = pyqtSignal(dict)

    def __init__(self, flask_app):
        super(QObject, self).__init__()
        self.flask_app = flask_app

        @self.flask_app.route('/', methods=['GET', 'POST'])
        def new_item_incoming():
            return self.handle_request(request)

    def _die(self, message):
        print(message)
        sys.exit(1)

    def _check_data(self, data):
        keys = data.keys()
        if 'mimetype' in keys and 'data' in keys and '_id' in keys:
            return True
        else:
            return False

    def start_server(self):
        self.register_to_server()
        self.flask_app.run(
                debug=True,
                use_reloader=False,
                port=12345
        )

    def handle_request(self, request):
        if not request.is_json:
            return 'Supplied content not application/json', 415
        data = request.get_json()
        if self._check_data(data):
            print(data)
            self.new_item_signal.emit(data)
            return 'new request handled', 204
        else:
            return 'Malformed request', 400

    def register_to_server(self):
        headers = {'content-type': 'application/json'}
        try:
            response = requests.post(
                    'http://localhost:5000/clipboard/register',
                    headers=headers,
                    json={'url': 'http://localhost:12345/'},
                    timeout=5
            )
            response.raise_for_status()
        except req_exceptions.ConnectionError as e:
            self._die('Connection refused by remote server')
        except req_exceptions.Timeout as e:
            self._die('Remote server failed to respond in time')
        except req_exceptions.HTTPError as e:
            m = 'Remote server responded with statuscode {}\n'.format(
                response.status_code)
            m += 'Message from server: {}'.format(response.text)
            self._die(m)
