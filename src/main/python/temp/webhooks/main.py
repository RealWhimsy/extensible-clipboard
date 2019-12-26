from argparse import ArgumentParser
import os
import sys

from flask import Flask

from networking import ConnectionHandler

"""
A webhook is a program that registers itself to teh remote clip-server.
Its purpose is to further process the data sent to the server. An example
could be transforming different image-types into each other.
Since a single webhook is expected to be limited in scope, it can specify
the mimetypes it is able to process so the server will only send it useful
data. The mimetyes can be changed in ConnectionHandler.TYPES
"""


class Webhook():
    """
    Parses arguments and inits the flask server
    """

    def main(self):
        self.flask_server.start_server()

    def __init__(self, argv):
        parser = ArgumentParser()
        parser.add_argument('-p', '--port', type=int, dest='port',
                            help='Port THIS server shall listen on, '
                            + 'defaults to 12345',
                            default=12345)
        parser.add_argument('-d', '--domain', type=str, dest='domain',
                            help='URL THIS server can be reached under, '
                            + 'must contain specified port, '
                            + 'defaults to localhost',
                            default='http://localhost')
        parser.add_argument('-c', '--clipserver', type=str, dest='clipserver',
                            help='URL this server can register itself '
                            + 'to the clipboard-server',
                            required=True)
        self.args = parser.parse_args()
        self.app = Flask(__name__)
        self.flask_server = ConnectionHandler(self.app,
                                              self.args.port,
                                              self.args.clipserver,
                                              self.args.domain)


if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    hook = Webhook(sys.argv)
    hook.main()
