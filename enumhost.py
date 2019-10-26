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

def check_autoruns():
    keys = ['hklm/software/microsoft/windows/currentversion/run']
    for sid in Reg.list_subkeys('hkey_users/'):
        if sid.lower().endswith('_classes'):
            continue
        keys += [f'hkey_users/{sid}/software/microsoft/windows/currentversion/run']
    
    for key in keys:
        print(f'[{key}]')
        try:
            print((Reg.get_subkey_values(Reg.open_key(key))))
        except:
            print('  Access Denied')

def main():
    check_autoruns()
    pass


if __name__ == '__main__':
    main()
