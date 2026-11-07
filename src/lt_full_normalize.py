r"""Run the ``full_normalize`` command with the Python interpreter that starts this script.

Python puts this script's folder first on the import path, so ``latex_toolkit``
loads from here whether or not that interpreter has it installed. Paths given to
the command stay relative to the caller's working folder.
"""

from latex_toolkit.full_normalize.full_normalize import main

raise SystemExit(main())
