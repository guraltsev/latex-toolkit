@echo off
set "PYTHONPATH=%~dp0;%PYTHONPATH%"
python -m latex_toolkit.mdt_greek_unicode2latex %*
exit /b %errorlevel%
