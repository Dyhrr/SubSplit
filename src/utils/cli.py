"""
Command-line entrypoint: parse args, call process_file or launch GUI
"""
import argparse
from transcribe import process_file
from gui import TranscriberGUI

def main():
    parser = argparse.ArgumentParser()
    # TODO: add --cli, --out, --verbose flags
    args = parser.parse_args()
    # TODO: dispatch to CLI or GUI
    pass

if __name__ == '__main__':
    main()
