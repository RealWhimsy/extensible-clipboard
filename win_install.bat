@echo off
echo Now installing extensible clipboard dependencies for windows
pip3 install virtualenv

cd clip_server
call win_install.bat

cd ..\clipboard_bridge
call win_install.bat
