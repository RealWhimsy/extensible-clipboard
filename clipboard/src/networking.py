import sys

from flask import request

import requests
from requests import exceptions as req_exceptions

from PyQt5.QtCore import QObject, pyqtSignal
from utils import NetworkUtil

"""
This file contains the two classes needed to provide the communication
to the remote clip-server.
ConnectionHandler is a QT-wrapper over a Flask server and will listen to
incoming requests and handle their data.
ClipSender on the other hand will send clips that were created locally and
send them to the remote server.
This was necessary since flask cannot take action itself withouth receiing
a request
"""


class ConnectionHandler(QObject):
    """
    Wrapper over Flask
    """

    new_item_signal = pyqtSignal(dict)
    recipient_id_got = pyqtSignal(str)

    def __init__(self, flask_app, port, clip_server_url, domain):
        super(QObject, self).__init__()
        self.flask_app = flask_app
        self.port = port
        self.clip_server_url = clip_server_url + "clipboards/register"
        if domain == 'http://localhost':
            self.domain = domain + ':' + str(self.port) + '/'
        # Request own ip through external service for more convenience
        elif domain == 'public':
            self.domain = NetworkUtil.get_public_ipv4(self.port)
        else:
            self.domain = domain + ':' + str(self.port) + '/'

        # needed to add the route here, because self.flask_app needs to be set
        @self.flask_app.route('/', methods=['POST'])
        def new_item_incoming():
            return self.handle_request(request)

    def _die(self, message):
        print("Clipboard Server: Networking has died")
        # This causes the app to crash if connection fails
        # TODO: add slot for error messages
        # sys.exit(1)

    def _check_data(self, data):
        """
        Checks if the relevant data could be parsed
        """
        keys = data.keys()
        if 'mimetype' in keys and 'data' in keys and '_id' in keys:
            return True
        else:
            return False

    def start_server(self):
        """
        Run flask on specified port
        """
        self.register_to_server()
        self.flask_app.run(
                host='0.0.0.0',
                port=self.port
        )

    def handle_request(self, request):
        """
        Parses incoming data from the server for the relevant parts
        """
        data = {}
        data['data'] = request.get_data()
        data['mimetype'] = request.headers['Content-Type']
        data['_id'] = request.headers['X-C2-_id']
        data['parent'] = request.headers.get('X-C2-parent', None)
        self.new_item_signal.emit(data)
        return '', 204

    def register_to_server(self):
        """
        Registers itself to the remote server. Kills the whole
        application if this fails
        """
        try:
            response = requests.post(
                    self.clip_server_url,
                    json={'url': self.domain},
                    timeout=5
            )
            response.raise_for_status()
            self.recipient_id_got.emit(response.json()['_id'])
        except req_exceptions.ConnectionError as e:
            self._die('Connection refused by remote server')
        except req_exceptions.Timeout as e:
            self._die('Remote server failed to respond in time')
        except req_exceptions.HTTPError as e:
            m = 'Remote server responded with statuscode {}\n'.format(
                response.status_code)
            m += 'Message from server: {}'.format(response.text)
            self._die(m)


class ClipSender:
    """
    Posting data to remote clip-server
    """

    def __init__(self, clip_server_url, id_updater):
        self.post_url = clip_server_url + "clips/"
        self.call_hook_url = self.post_url + "{}/hooks/call"
        self.add_child_url = self.post_url + "{}/children"
        self.id_updater = id_updater

    def _post_clip(self, clip, parent_id=None):
        """
        Sends a clip received from the local clipboard to the server
        """
        headers = {'Content-Type': clip['mimetype'],
                   'X-C2-sender_id': self._id, }
        if 'filename' in clip:
            headers['X-C2-filename'] = clip['filename']
        if parent_id:
            url = self.add_child_url.format(parent_id)
        else:
            url = self.post_url

        try:
            r = requests.post(
                url,
                headers=headers,
                data=clip['data'],
                timeout=100
            )
            r.raise_for_status()
        except req_exceptions.ConnectionError as e:
            print('Connection refused by server')
            r = None
        except req_exceptions.Timeout as e:
            print(e)
            print('Server failed to respond in time')
            r = None
        except req_exceptions.HTTPError as e:
            print('Remote server responded with statuscode {}\n'.format(
                r.status_code))
            print('Message from server: {}'.format(r.text))
            r = None
        return r

    def add_clips_to_server(self, clip_list):
        """
        Receives the current clipboard-data and pushes them onto the server
        """
        if not clip_list:
            return
        r = self._post_clip(clip_list[0])
        if r and r.status_code == 201:
            parent_id = r.headers['X-C2-_id']
            self.id_updater(parent_id)
            # Calls hooks on remote server
            requests.post(self.call_hook_url.format(parent_id))
            if len(clip_list) > 1:
                # adds subsequent entries as children of the first
                for c in clip_list[1:]:
                    r = self._post_clip(c, parent_id)
                    if r and r.status_code == 201:
                        requests.post(self.call_hook_url.format(
                            r.headers['X-C2-_id']))
