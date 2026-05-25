@echo off
setlocal

set "TOOLKIT_ROOT=%~dp0"
if "%PYTHONPATH%"=="" (
    set "PYTHONPATH=%TOOLKIT_ROOT%src"
) else (
    set "PYTHONPATH=%TOOLKIT_ROOT%src;%PYTHONPATH%"
)
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

python -m latex_toolkit.commands.texmacs_latex_to_latex %*
exit /b %ERRORLEVEL%
