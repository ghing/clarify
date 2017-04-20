import argparse

from clarify.cli.results import add_parser as results_add_parser
from clarify.cli.jurisdictions import add_parser as jurisdictions_add_parser


def main():
    parser = argparse.ArgumentParser(prog='clarify')
    subparsers = parser.add_subparsers(help="sub-command help")
    results_add_parser(subparsers)
    jurisdictions_add_parser(subparsers)
    args = parser.parse_args()
    args.func(args)
