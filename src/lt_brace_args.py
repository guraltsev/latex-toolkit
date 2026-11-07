r"""Run the ``brace_args`` command with the Python interpreter that starts this script.

Python puts this script's folder first on the import path, so ``latex_toolkit``
loads from here whether or not that interpreter has it installed. Paths given to
the command stay relative to the caller's working folder.
"""

from latex_toolkit.brace_args.brace_args import main

raise SystemExit(main())
