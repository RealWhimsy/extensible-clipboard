from argparse import ArgumentParser
import sys

from flask import Flask

from networking import ConnectionHandler

"""
Built after https://codereview.stackexchange.com/questions/114221/python-gui-by-qtwebkit-and-flask
https://stackoverflow.com/questions/41401386/proper-use-of-qthread-subclassing-works-better-method
"""  # noqa


class Webhook():

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
    hook = Webhook(sys.argv)
    hook.main()
