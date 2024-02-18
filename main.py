if __name__ == '__main__':
    from manager import Manager
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("--configuration", type = str, default = "./config/default.json", help = "Configuration file")
    args = parser.parse_args()

    with open(args.configuration) as f:
        configuration = json.load(f)

    m = Manager(configuration)

