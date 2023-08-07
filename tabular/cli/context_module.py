"""Functionality for TaCL's --context-module flag."""

import importlib.util
import os
import pathlib
import sys

from types import ModuleType
from typing import Any, Mapping


def load_module(file: os.PathLike, module_name: str | None = None) -> ModuleType:
    """Register and load a module from a pathlike object.

    See https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly.
    """
    file = pathlib.Path(file)
    module_name = (
        module_name
        if module_name is not None
        else file.stem
    )

    spec = importlib.util.spec_from_file_location(module_name, file)
    module = importlib.util.module_from_spec(spec)

    # register and load the module
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module


def get_namespace_mapping(module: ModuleType) -> Mapping[str, Any]:
    """Get a module mapping containing only public symbols."""
    namespace = {
        key: value for key, value
        in sys.modules[module.__name__].__dict__.items()
        if not key.startswith("_")
    }

    return namespace
