'''A python script to enumerate information about a windows host.

  If trying to store the output in a file, it may be necessary to 
  set the PYTHONIOENCODING environment varible to utf16 prior to 
  running the script. This is only necessary if encountering a 
  UnicodeEncodeError exception. This can be done like so:
  
    cmd> set PYTHONIOENCODING=utf16
    cmd> python enumhost.py > output.txt

  Requires packages: columnar, xmltodict

  Only tested on Windows 10, so it may potentially break on older OSes.
  
  Author: Shanief Webb (https://github.com/slw07g)
'''

import os, sys, argparse
import datetime

import columnar
import traceback
import xmltodict

import platforms


def on_windows():
    return sys.platform.lower() == 'win32'


def on_mac():
    return sys.platform.lower() == 'darwin'


def on_linux():
    return sys.platform == 'linux'


def main():
    if on_windows():
        from platforms import windows as platformenum
    if on_mac():
        from platforms import macos as platformenum
    if on_linux():
        from platforms import nix as platformenum

    args = platformenum.get_args()
    platformenum.main(args)


if __name__ == '__main__':
    main()
