import os
import sys

from database import ClipSqlPeeweeDatabase
from networking import FlaskServer
from resources import Clip, Clips, ChildClip, Recipient
from configparser import ConfigParser
from argparse import ArgumentParser

"""
This class is responsible for starting the whole application.
It initializes the database first and then builds the configuration
for the Flask server
"""


class ClipServer():

    def add_resources(self):
        """
        Since we use class-based routing for the server, we cannot utilize
        the decorators provided by Flask and instead have to plug in the
        routes manually
        """
        clip_view = Clip.as_view('clip')  # 'clip' can be used in url_for
        clip_details = Clip.as_view('clip_details')
        clip_list_view = Clips.as_view('clip_list')
        child_add_view = ChildClip.as_view('child_adder')
        recipient_view = Recipient.as_view('recipient')

        self.flask_server.add_url_rule('/clips/',
                                       view_func=clip_list_view,
                                       methods=['GET', 'POST'])
        self.flask_server.add_url_rule('/clips/latest/',
                                       view_func=clip_view,
                                       methods=['GET'])
        self.flask_server.add_url_rule('/clips/<uuid:clip_id>/',
                                       view_func=clip_details,
                                       methods=['GET', 'DELETE',
                                                'PUT', ])
        self.flask_server.add_url_rule('/clips/<uuid:clip_id>/'
                                       + 'alternatives/',
                                       view_func=clip_view,
                                       methods=['GET'])
        self.flask_server.add_url_rule('/clips/<uuid:clip_id>/hooks/call',
                                       view_func=clip_view,
                                       methods=['POST'])
        self.flask_server.add_url_rule('/clips/<uuid:clip_id>/children',
                                       view_func=child_add_view,
                                       methods=['POST'])
        self.flask_server.add_url_rule('/clipboards/register',
                                       view_func=recipient_view,
                                       methods=['POST'])
        self.flask_server.add_url_rule('/hooks/register',
                                       view_func=recipient_view,
                                       methods=['POST'])

    def main(self):
        self.add_resources()
        self.flask_server.start_server()

    def __init__(self, port):
        self.database = ClipSqlPeeweeDatabase()
        self.flask_server = FlaskServer(__name__, self.database, port)

if __name__ == "__main__":
    config = ConfigParser()
    argparser = ArgumentParser()
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    config.read('./../config/config.ini')
    argparser.add_argument("-p", '--port',
                    help="The port used for providing the server.",
                    default=config['networking']['port'])
    args, unknown = argparser.parse_known_args()
    q_app = ClipServer(args.port)
    q_app.main()
