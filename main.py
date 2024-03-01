"""
Main script to run the application.

Authors: Giulio Foletto.
"""

# Encapsulation in condition is necessary because otherwise subprocess might re-execute this module.
if __name__ == '__main__':
    import argparse
    import json
    from manager import default_configuration
    from analyzer import Analyzer
    from util import configure_logging
    from logic import main
    
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", type = str, help = "Mode of operation [run|analyze]")
    parser.add_argument("file", type = str, nargs = "?", default = "", help = "Configuration file for run or data file for analyze")
    args = parser.parse_args()

    configure_logging()

    if args.mode == "run":
        try:
            with open(args.file) as f:
                configuration = json.load(f)
        except:
            configuration = default_configuration

        #m = Manager(configuration)
        configuration = main(configuration)
    elif args.mode == "analyze":
        a = Analyzer(args.file)

