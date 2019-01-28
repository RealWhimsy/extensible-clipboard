import signal
import sys

from flask import Flask
from flask_restful import Api

from src.server.database import ClipDatabase
from src.server.flask_server import FlaskServer
from src.server.resources import Clip, Recipient

"""
Built after https://codereview.stackexchange.com/questions/114221/python-gui-by-qtwebkit-and-flask
https://stackoverflow.com/questions/41401386/proper-use-of-qthread-subclassing-works-better-method
"""  # noqa


class MainApp():

    def add_resources(self):
        # Creates endpoint for REST-Api
        self.api.add_resource(Clip,
                              '/clip/',
                              '/clip/latest/',
                              '/clip/<uuid:clip_id>',
                              '/clip/<uuid:clip_id>/add_child',
                              '/clip/<uuid:clip_id>/get_alternatives/',
                              resource_class_kwargs={
                                    'server': self.server_qt
                              })

        self.api.add_resource(Recipient,
                              '/clipboard/register',
                              '/hook/register',
                              resource_class_kwargs={
                                    'server': self.server_qt
                               })

    def main(self):
        self.add_resources()
        self.server_qt.start_server()

    def __init__(self, argv):
        # The flask-server itself
        self.flask_server = Flask(__name__)
        # Restful-Flask server
        self.api = Api(self.flask_server)
        # Database for saving clips, currently mongo
        self.database = ClipDatabase()

        # The Flask-Server itself
        self.server_qt = FlaskServer(self.flask_server, self.database)


if __name__ == "__main__":
    q_app = MainApp(sys.argv)
    q_app.main()
