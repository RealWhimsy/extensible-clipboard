import os
import sys

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
        clip_view = Clip.as_view('clip')
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
        self.flask_server = FlaskServer(__name__, self.database)


if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    q_app = MainApp(sys.argv)
    q_app.main()
