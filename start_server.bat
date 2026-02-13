@echo off
REM Quizzer Web Server Launcher for Windows
REM Double-click this file to start the server
REM Or use from command line with options: start_server.bat --test-mode

python start_server.py %*
pause
