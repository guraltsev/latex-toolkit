@echo off
set "PYTHONPATH=%~dp0;%PYTHONPATH%"
python -m latex_toolkit.mdt_math_dollar2latex %*
exit /b %errorlevel%
