@echo off
set "PYTHONPATH=%~dp0;%PYTHONPATH%"
python -m latex_toolkit.latex_transformer_template %*
