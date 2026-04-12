"""Command discovery package for lt-cli.

The command directories intentionally keep filesystem names such as
``expand-includes`` rather than Python package names. The thin dispatcher loads
``main.py`` directly from the selected command directory.
"""
