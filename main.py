"""
Main script to run the application.

Authors: Giulio Foletto.
"""

# Encapsulation in condition is necessary because otherwise subprocess might re-execute this module.
if __name__ == '__main__':
    import argparse
    import json
    from manager import Manager, default_configuration
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configuration", type = str, default = "", help = "Configuration file")
    args = parser.parse_args()

    try:
        with open(args.configuration) as f:
            configuration = json.load(f)
    except:
        configuration = default_configuration

    m = Manager(configuration)

