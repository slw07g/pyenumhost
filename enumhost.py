import os, sys, argparse
from utils.reg import Reg
import traceback


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
    builtins = { 'S-1-5-18': 'SYSTEM',
    'S-1-5-19': 'LocalService',
    'S-1-5-20': 'NetworkService'}
    for sid in Reg.get_users_keys():
        try:
            if sid in builtins:
                profile = builtins[sid]
            else:
                profilepath = Reg.get_value(f'HKEY_LOCAL_MACHINE/SOFTWARE/Microsoft\Windows NT/CurrentVersion/ProfileList/{sid}', 'ProfileImagePath')
                profile = os.path.basename(profilepath.value)
            
        except:
            profile = '<NOT FOUND>'
        finally:
            ret[sid] = profile
    return ret

def enum_autoruns():
    keys = {'hklm/software/microsoft/windows/currentversion/run': 'GLOBAL (HKLM)',
    'hklm/software/microsoft/windows/currentversion/runonce': 'GLOBAL (HKLM)'}
    users = map_sid_to_users()
    for sid in Reg.get_users_keys():
        keys[f'hkey_users/{sid}/software/microsoft/windows/currentversion/run'] = users[sid]
        keys[f'hkey_users/{sid}/software/microsoft/windows/currentversion/runonce'] = users[sid]
        
    
    for key in keys.keys():
        print(f'{keys[key]} ({key})')
        try:
            vals = Reg.get_subkey_values(key)['\\']
        except:
            vals = ['  Access Denied or Key does not exist']
        finally:
            for val in vals:
                print(f'  {val}')
        print('\n\n')

def enum_users():
    users = map_sid_to_users()
    ret = []
    for sid in users.keys():
        ret.append(users[sid])
    print(ret)
    return ret

def enum_services():     
    class Service:
        def __init__(self, name, displayname, svctype, start, path, user='LocalSystem', servicedll='N/A'):
            startopts = {0: 'BOOT', 
                         1: 'SYSTEM', 
                         2: 'AUTOLOAD', 
                         3: 'MANUAL', 
                         4: 'DISABLED'}
            typeopts = {1: 'Kernel Driver', 
                        2: 'File System Driver', 
                        4: 'Network Adapter', 
                        0x10: 'Win32 Own Process', 
                        0x20: 'Win32 Shared Process',
                        0x100: 'Interactive Process'}
            self.name = name
            self.type = typeopts[svctype] if svctype in typeopts else f'UNKNOWN (0x {svctype:02x})'
            self.displayname = displayname
            self.start = startopts[start] 
            self.path = path
            self.user = user # ObjectName
            self.servicedll = servicedll
            
        def __str__(self):
            return (f'Service: {self.name}\n  DisplayName: {self.displayname}\n  Type: {self.type}\n  '
                    f'ImagePath: {self.path}\n  Start: {self.start}\n  RunAs: {self.user}\n  ServiceDLL: {self.servicedll}')

    subkeys = Reg.list_subkeys('HKLM/system/currentcontrolset/services')
    for subkey in subkeys:
        vals = { 'name': subkey, 
                 'displayname': subkey, 
                 'type': None, 
                 'start': None, 
                 'imagepath': None, 
                 'objectname': 'LocalSystem', 
                 'servicedll': 'N/A'}
        for valname in vals.keys():
            try:
                vals[valname] = Reg.get_value(f'HKLM/system/currentcontrolset/services/{subkey}', valname).value
                #print(val)
            except:
                continue
        #print(vals)
        if vals['type'] is None:
            continue
        if vals['imagepath'] and vals['imagepath'].lower().find('svchost.exe') >= 0:
            try:
                vals['servicedll'] = Reg.get_value(f'HKLM/system/currentcontrolset/services/{subkey}/Parameters', 'servicedll').value
            except:
                pass
        svc = Service(vals['name'], vals['displayname'], vals['type'], vals['start'], vals['imagepath'], vals['objectname'], vals['servicedll'])

        print(svc)
        
        
        
         

def main():
    users = enum_users()
    enum_services()
    #enum_autoruns()
    sidinfo = map_sid_to_users()
    
    print(users)
    print(sidinfo)
    pass


if __name__ == '__main__':
    main()
