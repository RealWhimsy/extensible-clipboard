@echo off
cd clipserver
START /B win_run.bat
cd ..\clipboard
call win_run.bat
cd ..
