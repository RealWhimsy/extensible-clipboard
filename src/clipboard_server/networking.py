from json import dumps, dump

from PyQt5.QtCore import QByteArray, QUrl, QBuffer
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest

class ConnectionHandler():

    def __init__(self):
        print('initing networks')
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.handle_response)

    def handle_response(self, reply):
        print('in handling')
        print(reply.error())
        print(reply.readAll())

    def register_to_server(self):
        print('registering')
        req = QNetworkRequest(QUrl('http://localhost:5000/clipboard/register'))
        req.setRawHeader('content-type'.encode(encoding='utf8'), 'application/json'.encode(encoding='utf8'))
        data = {'url': 'world'}
        data = dumps(data)
        data = data.encode(encoding='utf8')
        ba = QByteArray(data)
        _buffer = QBuffer(ba)
        print(data)
        self.network_manager.post(req, data)

