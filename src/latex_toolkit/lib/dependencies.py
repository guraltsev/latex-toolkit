"""This module loads configured Python modules and executables for command runtimes."""

from __future__ import annotations

import importlib
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType


class DependencyManager:
    """Load configured runtime dependencies, installing a missing distribution.

    Parameters
    ----------
    distributions : dict[str, str]
        Mapping from import or executable names to their install requirements.

    Methods
    -------
    require
        Import one configured Python module.
    require_executable
        Locate one configured executable.
    """

    def __init__(self, distributions: dict[str, str]) -> None:
        self._distributions = dict(distributions)

    def require(self, import_name: str) -> ModuleType:
        """Import a configured module, installing its distribution if absent.

        Parameters
        ----------
        import_name : str
            Configured import name whose module should be loaded.

        Returns
        -------
        types.ModuleType
            The imported module.

        Raises
        ------
        KeyError
            The import name has no configured distribution.
        ModuleNotFoundError
            The configured distribution remains unavailable after installation.
        """
        requirement = self._distributions[import_name]
        try:
            return importlib.import_module(import_name)
        except ModuleNotFoundError as error:
            missing_requested_path = error.name == import_name or import_name.startswith(
                f"{error.name}."
            )
            if not missing_requested_path:
                raise

        self._install(requirement)
        importlib.invalidate_caches()
        package_name = import_name.partition(".")[0]
        for module_name in tuple(sys.modules):
            if module_name == package_name or module_name.startswith(f"{package_name}."):
                sys.modules.pop(module_name, None)
        return importlib.import_module(import_name)

    def require_executable(self, executable_name: str) -> Path:
        """Locate a configured executable, installing its distribution if absent.

        Parameters
        ----------
        executable_name : str
            Configured executable name to locate on ``PATH`` or beside Python.

        Returns
        -------
        pathlib.Path
            Path to the available executable.

        Raises
        ------
        KeyError
            The executable name has no configured distribution.
        RuntimeError
            The executable is unavailable after its distribution is installed.
        """
        requirement = self._distributions[executable_name]
        located = self._find_executable(executable_name)
        if located is None:
            self._install(requirement)
            located = self._find_executable(executable_name)
        if located is None:
            raise RuntimeError(
                f"{executable_name} is unavailable after installing {requirement}"
            )
        return located

    @staticmethod
    def _install(requirement: str) -> None:
        """Install one configured requirement into the active Python environment."""
        subprocess.check_call([sys.executable, "-m", "pip", "install", requirement])

    @staticmethod
    def _find_executable(executable_name: str) -> Path | None:
        """Return an executable available on PATH or beside the interpreter."""
        located = shutil.which(executable_name)
        if located:
            return Path(located)
        for candidate in (
            Path(sys.executable).with_name(f"{executable_name}.exe"),
            Path(sys.executable).parent / "Scripts" / f"{executable_name}.exe",
        ):
            if candidate.is_file():
                return candidate
        return None
