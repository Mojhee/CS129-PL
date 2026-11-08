@echo off
REM Build the PE03 executable (Task 4). Run from the PE03 folder on Windows.
REM PyInstaller is needed only on the build computer; the program never imports it.

python -m pip install --upgrade pyinstaller || goto :error
if exist stubs.py echo WARNING: stubs.py is still in the folder. Delete it before building the submission.

python -m PyInstaller --onefile --windowed --clean --name PE03_Parser main.py || goto :error

echo.
echo Built dist\PE03_Parser.exe
echo Copy it to another folder with the tests\ files and run scenarios 1-4 there.
goto :eof

:error
echo Build failed.
exit /b 1
