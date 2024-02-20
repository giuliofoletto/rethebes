if __name__ == "__main__":
    import argparse
    from analyzer import Analyzer

    parser = argparse.ArgumentParser()
    parser.add_argument("file_name")
    args = parser.parse_args()

    Analyzer(args.file_name)