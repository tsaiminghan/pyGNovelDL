@ECHO off

cd /d %~dp0
pyinstaller commandline.py -F --clean -c --hidden-import=pkg_resources --upx-exclude=vcruntime140.dll --upx-exclude=ucrtbase.dll
pyinstaller window.py -F --clean -w --hidden-import=pkg_resources --upx-exclude=vcruntime140.dll --upx-exclude=ucrtbase.dll


