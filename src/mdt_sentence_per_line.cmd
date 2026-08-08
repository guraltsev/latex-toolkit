@echo off
set "PYTHONPATH=%~dp0;%PYTHONPATH%"
python -m latex_toolkit.mdt_sentence_per_line %*
exit /b %errorlevel%
