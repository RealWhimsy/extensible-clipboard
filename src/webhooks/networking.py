import re
import sys
import _thread

from flask import request

import requests
from requests import exceptions as req_exceptions

class HookWorker():

    def do_work(self, data, mimetype):
        result = {}
        if mimetype == 'text/html':
            if data.startswith('<a') and data.endswith('/a>'):
                # Extracts link from single a-Element
                pattern = re.compile(r'href=[\'\"](\S*)[\'\"]')
                result['data'] = pattern.search(data).group(1)
            else:
                result['data'] = str(data)

            result['mimetype'] = 'text/plain'
            return result
        elif mimetype == 'text/plain':
            result['mimetype'] = 'application/json'
            result['data'] = {'senttext': str(data)}
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
        result = self.hook.do_work(data['data'], data['mimetype'])
        if result:
            result['from_hook'] = True
            result['sender_id'] = self._id
            requests.post(data['response_url'], json=result)

    def handle_new_data(self, request):
        print(request.headers['Content-Type'])
        if not request.is_json:
            return 'Supplied content not application/json', 415
        data = request.get_json()
        if self._check_data(data):
            _thread.start_new_thread(self.delegate_work, (data,))
            return '', 204
        else:
            return 'Malformed request', 400

    def register_to_server(self):
        types = ['text/html', 'text/plain'] 
        try:
            response = requests.post(
                    self.clipserver,
                    json={
                        'url': self.domain,
                        'subscribed_types': types},
                    timeout=5
            )
            response.raise_for_status()
            self.response_url = response.json()['response_url']
            self._id = response.json()['_id']
        except req_exceptions.ConnectionError as e:
            self._die('Connection refused by remote server')
        except req_exceptions.Timeout as e:
            self._die('Remote server failed to respond in time')
        except req_exceptions.HTTPError as e:
            m = 'Remote server responded with statuscode {}\n'.format(
                response.status_code)
            m += 'Message from server: {}'.format(response.text)
            self._die(m)
