import os, sys, argparse
from utils.reg import Reg
import columnar
import traceback
import datetime


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

def enum_system():
    keyroot = r'HKLM\software\microsoft\windows nt\currentversion'
    valuenames = ['ProductName', 
                  'BaseBuildRevisionNumber', 'BuildLab', 'BuildLabEx', 'CurrentVersion', 'CurrentMajorVersionNumber', 'CurrentMinorVersionNumber', 'CurrentBuildNumber', 'EditionID', 
                  'InstallationType', 'InstallDate', 'InstallTime', 'PathName', 'SystemRoot', 'RegisteredOwner']
    values = []
    for valuename in valuenames:
        value = Reg.get_value(keyroot, valuename)
        if valuename.lower() in ['installtime', 'installdate']:
            val = int(value.value)
            if valuename.lower() == 'installtime':
              val = (val - 116444736000000000)/10000000
            value.value = datetime.datetime.fromtimestamp(val).strftime(r'%Y-%m-%dT%H:%M:%SZ')
        values.append([valuename, value.value])
    return (values, ['ValueName', 'Value'])

def enum_autoruns():
    autoruns = {'GLOBAL (HKLM)': {} }  # { user: { valuename: value}}
    userpaths = {}
    keys = {'hklm/software/microsoft/windows/currentversion/run': 'GLOBAL (HKLM)',
    'hklm/software/microsoft/windows/currentversion/runonce': 'GLOBAL (HKLM)',
    'HKLM/Software/Microsoft/Windows/CurrentVersion/policies/Explorer/Run' : 'GLOBAL (HKLM)'}
    users = map_sid_to_users()
    for sid in Reg.get_users_keys():
        keys[f'hkey_users/{sid}/software/microsoft/windows/currentversion/run'] = users[sid]
        keys[f'hkey_users/{sid}/software/microsoft/windows/currentversion/runonce'] = users[sid]
        keys[f'hkey_users/{sid}/Software\Microsoft/Windows NT/CurrentVersion/Windows/Run'] = users[sid]
        userpaths[sid] = Reg.get_value(f'HKLM/SOFTWARE/Microsoft/Windows NT/CurrentVersion/ProfileList/{sid}', 'ProfileImagePath').value
        autoruns[users[sid]] = {}
        
    
    for key in keys.keys():
        #print(f'{keys[key]} ({key})')
        exception = None
        try:
            vals = Reg.get_subkey_values(key)['\\']
        except PermissionError:
            exception = 'ACCESS DENIED'
            vals = None
        except FileNotFoundError:
            exception = 'KEY DOES NOT EXIST'
            vals = None
        except:
            print(traceback.format_exc())
        finally:
            if not vals and exception:
                autoruns[keys[key]][f'{exception} ("{os.path.basename(key)}" KEY)'] = None
            else:
                for val in vals:
                    autoruns[keys[key]][val.name] = val.value
    startupentries = []
    for sid in userpaths:
        folder = os.path.join(userpaths[sid], r'appdata\roaming\microsoft\windows\start menu\programs\startup')
        for root, subdirs, files in os.walk(folder):
            for file in files:
                startupentries.append([users[sid], 'STARTUP_FOLDER', os.path.join(root, file)])
        
    ret = []
    for user in autoruns:
        for val in autoruns[user]:
                ret.append([user, val, autoruns[user][val]])
    return (ret + startupentries, ['User', 'Name', 'Path/Command'])

def enum_users():
    users = map_sid_to_users()
    ret = []
    for sid in users.keys():
        ret.append(users[sid])
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
            return (f'Service: {self.name}\n    DisplayName: {self.displayname}\n    Type: {self.type}\n    '
                    f'ImagePath: {self.path}\n    Start: {self.start}\n    RunAs: {self.user}\n    ServiceDLL: {self.servicedll}')

        def __row__(self):
            return  [self.name, self.displayname, self.type, self.path, self.start, self.user, self.servicedll]
        
        @staticmethod
        def __tableheader__():
            return  ['name', 'displayname', 'type', 'path', 'start', 'user', 'servicedll']
    rows = []
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
        rows.append(svc.__row__())

    return (rows, Service.__tableheader__())

def enum_winlogon():
    '''Enumerates values in the 
       HKLM\Software\Microsoft\Windows NT\CurrentVersion\WinLogon key'''
    ret = []
    for value in Reg.get_subkey_values(r'HKLM\Software\Microsoft\Windows NT\CurrentVersion\WinLogon')['\\']:
        print(value)
        ret.append([value.name, value.value])
    
    return [ret, ['WinLogon Value Name','Value']]
        
def print_table_ex(rows :list, headers : list = None):
    if not headers:
        headers = rows[0]
        rows = rows[1:]

    print(columnar.columnar(rows, headers=headers))
         
def print_table(rowsandheaders: list):
    ''' Expects a list object of [<rows>, <headers>] '''
    print_table_ex(rowsandheaders[0], rowsandheaders[1])

def enum_installed_software():
    rootkeys = [r'HKLM\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall', 
                r'HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall']
    valuenames = ['DisplayName', 'DisplayVersion', 'Publisher', 'VersionMajor', 'VersionMinor']
    ret = []
    for key in rootkeys:
        x64 = key.lower().find('\\wow6432node\\') > 0
        apps = sorted(Reg.list_subkeys(key))
        for app in apps:
            info = []
            for valuename in valuenames:
                try:
                    value = Reg.get_value(os.path.join(key, app), valuename).value
                except:
                    value = None
                info.append(value)
            info.append(x64)    
            ret.append(info)
    headers = valuenames + ['x64']
    return ([ret, headers])

def main():
    users = enum_users()
    services = enum_services()
    autoruns = enum_autoruns()
    sidinfo = map_sid_to_users()
    systeminfo = enum_system()
    installedsoftware = enum_installed_software()
    winlogon = enum_winlogon()

    print(users)
    print_table(systeminfo)
    print_table_ex([ [sidinfo[x], x] for x in sidinfo.keys()], headers=['user', 'SID'])
    print_table(autoruns)
    print_table(services)
    print_table(installedsoftware)
    print_table(winlogon)


if __name__ == '__main__':
    main()
