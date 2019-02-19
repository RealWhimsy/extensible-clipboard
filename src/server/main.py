import signal
import os
import sys

from flask import Flask
from flask_restful import Api

from database import ClipDatabase
from flask_server import FlaskServer
from resources import Clip, Clips, ChildClipAdder, Recipient

"""
Built after https://codereview.stackexchange.com/questions/114221/python-gui-by-qtwebkit-and-flask
https://stackoverflow.com/questions/41401386/proper-use-of-qthread-subclassing-works-better-method
"""  # noqa


class MainApp():

    def add_resources(self):
        # Creates endpoint for REST-Api
        self.api.add_resource(ChildClipAdder,
                              '/clip/<uuid:clip_id>/add_child',
                              endpoint='adder',
                              resource_class_kwargs={
                                    'server': self.server_qt
                              })
        self.api.add_resource(Clip,
                              '/clip/latest/',
                              '/clip/<uuid:clip_id>/',
                              '/clip/<uuid:clip_id>/get_alternatives/',
                              '/clip/<uuid:clip_id>/call_hooks',
                              resource_class_kwargs={
                                    'server': self.server_qt
                              })
        self.api.add_resource(Clips,
                              '/clip/',
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
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    q_app = MainApp(sys.argv)
    q_app.main()
