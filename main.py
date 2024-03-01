"""
Main script to run the application.

Authors: Giulio Foletto.
"""

# Encapsulation in condition is necessary because otherwise subprocess might re-execute this module.
if __name__ == '__main__':
    import argparse
    import json
    import logging
    import sys
    from manager import Manager, default_configuration
    from analyzer import Analyzer
    
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", type = str, help = "Mode of operation [run|analyze]")
    parser.add_argument("file", type = str, nargs = "?", default = "", help = "Configuration file for run or data file for analyze")
    args = parser.parse_args()

    logging.basicConfig(stream = sys.stdout,
                        level = logging.INFO,
                        format = "[%(asctime)s] %(levelname)s - %(message)s",
                        datefmt="%Y-%m-%dT%H:%M:%S") # Note that time (and hence default logger) does not support %f

    if args.mode == "run":
        try:
            with open(args.file) as f:
                configuration = json.load(f)
        except:
            configuration = default_configuration

        m = Manager(configuration)
    elif args.mode == "analyze":
        a = Analyzer(args.file)

