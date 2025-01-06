"""
Main script to run the application, contains user interface.

Authors: Giulio Foletto.
License: See project-level license file.
"""

import json
import logging
from pathlib import Path

import click

from rethebes.analysis import analysis, compare
from rethebes.run import (
    default_configuration,
    get_default_config_directory,
    get_default_output_directory,
    run,
)
from rethebes.util import configure_logging


@click.group()
def cli():
    configure_logging()


@cli.command(name="run")
@click.argument("config_file", type=click.Path(), required=False)
def run_command(config_file):
    """Run measurement according to CONFIG_FILE."""
    if config_file is None:
        configuration = default_configuration
    else:
        candidates = [
            Path(config_file).resolve(),
            get_default_config_directory() / config_file,
            get_default_config_directory() / (config_file + ".json"),
        ]
        config_found = False
        for path in candidates:
            try:
                with open(path) as f:
                    configuration = json.load(f)
                config_found = True
                break
            except:
                pass
        if not config_found:
            logging.critical("Config file " + str(config_file) + " not found")
            return
    run(configuration)


@cli.command(name="analyze")
@click.argument("data_file", type=click.Path())
def analyze_command(data_file):
    """Analyze DATA_FILE."""
    candidates = [
        Path(data_file).resolve(),
        get_default_output_directory() / data_file,
        get_default_output_directory() / (data_file + ".csv"),
    ]
    analysis_file_found = False
    for path in candidates:
        if path.exists():
            analysis_file_found = True
            break
    if not analysis_file_found:
        logging.critical("File to analyze " + str(data_file) + " not found")
        return
    analysis(path)


@cli.command(name="compare")
@click.argument("data_files", type=click.Path(), nargs=-1)
def compare_command(data_files):
    """Compare DATA_FILES."""
    if len(data_files) == 0:
        logging.critical("No files to compare")
        return
    elif len(data_files) == 1:
        logging.critical(
            "Compare mode requires at least two files. Use analyze mode for one file"
        )
        return
    files = []
    for file in data_files:
        candidates = [
            Path(file).resolve(),
            get_default_output_directory() / file,
            get_default_output_directory() / (file + ".csv"),
        ]
        analysis_file_found = False
        for path in candidates:
            if path.exists():
                analysis_file_found = True
                files.append(path)
                break
        if not analysis_file_found:
            logging.critical("File to compare " + str(file) + " not found")
            return
    compare(files)


if __name__ == "__main__":
    cli()
