"""
Main script to run the application, contains user interface.

Authors: Giulio Foletto.
License: See project-level license file.
"""

import argparse
import json
import logging
from pathlib import Path

from rethebes.analysis import analysis, compare
from rethebes.main import (
    default_configuration,
    get_default_config_directory,
    get_default_output_directory,
    main,
)
from rethebes.util import configure_logging


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode", type=str, help="Mode of operation [run|analyze|compare]"
    )
    parser.add_argument(
        "files",
        type=str,
        nargs="*",
        help="Configuration file for run or data file for analyze",
    )
    args = parser.parse_args()

    # Called here (although its called also in __main__)
    # so that even if cli() is called directly, the logging works properly
    configure_logging()

    if args.mode == "run":
        if len(args.files) == 0:
            configuration = default_configuration
        elif len(args.files) == 1:
            candidates = [
                Path(args.files[0]).resolve(),
                get_default_config_directory() / args.files[0],
                get_default_config_directory() / (args.files[0] + ".json"),
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
        else:
            logging.critical("Run mode currently supports only one configuration file")
            return
        main(configuration)
    elif args.mode == "analyze":
        if len(args.files) == 0:
            logging.critical("No file to analyze")
            return
        elif len(args.files) > 1:
            logging.critical(
                "Analyze mode currently supports only one file. Use compare mode for multiple files"
            )
            return
        candidates = [
            Path(args.files[0]).resolve(),
            get_default_output_directory() / args.files[0],
            get_default_output_directory() / (args.files[0] + ".csv"),
        ]
        analysis_file_found = False
        for path in candidates:
            if path.exists():
                analysis_file_found = True
                break
        if not analysis_file_found:
            logging.critical("File to analyze " + args.files[0] + " not found")
            return
        analysis(path)
    elif args.mode == "compare":
        if len(args.files) == 0:
            logging.critical("No files to compare")
            return
        elif len(args.files) == 1:
            logging.critical(
                "Compare mode requires at least two files. Use analyze mode for one file"
            )
            return
        files = []
        for file in args.files:
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
                logging.critical("File to compare " + file + " not found")
                return
        compare(files)
    else:
        logging.critical("Invalid mode. Supported modes: run, analyze, compare")


if __name__ == "__main__":
    cli()
