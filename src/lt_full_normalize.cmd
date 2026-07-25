@echo off
set "PYTHONPATH=%~dp0;%PYTHONPATH%"
python -m latex_toolkit.full_normalize %*
exit /b %errorlevel%
