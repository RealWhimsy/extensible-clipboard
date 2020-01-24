

# most portions of the code were taken from https://github.com/mherrmann/fbs-tutorial

# 1. create virtual environment
python -m venv venv

# 2. activate virtual environment
source venv/bin/activate # mac/linux code
# call venv\scripts\activate.bat # windows code

# 3. install current pyqt version
pip install fbs PyQt5==5.9.2

# 4. init project
fbs startproject
