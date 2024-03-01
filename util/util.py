import sys
import logging

def configure_logging():
    logging.basicConfig(stream = sys.stdout,
                        level = logging.INFO,
                        format = "[%(asctime)s] %(levelname)s - %(message)s",
                        datefmt="%Y-%m-%dT%H:%M:%S") # Note that time (and hence default logger) does not support %f