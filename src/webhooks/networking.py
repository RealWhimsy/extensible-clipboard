from json import dumps, dump
import sys
import time, _thread

from flask import request

import requests
from requests import exceptions as req_exceptions

class HookWorker():

    def do_work(self, data, mimetype):
        result = {}
        if mimetype == 'text/plain':
            result['data'] = 'Worker doing his work'
            result['mimetype'] = 'application/xml'
            return result
        else:
            return None


class ConnectionHandler():

    def __init__(self, flask_app, port, clipserver, domain):
        self.flask_app = flask_app
        self.port = port
        self.clipserver = clipserver
        if domain == 'http://localhost':
            domain = domain + ':' + str(self.port) + '/'
        self.domain = domain
        self.respons_url = ''
        self.hook = HookWorker()

        @self.flask_app.route('/', methods=['POST'])
        def new_item_incoming():
            return self.handle_new_data(request)

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
                port=self.port
        )

    def delegate_work(self, data):
        time.sleep(5)
        print('wakey wakey')
        result = self.hook.do_work(data['data'], data['mimetype'])
        if result:
            data['parent'] = data.pop('_id')
            data['data'] = result['data']
            data['mimetype'] = result['mimetype']
            data['from_hook'] = True
            r = requests.post(self.response_url, json=data)
            print(r.json())

    def handle_new_data(self, request):
        if not request.is_json:
            return 'Supplied content not application/json', 415
        data = request.get_json()
        if self._check_data(data):
            _thread.start_new_thread(self.delegate_work, (data,))
            return '', 204
        else:
            return 'Malformed request', 400

    def register_to_server(self):
        try:
            response = requests.post(
                    self.clipserver,
                    json={'url': self.domain},
                    timeout=5
            )
            response.raise_for_status()
            self.response_url = response.json()['response_url']
        except req_exceptions.ConnectionError as e:
            self._die('Connection refused by remote server')
        except req_exceptions.Timeout as e:
            self._die('Remote server failed to respond in time')
        except req_exceptions.HTTPError as e:
            m = 'Remote server responded with statuscode {}\n'.format(
                response.status_code)
            m += 'Message from server: {}'.format(response.text)
            self._die(m)
