@echo off
setlocal

set "TOOLKIT_ROOT=%~dp0"
if "%PYTHONPATH%"=="" (
    set "PYTHONPATH=%TOOLKIT_ROOT%src"
) else (
    set "PYTHONPATH=%TOOLKIT_ROOT%src;%PYTHONPATH%"
)

python -m latex-toolkit.commands.ltae2aligned --clipboard
if errorlevel 1 exit /b %ERRORLEVEL%

python -m latex-toolkit.commands.dollar2bracket --clipboard
if errorlevel 1 exit /b %ERRORLEVEL%

python -m latex-toolkit.commands.uni2tex --clipboard
exit /b %ERRORLEVEL%
