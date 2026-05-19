@echo off

:loop

cd /d D:\UploadSite

"C:\Users\PCKK0001\AppData\Local\Python\bin\pythonw.exe" appYPB.py

timeout /t 5

goto loop