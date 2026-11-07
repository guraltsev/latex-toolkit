r"""Run the ``mdt_sentence_per_line`` command with the Python interpreter that starts this script.

Python puts this script's folder first on the import path, so ``latex_toolkit``
loads from here whether or not that interpreter has it installed. Paths given to
the command stay relative to the caller's working folder.
"""

from latex_toolkit.mdt_sentence_per_line.mdt_sentence_per_line import main

raise SystemExit(main())
