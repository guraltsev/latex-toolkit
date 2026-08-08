@echo off
set "PYTHONPATH=%~dp0;%PYTHONPATH%"
python -m latex_toolkit.mdt_brace_args %*
exit /b %errorlevel%
