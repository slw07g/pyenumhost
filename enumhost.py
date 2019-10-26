import os, sys, argparse
from utils.reg import Reg


def on_windows():
    return sys.platform.lower() == 'win32'


def on_mac():
    return sys.platform.lower() == 'darwin'


def on_linux():
    return sys.platform == 'linux'


def enum_windows():
    regkeys = []


def main():
    pass


if __name__ == '__main__':
    main()
