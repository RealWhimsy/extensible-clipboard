import os
import sys

from database import ClipDatabase
from flask_server import FlaskServer
from resources import Clip, Clips, ChildClipAdder, Recipient

"""
This class is responsible for starting the whole application.
It initializes the database first and then builds the configuration
for the Flask server
"""


class MainApp():

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

        self.flask_server.add_url_rule('/clip/',
                                       view_func=clip_list_view,
                                       methods=['GET', 'POST'])
        self.flask_server.add_url_rule('/clip/latest/',
                                       view_func=clip_view,
                                       methods=['GET'])
        self.flask_server.add_url_rule('/clip/<uuid:clip_id>/',
                                       view_func=clip_details,
                                       methods=['GET', 'DELETE',
                                                'PUT', ])
        self.flask_server.add_url_rule('/clip/<uuid:clip_id>/'
                                       + 'get_alternatives/',
                                       view_func=clip_view,
                                       methods=['GET'])
        self.flask_server.add_url_rule('/clip/<uuid:clip_id>/call_hooks',
                                       view_func=clip_view,
                                       methods=['POST'])
        self.flask_server.add_url_rule('/clip/<uuid:clip_id>/add_child',
                                       view_func=child_add_view,
                                       methods=['POST'])
        self.flask_server.add_url_rule('/clipboard/register',
                                       view_func=recipient_view,
                                       methods=['POST'])
        self.flask_server.add_url_rule('/hook/register',
                                       view_func=recipient_view,
                                       methods=['POST'])

    def main(self):
        self.add_resources()
        self.flask_server.start_server()

    def __init__(self, argv):
        # Database for saving clips, currently mongo
        self.database = ClipDatabase()
        # The flask-server itself
        if len(argv) > 1 and argv[1].isdigit():
            port = argv[1]
            self.flask_server = FlaskServer(__name__, self.database, port)
        elif len(argv) > 1 and argv[1] == '-h':
            print('A port can be specified as the first argument')
            print('5000 will be used otherwise')
            sys.exit()
        else:
            self.flask_server = FlaskServer(__name__, self.database)


if __name__ == "__main__":
    # Changes into dir for imports to work as expected
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    q_app = MainApp(sys.argv)
    q_app.main()
