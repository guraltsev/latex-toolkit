r"""Run the ``greek_latex2unicode`` command with the Python interpreter that starts this script.

Python puts this script's folder first on the import path, so ``latex_toolkit``
loads from here whether or not that interpreter has it installed. Paths given to
the command stay relative to the caller's working folder.
"""

from latex_toolkit.greek_latex2unicode.greek_latex2unicode import main

raise SystemExit(main())
