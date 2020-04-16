import os
import sys

from database import ClipSqlPeeweeDatabase
from server import Server
from configparser import ConfigParser
from argparse import ArgumentParser

"""
This class is responsible for starting the whole application.
It initializes the database first and then builds the configuration
for the Flask server
"""


class ClipServer():



    def main(self):
        # self.add_resources()
        self.flask_server.start()

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
