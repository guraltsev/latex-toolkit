# snapper-fmt Runtime

This directory is the repository-local install prefix for the external
`snapper-fmt` dependency used by `latex_toolkit.commands.snapper_format`.

The command installs or refreshes the runtime here with `pip --prefix`. The
installed files are intentionally ignored so ad-hoc dependency artifacts are
not committed to the repository.
