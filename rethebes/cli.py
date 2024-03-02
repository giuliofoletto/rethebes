"""
Main script to run the application.

Authors: Giulio Foletto.
"""

# Encapsulation in condition is necessary because otherwise subprocess might re-execute this module.
def cli():
    import os
    import argparse
    import json
    import logging
    from rethebes.analyzer import Analyzer
    from rethebes.util import configure_logging
    from rethebes.logic import main, default_configuration, get_default_config_directory
    
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", type = str, help = "Mode of operation [run|analyze]")
    parser.add_argument("file", type = str, nargs = "?", default = "", help = "Configuration file for run or data file for analyze")
    args = parser.parse_args()

    configure_logging()

    if args.mode == "run":
        if args.file == "":
            configuration = default_configuration
        else:
            candidates = [
                os.path.normpath(args.file),
                os.path.join(get_default_config_directory(), args.file),
                os.path.join(get_default_config_directory(), args.file + ".json")
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
        a = Analyzer(args.file)

if __name__ == '__main__':
    cli()