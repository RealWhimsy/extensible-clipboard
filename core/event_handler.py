from PyQt5.QtWidgets import QApplication

from .clipboard import Clipboard
from .network_manager import NetworkManager

class EventHandler:
    """
    This class is responsible to take data from other programs, plugins etc and save them to the clipboard
    and also forwards the data to the server
    It also retrieves data from the server and can return it
    """
    clipboard = None
    network_manager = None

    def _save_to_local_clipboard(self, data):
        """
        Saves data to the local clipboard. Uses a QClipboard
        :param data: Data to be saved
        """
        self.clipboard.save(data)

    def _propagate_to_server(self, data):
        """
        Passes the saved data to the server to store it there
        :param data: The data to be sent
        """
        self.network_manager.send_data(data)

    def put_into_storage(self, data):
        """
        Responsible for storing data on a higher level. This function should be called when you want to save
        data in your clipboard and on the server simultaneously
        :data: The data to be saved
        """
        self._save_to_local_clipboard(data)
        self._propagate_to_server(data)

    def retrieve_from_storage(self):
        """
        Queries the server for the current content of the clipboard and returns the data
        :return: The data sent from the server
        """
        print('retrieving from server ...')

    def __init__(self, qApp):
        self.clipboard = Clipboard(qApp.clipboard())
        self.network_manager = NetworkManager()
