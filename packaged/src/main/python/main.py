from fbs_runtime.application_context.PyQt5 import ApplicationContext

import sys
import time

# from server.main import MainApp as MainServerApp
# from clipboard_server.main import  ClipboardServerApp as ClipboardApp

from server.main import  ClipServer
from clipboard_server.main import ClipboardServerApp
from util.context import Context

from configparser import ConfigParser



from importlib import machinery

if __name__ == '__main__':
    config = ConfigParser()
    config.read(ApplicationContext().get_resource('config/networking.ini'))

    main_server_port = config['main_server']['port']
    clipboard_port = config['clipboard_server']['port']
    clipboard_main_server_address = config['clipboard_server']['main_server_address']
    clipboard_domain = config['clipboard_server']['domain']
    clipboard_is_syncing = config['clipboard_server']['is_syncing']

    Context.ctx = ApplicationContext()       # 1. Instantiate ApplicationContext

    server = ClipServer(sys.argv, main_server_port)
    server.main()

    # TODO: quite messy way of waiting for the server to finish starting, but it should do the trick for now
    time.sleep(1)

    print("Start Server")

    clipboard = ClipboardServerApp(
        clipboard_port,
        clipboard_main_server_address,
        clipboard_domain,
        clipboard_is_syncing,
        sys.argv,
        Context.ctx.app
    )
    clipboard.main()
    exit_code = Context.ctx.app.exec_()      # 2. Invoke appctxt.app.exec_()
    # sys.exit(exit_code)

