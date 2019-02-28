from json import dumps
import re
import sys
import _thread

from flask import request

import requests
from requests import exceptions as req_exceptions

"""
This file contains the two classes necessary to provide the communication
to the remote clip-server.
ConnectionHandler is a wrapper for Flask itself and will pass received data
to HookWorker. In order not to block the remote clip-server, ConnectionHandler
returns immediately with a response if the data was valid while HookWorker
runs in its own thread and returns the data when ready. This was introduced
because of how long the processing a hook needs to do might vary and this
could harm the performance of the whole system if done synchronous.
"""


class HookWorker():

    def do_work(self, data, mimetype):
        """
        Does some processing on the data and returns a dict consisting of
        the new mimetype and the new data. None if any error occurred
        """
        result = {}
        if mimetype == 'text/plain':
            result['mimetype'] = 'application/json'
            result['data'] = {'senttext': data.decode()}
            return result
        else:
            return None


class ConnectionHandler():

    # Specify the mimetypes the hook is able to process HERE
    TYPES = ['text/html', 'text/plain']

    def __init__(self, flask_app, port, clipserver, domain):
        self.flask_app = flask_app
        self.port = port
        self.clipserver = clipserver
        self.register_url = clipserver + "hook/register"
        if domain == 'http://localhost':
            domain = domain + ':' + str(self.port) + '/'
        self.domain = domain
        self.response_url = ''
        self.hook = HookWorker()

        @self.flask_app.route('/', methods=['POST'])
        def new_item_incoming():
            return self.handle_new_data(request)

    def _die(self, message):
        print(message)
        sys.exit(1)

    def start_server(self):
        """
        Starts flask on specified port
        """
        self.register_to_server()
        self.flask_app.run(
                host='0.0.0.0',
                port=self.port
        )

    def delegate_work(self, clip):
        """
        Passes the received clip to HookWorker and sends it to the clip-server
        if it could be processed successfully. Otherwise, no data will be sent.
        """
        result = self.hook.do_work(clip['data'], clip['mimetype'])
        if result:
            """
            from_hook needs to be specified so clip data will NOT be sent to
            hooks again which in turn could lead to an endless cycle
            """
            headers = {'Content-Type': result['mimetype'],
                       'X-C2-from_hook': "True"}
            if result['mimetype'] == 'application/json':
                result['data'] = dumps(result['data'])
            requests.post(clip['response_url'],
                          data=result['data'],
                          headers=headers)

    def handle_new_data(self, request):
        """
        Parses the incoming data and processes them
        """
        clip = {'data': request.get_data(),
                'mimetype': request.headers['Content-Type'],
                'response_url': request.headers['X-C2-response_url']}
        if clip['mimetype'] not in self.TYPES:
            return 'Supplied content not subscribed', 415
        # new thread, so basically async
        _thread.start_new_thread(self.delegate_work, (clip,))
        return '', 204

    def register_to_server(self):
        """
        Registers itself to the remote clip-server and dies if not sucessful
        """
        try:
            response = requests.post(
                    self.register_url,
                    json={
                        'url': self.domain,
                        'subscribed_types': self.TYPES},
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
