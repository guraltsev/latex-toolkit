@echo off
set "PYTHONPATH=%~dp0;%PYTHONPATH%"
python -m latex_toolkit.latex_delimiters_to_dollar_math %*
