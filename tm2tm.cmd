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


>&2 echo latex-toolkit: starting TeXmacs snippet normalization.

python --version >nul 2>&1
if errorlevel 1 (
    >&2 echo latex-toolkit: Python could not be started from cmd.exe.
    >&2 echo latex-toolkit: Run "python --version" in Command Prompt and fix PATH or the Windows Python app alias.
    exit /b 1
)

call :run tm_alignedt2ltae
if errorlevel 1 exit /b %ERRORLEVEL%

>&2 echo latex-toolkit: TeXmacs snippet normalization finished.
exit /b 0

:run
set "COMMAND_NAME=%~1"
>&2 echo latex-toolkit: running %COMMAND_NAME%...
python -m latex-toolkit.commands.%COMMAND_NAME% --clipboard
set "STATUS=%ERRORLEVEL%"
if not "%STATUS%"=="0" (
    >&2 echo latex-toolkit: %COMMAND_NAME% failed with exit code %STATUS%.
    >&2 echo latex-toolkit: TeXmacs snippet normalization stopped before later steps.
    exit /b %STATUS%
)
>&2 echo latex-toolkit: %COMMAND_NAME% finished.
exit /b 0
