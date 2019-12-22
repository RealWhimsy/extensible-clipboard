from fbs_runtime.application_context.PyQt5 import ApplicationContext

import sys
import time

# from server.main import MainApp as MainServerApp
# from clipboard_server.main import  ClipboardServerApp as ClipboardApp

from server.main import  ClipServer
from clipboard_server.main import ClipboardServerApp
from util.context import Context

from configparser import ConfigParser
from argparse import ArgumentParser



from importlib import machinery

if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument("-nocs", '--noclipserver',
                    action="store_true",
                    help="Do not start a clip server. You need to define a host clipserver!")
    ap.add_argument("-cshost", '--clipserverhost',
                    help="Define the address of a host clipserver. (pattern: http://123.123.123.123:1234/)")
    ap.add_argument("-nocbs", "--noclipboardserver",
                    action="store_true",
                    help="Do not start a clipboard server. This may be useful, if you want to host a remote server.")
    cl_arguments = ap.parse_args()
    print("Command Line Arguments", cl_arguments)

    network_config = ConfigParser()
    network_config.read(ApplicationContext().get_resource('config/networking.ini'))
    system_config = ConfigParser()
    system_config.read(ApplicationContext().get_resource('config/system.ini'))

    main_server_port = network_config['main_server']['port']
    clipboard_port = network_config['clipboard_server']['port']
    clipboard_main_server_address = network_config['clipboard_server']['main_server_address']
    if cl_arguments.clipserverhost is not None:
        clipboard_main_server_address = cl_arguments.clipserverhost

    clipboard_domain = network_config['clipboard_server']['domain']
    clipboard_is_syncing = network_config['clipboard_server']['is_syncing']

    Context.ctx = ApplicationContext()       # 1. Instantiate ApplicationContext

    if cl_arguments.noclipserver is not True:
        if system_config['system'].getboolean('is_instantiating_main_server'):
            print(system_config['system']['is_instantiating_main_server'])
            server = ClipServer(sys.argv, main_server_port)
            server.main()
            # TODO: quite messy way of waiting for the server to finish starting, but it should do the trick for now
            time.sleep(1)
    else:
        if cl_arguments.clipserverhost is None:
            print("X² System: No clipserver was defined, please define parameter:  -cshost")
            sys.exit(1)

    if cl_arguments.noclipboardserver is not True:
        if system_config['system'].getboolean('is_instantiating_clipboard_server'):
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

