@ECHO off

cd /d %~dp0
python window.py



if %ERRORLEVEL% == 0 GOTO:EOF
pause