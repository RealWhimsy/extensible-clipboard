import os
import sys

from server.database import ClipDatabase, ClipSqlDatabase
from server.flask_server import FlaskServer
from server.resources import Clip, Clips, ChildClipAdder, Recipient

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
        server_thread = Thread(target=self.flask_server.start_server)
        server_thread.daemon = True
        server_thread.start()

    def __init__(self, argv, port=None):
        # Database for saving clips, currently mongo
        self.database = ClipDatabase()
        self.database_2_temp = ClipSqlDatabase()
        # self.database_2_temp.add_recipient("abasdasd", True, [])
        # self.database_2_temp.get_recipients()
        self.database_2_temp.get_all_clips()
        self.database_2_temp.save_clip({'mimetype': 'text/plain', 'data': 'Freude schöner Götterfunken' })

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
