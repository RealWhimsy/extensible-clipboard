import os
import sys

from database import ClipSqlPeeweeDatabase
from flask_server import FlaskServer
from resources import Clip, Clips, ChildClipAdder, Recipient
from configparser import ConfigParser
from threading import Thread

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
        child_add_view = ChildClipAdder.as_view('child_adder')
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
        server_thread = Thread(target=self.flask_server.start_server)
        server_thread.daemon = True
        server_thread.start()

    def __init__(self, argv, port=None):
        # self.database = ClipDatabase()
        self.database = ClipSqlPeeweeDatabase()

        # The flask-server itself
        if port is not None:
            self.flask_server = FlaskServer(__name__, self.database, port)
        elif len(argv) > 1 and argv[1].isdigit():
            m_port = argv[1]
            self.flask_server = FlaskServer(__name__, self.database, m_port)
        elif len(argv) > 1 and argv[1] == '-h':
            print('A port can be specified as the first argument')
            print('5000 will be used otherwise')
            # TODO: this may cause problems? should be removed later on
            sys.exit()
        else:
            self.flask_server = FlaskServer(__name__, self.database)


if __name__ == "__main__":
    # Changes into dir for imports to work as expected
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    q_app = ClipServer(sys.argv)
    q_app.main()
