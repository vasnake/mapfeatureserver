@rem -*- mode: bat; coding: cp1251 -*-

@echo off
chcp 1251 > nul
set wd=%~dp0
pushd "%wd%"

set path=c:\d\Python27;%path%

pushd c:\d\code\git\mapfeatureserver\wsgi
start python.exe -u mapfs_controller.py

popd
exit
