@echo off
set "PYTHONPATH=%~dp0;%PYTHONPATH%"
python -m latex_toolkit.greek_latex2unicode %*
exit /b %errorlevel%
