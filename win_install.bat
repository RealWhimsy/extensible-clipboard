@echo off
echo Now installing extensible clipboard dependencies for windows
pip3 install virtualenv

cd clipserver
call win_install.bat

cd ..\clipboard
call win_install.bat
