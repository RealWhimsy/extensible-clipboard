# Enhanced Clipboard C<sup>2</sup>

## Installation and Execution

### General Requirements
Tested with Python 3.6.6\
Mongodb needs to be running. The connection can be configured in `src/server/config.ini`\
The necessary database will be created automatically.\
For the extensions a Chromium-based webbrowser and LibreOffice are needed.
Install the required dependencies for all parts with `pip install -r requirements.txt` or install only the ones needed for a specific part as stated below.

### Structure
The whole project consists of five distinct programs: The Clip-Server, Webhooks, Clipboard-Server, a Chrome-Plugin and and a LibreOffice Writer plugin.\

#### Clip-Server
This is the server that enables the communication between all the other parts, it needs to be running at all times or many of the other components will refuse to start. It depends on three major packages each with their own dependencies: *Flask*, *pymongo* and *requests*, please make sure those are installed on your system or virtual environment. To start the server, `src/server/main.py` needs to be called. By default it runs on port 5000, to change the port, you can add a command line argument. To run the server on port 12345 for example the command would be `python PATH/TO/PROJECT/src/server/main.py 12345`

#### Clipboard-Server
This program provides to supervise and change the contents of the current device's clipboard. It can be run in two modes: it can either just listen to incoming connections from the Clip-Server and put the data into the OS's clipboard or it can supervise said clipboard and send data put into it to the server. The communication with the clipboard is implemented via QT so your system needs to be able to run that. In addition, the QT-Documentation for QCliboard states that detecting new data will not work properly on macOS-devices.\
To run this program, *Flask*, *PyQT5* and *requests* are needed, please make sure those are installed on your system or virtual environment. To start the Clipboard-Server one needs to provide several commandline-arguments to configure the connections correctly; running `python PATH/TO/PROJECT/src/clipboard_server/main.py -h` will explain them in detail. To give an example for running the application locally on port 5555 and monitoring the OS-clipboard with Clip-Server already running on port 5000 use following command: `python PATH/TO/PROJECT/src/clipboard_server/main.py --port 5555 --domain http://localhost:5555/ --clipserver http://localhost:5000/ --sync-clipboard True`. If clipserver cannot be reached, the program will exit and print an appropriate error.

#### Webhooks
Webhooks are designed to register themselves to the Clip-Server and be notified when new data was saved there. It depends on following packages: *Flask* and *requests*, please make sure those are installed on your system or virtual environment. The webhook shares most of the command-line interface with the Clipboard-Server with only the `sync-clipboard` option removed. Detailed explanaition can be requested by calling `python PATH/TO/PROJECT/src/webhooks/main.py -h`. A similar example to the clipboard-server above, running on port 6000 would be `python src/webhooks/main.py -p 6000 -d http://localhost:6000/ -c http://localhost:5000/`.

#### Chrome Plugin
The extension should work for any reasonably new webbrowser based on the Chromium enging. It was developed and tested with Vivaldi 2.3. To install it, simply go to the extensions-page `chrome://extensions/`, activate "Developer mode" and click on "Load unpacked". In the pop-up, select the directory `PATH/TO/PROJECT/src/chrome-plugin`. Use the options-page of the extension (right-click on the icon for example) to specify the URL of your running Clip-Server

#### LibreOffice Writer Plugin
The extension was written for LibreOffice 6.0.7.3. To install it, open the Extension Manager of LibreOffice, click "Add" and then select the file `PATH/TO/PROJECT/src/writer-plugin/???`

#### Testing
To ensure the basic functionality of the Clip-Server a bunch of tests are included, located under `PATH/TO/PROJECT/src/tests`. These tests ensure most of the outward-facing API used by the server is correct but currently does not account for every single possible variation. To run those tests enter `python -m unittest discover PATH/TO/PROJECT/tests`.
