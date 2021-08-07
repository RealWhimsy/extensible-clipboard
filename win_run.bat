@echo off
cd clip_server
START /B win_run.bat
cd ..\clipboard_bridge
call win_run.bat
cd ..
