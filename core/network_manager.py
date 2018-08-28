from urllib.parse import urlencode

from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import QByteArray, QUrl

class NetworkManager:

    server_post_url = QUrl('http://localhost:8000/post/')
    manager = None

    def prepare_data(self, data):
        # https://stackoverflow.com/questions/21529266/http-post-request-from-a-pyqt-gui
        parameters = urlencode({'new_contents': data})
        result = QByteArray()
        result.append(parameters)
        return result

    def send_data(self, data):
        #print('sending: {}'.format(data))
        request = QNetworkRequest(self.server_post_url)
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/x-www-form-urlencoded")
        post_data = self.prepare_data(data)
        self.manager.post(request, post_data)
        #print('finished sending')


    def __init__(self):
        self.manager = QNetworkAccessManager()