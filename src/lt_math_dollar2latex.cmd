@echo off
set "PYTHONPATH=%~dp0;%PYTHONPATH%"
python -m latex_toolkit.dollar_math_to_latex_delimiters %*
