r"""Run the ``mdt_brace_args`` command with the Python interpreter that starts this script.

Python puts this script's folder first on the import path, so ``latex_toolkit``
loads from here whether or not that interpreter has it installed. Paths given to
the command stay relative to the caller's working folder.
"""

from latex_toolkit.mdt_brace_args.mdt_brace_args import main

raise SystemExit(main())
