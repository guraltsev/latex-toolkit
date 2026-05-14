@echo off
setlocal

set "TOOLKIT_ROOT=%~dp0"
if "%PYTHONPATH%"=="" (
    set "PYTHONPATH=%TOOLKIT_ROOT%src"
) else (
    set "PYTHONPATH=%TOOLKIT_ROOT%src;%PYTHONPATH%"
)

>&2 echo latex-toolkit: starting TeXmacs clipboard conversion.

python --version >nul 2>&1
if errorlevel 1 (
    >&2 echo latex-toolkit: Python could not be started from cmd.exe.
    >&2 echo latex-toolkit: Run "python --version" in Command Prompt and fix PATH or the Windows Python app alias.
    exit /b 1
)

call :run dollar2bracket
if errorlevel 1 exit /b %ERRORLEVEL%

call :run ltae2aligned
if errorlevel 1 exit /b %ERRORLEVEL%

call :run tmscript2substack
if errorlevel 1 exit /b %ERRORLEVEL%

call :run proofstar2proof
if errorlevel 1 exit /b %ERRORLEVEL%

call :run uni2tex
if errorlevel 1 exit /b %ERRORLEVEL%

>&2 echo latex-toolkit: clipboard conversion finished.
exit /b 0

:run
set "COMMAND_NAME=%~1"
>&2 echo latex-toolkit: running %COMMAND_NAME%...
python -m latex-toolkit.commands.%COMMAND_NAME% --clipboard
set "STATUS=%ERRORLEVEL%"
if not "%STATUS%"=="0" (
    >&2 echo latex-toolkit: %COMMAND_NAME% failed with exit code %STATUS%.
    >&2 echo latex-toolkit: clipboard conversion stopped before later steps.
    exit /b %STATUS%
)
>&2 echo latex-toolkit: %COMMAND_NAME% finished.
exit /b 0
