@echo off
set "PYTHONPATH=%~dp0;%PYTHONPATH%"
python -m latex_toolkit.mdt_math_latex2dollar %*
exit /b %errorlevel%
