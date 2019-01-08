# Enhanced Clipboard

## Installation and Execution
Tested with Python 3.6.6
**Requires Mongodb 4.0 running**
Install the required dependencies with `pip install -r requirements.txt`
To run the server, execute in the projects root directory `python src/server/main.py`. This is the Flask development server and will run on port 5000. The server can be stopped with CTRL-C
The cofiguration of the database can be adjusted in config.ini

### Usage of hooks
All hooks get called whenever new data is pushed to the server. To add a custom hook, you need to add a file ending in \_hook.py into the folder _src/server/hooks_.
The file needs to contain a class which inherits from `BaseHook` and implements the abstract method `do_work`. The the documentation of `BaseHook` for details.
