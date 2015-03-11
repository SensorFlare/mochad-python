import logging
import sys


def log_config():
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    root.addHandler(ch)

    fh = logging.FileHandler('mochad_python.log')
    fh.setFormatter(formatter)
    root.addHandler(fh)
