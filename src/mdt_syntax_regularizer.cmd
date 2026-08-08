@echo off
set "PYTHONPATH=%~dp0;%PYTHONPATH%"
python -m latex_toolkit.mdt_syntax_regularizer %*
exit /b %errorlevel%
