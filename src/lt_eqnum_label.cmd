@echo off
set "PYTHONPATH=%~dp0;%PYTHONPATH%"
python -m latex_toolkit.eqnum_label %*
exit /b %errorlevel%
