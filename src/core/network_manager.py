from time import sleep
from urllib.parse import urlencode

from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import QByteArray, QUrl


class NetworkManager:
    """
    This class is responsible for communication of the core itself with the remote clipboard.
    It works over HTTP-request and can push new data onto the server or get the data currently saved on the server
    to overwrite the local clipboard.
    Because the querying of the current data from the server is asynchrounus, a suitable callback needs  to be provided
    when calling the the appropriate function.
    """

    # URL used for posting a clip to the server
    server_post_url = QUrl('http://localhost:8000/post/')
    # URL used for querying the current clip from the server
    server_get_url = QUrl('http://localhost:8000/get/')
    # QNetworkAccesssManager responsible for executing each request
    manager = None

    def _prepare_data(self, data):
        """
        Converts the data into a format fit for sending with an HTTP-request
        :param data: The original data
        :return: A QByteArray with the encoded contents of data
        """
        # https://stackoverflow.com/questions/21529266/http-post-request-from-a-pyqt-gui
        parameters = urlencode({'new_contents': data})
        result = QByteArray()
        result.append(parameters)
        return result

    def send_data(self, data):
        """
        Receives the data to be saved in the remote clipboard and sends it to the server
        :param data: Data the currently in the local clipboard
        """
        # print('sending: {}'.format(data))
        request = QNetworkRequest(self.server_post_url)
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/x-www-form-urlencoded")
        post_data = self._prepare_data(data)
        self.manager.post(request, post_data)
        # print('finished sending')

    def download_finished(self, reply, callback):
        """
        Slot that gets called when the HTTP-Request is finished. Handles parsing of the data into a single string
        and then executes the callback received.
        :param reply: QNetworkreply, contains the received data
        :param callback: Function of 'view' that initiated the request originally
        """
        contents = reply.readAll()
        # https://forum.qt.io/topic/85064/qbytearray-to-string
        contents = str(contents.data(), encoding='utf-8')
        callback(contents)
        self.manager.finished.disconnect()

    def get_data(self, callback):
        """
        Queries the current data of the remote clipboard and executes callback upon their delivery.
        Callback right now will get called with a single  string
        :param callback: The function to be executed when the data arrive.
                         Use the function which will expect the clipboard content
        """
        request = QNetworkRequest(self.server_get_url)
        self.manager.finished.connect(lambda: self.download_finished(reply, callback))

        reply = self.manager.get(request)

    def __init__(self):
        self.manager = QNetworkAccessManager()
