"""
Shared utility functions.

Authors: Giulio Foletto.
License: See project-level license file.
"""

import logging
import sys
from pathlib import Path


def configure_logging():
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s - %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )  # Note that time (and hence default logger) does not support %f


def get_default_global_directory(create=False):
    user_dir = Path.home()
    rethebes_dir = user_dir / ".rethebes"
    if create and not rethebes_dir.exists():
        rethebes_dir.mkdir()
    return rethebes_dir


def get_default_output_directory(create=False):
    rethebes_dir = get_default_global_directory()
    output_dir = rethebes_dir / "output"
    if create and not output_dir.exists():
        output_dir.mkdir()
    return output_dir


def get_default_config_directory(create=False):
    rethebes_dir = get_default_global_directory()
    config_dir = rethebes_dir / "config"
    if create and not config_dir.exists():
        config_dir.mkdir()
    return config_dir
