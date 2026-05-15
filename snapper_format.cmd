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

python --version >nul 2>&1
if errorlevel 1 (
    >&2 echo latex-toolkit: Python could not be started from cmd.exe.
    >&2 echo latex-toolkit: Run "python --version" in Command Prompt and fix PATH or the Windows Python app alias.
    exit /b 1
)

python -m latex_toolkit.commands.snapper_format %*
exit /b %ERRORLEVEL%
