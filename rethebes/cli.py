"""
Main script to run the application, contains user interface.

Authors: Giulio Foletto.
License: See project-level license file.
"""

import argparse
import json
import logging
import os

from rethebes.analysis import analysis
from rethebes.main import (
    default_configuration,
    get_default_config_directory,
    get_default_output_directory,
    main,
)
from rethebes.util import configure_logging


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", type=str, help="Mode of operation [run|analyze]")
    parser.add_argument(
        "file",
        type=str,
        nargs="?",
        default="",
        help="Configuration file for run or data file for analyze",
    )
    args = parser.parse_args()

    # Called here (although its called also in __main__)
    # so that even if cli() is called directly, the logging works properly
    configure_logging()

    if args.mode == "run":
        if args.file == "":
            configuration = default_configuration
        else:
            candidates = [
                os.path.normpath(args.file),
                os.path.join(get_default_config_directory(), args.file),
                os.path.join(get_default_config_directory(), args.file + ".json"),
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
                logging.critical("Config file not found")
                return
        main(configuration)
    elif args.mode == "analyze":
        candidates = [
            os.path.normpath(args.file),
            os.path.join(get_default_output_directory(), args.file),
            os.path.join(get_default_output_directory(), args.file + ".csv"),
        ]
        analysis_file_found = False
        for path in candidates:
            if os.path.exists(path):
                analysis_file_found = True
                break
        if not analysis_file_found:
            logging.critical("File to analyze not found")
            return
        analysis(path)


if __name__ == "__main__":
    cli()
