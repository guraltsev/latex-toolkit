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

>&2 echo latex-toolkit: starting LLM-to-TeXmacs clipboard conversion.

set "MACROS_FILE="
if "%~1"=="--macros-file" (
    if "%~2"=="" (
        >&2 echo latex-toolkit: Usage: %~nx0 [--macros-file ABSOLUTE_TOML_PATH]
        exit /b 2
    )
    set "MACROS_FILE=%~2"
    if not "%~3"=="" (
        >&2 echo latex-toolkit: Usage: %~nx0 [--macros-file ABSOLUTE_TOML_PATH]
        exit /b 2
    )
) else (
    if not "%~1"=="" (
        set "MACROS_FILE=%~1"
        if not "%~2"=="" (
            >&2 echo latex-toolkit: Usage: %~nx0 [--macros-file ABSOLUTE_TOML_PATH]
            exit /b 2
        )
    )
)

python --version >nul 2>&1
if errorlevel 1 (
    >&2 echo latex-toolkit: Python could not be started from cmd.exe.
    >&2 echo latex-toolkit: Run "python --version" in Command Prompt and fix PATH or the Windows Python app alias.
    exit /b 1
)

call :run_brace_unary_macros
if errorlevel 1 exit /b %ERRORLEVEL%

call :run texmacs_vert_delimiters
if errorlevel 1 exit /b %ERRORLEVEL%

call :run proof2proofstar
if errorlevel 1 exit /b %ERRORLEVEL%

>&2 echo latex-toolkit: clipboard conversion finished.
exit /b 0

:run_brace_unary_macros
set "COMMAND_NAME=brace_unary_macros"
>&2 echo latex-toolkit: running %COMMAND_NAME%...
if "%MACROS_FILE%"=="" (
    python -m latex_toolkit.commands.%COMMAND_NAME% --clipboard
) else (
    python -m latex_toolkit.commands.%COMMAND_NAME% --clipboard --macros-file "%MACROS_FILE%"
)
set "STATUS=%ERRORLEVEL%"
if not "%STATUS%"=="0" (
    >&2 echo latex-toolkit: %COMMAND_NAME% failed with exit code %STATUS%.
    >&2 echo latex-toolkit: clipboard conversion stopped before later steps.
    exit /b %STATUS%
)
>&2 echo latex-toolkit: %COMMAND_NAME% finished.
exit /b 0

:run
set "COMMAND_NAME=%~1"
>&2 echo latex-toolkit: running %COMMAND_NAME%...
python -m latex_toolkit.commands.%COMMAND_NAME% --clipboard
set "STATUS=%ERRORLEVEL%"
if not "%STATUS%"=="0" (
    >&2 echo latex-toolkit: %COMMAND_NAME% failed with exit code %STATUS%.
    >&2 echo latex-toolkit: clipboard conversion stopped before later steps.
    exit /b %STATUS%
)
>&2 echo latex-toolkit: %COMMAND_NAME% finished.
exit /b 0
