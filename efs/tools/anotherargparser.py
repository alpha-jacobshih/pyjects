"""
anotherargparser.py: another argument parser extended from ArgumentParser
"""
import sys
import argparse


class AnotherArgumentParser(argparse.ArgumentParser):
    """
    AnotherArgumentParser is subclassed from argparse.ArgumentParser and
    overrides the method error() to print a customized message while the
    command line arguments are parsed error. it prints the error and show
    the command line help if error occurs.
    """

    def error(self, message):
        sys.stderr.write('ERROR: %s\n\n' % message)
        self.print_help()
        sys.exit(2)
