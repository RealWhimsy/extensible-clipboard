from time import sleep
from urllib.parse import urlencode

from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtCore import QByteArray ,QUrl

class NetworkManager:

    server_post_url = QUrl('http://localhost:8000/post/')
    server_get_url = QUrl('http://localhost:8000/get/')
    manager = None

    def _prepare_data(self, data):
        # https://stackoverflow.com/questions/21529266/http-post-request-from-a-pyqt-gui
        parameters = urlencode({'new_contents': data})
        result = QByteArray()
        result.append(parameters)
        return result

    def send_data(self, data):
        #print('sending: {}'.format(data))
        request = QNetworkRequest(self.server_post_url)
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/x-www-form-urlencoded")
        post_data = self._prepare_data(data)
        self.manager.post(request, post_data)
        #print('finished sending')

    def download_finished(self, reply, callback):
        contents = QByteArray()
        contents = reply.readAll()
        # https://forum.qt.io/topic/85064/qbytearray-to-string
        contents = str(contents.data(), encoding='utf-8')
        callback(contents)
        self.manager.finished.disconnect()


    def get_data(self, callback):
        self.download_callback = callback
        request = QNetworkRequest(self.server_get_url)
        self.manager.finished.connect(lambda: self.download_finished(reply, callback))

        reply = self.manager.get(request)


    def __init__(self):
        self.manager = QNetworkAccessManager()