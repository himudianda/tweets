from argparse import ArgumentParser
from web import init_parser

__all__ = ['parser']

parser = ArgumentParser()
subparser = parser.add_subparsers()
init_parser(subparser)


def main():
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
