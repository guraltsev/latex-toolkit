@echo off
setlocal
set "PYTHON=%~dp0..\.venv\Scripts\python.exe"
if not exist "%PYTHON%" set "PYTHON=python"
set "PYTHONPATH=%~dp0;%PYTHONPATH%"
"%PYTHON%" -m latex_toolkit.math_latex2dollar %*
exit /b %errorlevel%
