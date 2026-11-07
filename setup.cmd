@echo off
rem Create .venv from the python on PATH and install the toolkit into it.
rem Uses uv when available, otherwise the standard venv and pip modules.
setlocal
set "ROOT=%~dp0"
set "VENV=%ROOT%.venv"

rem Resolve the real interpreter behind the python on PATH.
set "BASE_PYTHON="
for /f "delims=" %%P in ('python -c "import sys; print(sys._base_executable)" 2^>nul') do set "BASE_PYTHON=%%P"
if not defined BASE_PYTHON (
    echo error: no working python found on PATH. 1>&2
    exit /b 1
)
echo Using base interpreter: %BASE_PYTHON%

where uv >nul 2>nul
if %errorlevel%==0 (
    echo Creating %VENV% with uv
    uv venv --clear --python "%BASE_PYTHON%" "%VENV%" || exit /b 1
    uv pip install --python "%VENV%\Scripts\python.exe" --editable "%ROOT%." || exit /b 1
) else (
    echo uv not found; creating %VENV% with venv and pip
    "%BASE_PYTHON%" -m venv --clear "%VENV%" || exit /b 1
    "%VENV%\Scripts\python.exe" -m pip install --upgrade pip || exit /b 1
    "%VENV%\Scripts\python.exe" -m pip install --editable "%ROOT%." || exit /b 1
)

echo Done. Commands in src\ now run with %VENV%\Scripts\python.exe
exit /b 0
