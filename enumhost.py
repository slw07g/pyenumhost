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


def map_sid_to_users():
    ret = {}
    for sid in Reg.get_users_keys():
        try:
            profilepath = Reg.get_value(f'HKEY_LOCAL_MACHINE/SOFTWARE/Microsoft\Windows NT/CurrentVersion/ProfileList/{sid}', 'ProfileImagePath')
            profile = os.path.basename(profilepath.value)
        except:
            profile = '<NOT FOUND>'
        finally:
            ret[sid] = profile
    return ret

def check_autoruns():
    keys = ['hklm/software/microsoft/windows/currentversion/run']
    for sid in Reg.get_users_keys():
        keys += [f'hkey_users/{sid}/software/microsoft/windows/currentversion/run']
    
    for key in keys:
        print(f'[{key}]')
        try:
            vals = Reg.get_subkey_values(key)['\\']
        except:
            vals = ['  Access Denied']
        finally:
            for val in vals:
                print(f'  {val}')

def main():
    check_autoruns()
    sidinfo = map_sid_to_users()
    
    print(sidinfo)
    pass


if __name__ == '__main__':
    main()
