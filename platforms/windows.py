import argparse
import datetime
import os
import traceback

import xmltodict

try:
    from platforms.utils.reg import Reg
    from platforms.utils import printer
except:
    from utils.reg import Reg
    from utils import printer


def map_sid_to_users():
    ret = {}
    builtins = {
        'S-1-5-18': 'SYSTEM',
        'S-1-5-19': 'LocalService',
        'S-1-5-20': 'NetworkService'
    }
    for sid in Reg.get_users_keys():
        try:
            if sid in builtins:
                profile = builtins[sid]
            else:
                profilepath = Reg.get_value(
                    f'HKEY_LOCAL_MACHINE/SOFTWARE/Microsoft/Windows NT/CurrentVersion/ProfileList/{sid}',
                    'ProfileImagePath')
                profile = os.path.basename(profilepath.value)

        except:
            profile = '<NOT FOUND>'
        finally:
            ret[sid] = profile
    return ret


def enum_system():
    keyroot = r'HKLM\software\microsoft\windows nt\currentversion'
    valuenames = [
        'ProductName', 'BaseBuildRevisionNumber', 'BuildLab', 'BuildLabEx',
        'CurrentVersion', 'CurrentMajorVersionNumber',
        'CurrentMinorVersionNumber', 'CurrentBuildNumber', 'EditionID',
        'InstallationType', 'InstallDate', 'PathName', 'SystemRoot',
        'RegisteredOwner'
    ]
    values = []
    for valuename in valuenames:
        value = Reg.get_value(keyroot, valuename)
        if valuename.lower() in ['installdate']:
            val = int(value.value)
            if valuename.lower() == 'installtime':
                val = int((val - 116444736000000000) / 10000000)
            value.value = datetime.datetime.fromtimestamp(val).strftime(
                r'%Y-%m-%dT%H:%M:%SZ')
        values.append([valuename, value.value])
    return (values, ['ValueName', 'Value'])


def enum_autoruns():
    autoruns = {'GLOBAL (HKLM)': {}}  # { user: { valuename: value}}
    userpaths = {}
    keys = {
        'hklm/software/microsoft/windows/currentversion/run':
        'GLOBAL (HKLM)',
        'hklm/software/microsoft/windows/currentversion/runonce':
        'GLOBAL (HKLM)',
        'HKLM/Software/Microsoft/Windows/CurrentVersion/policies/Explorer/Run':
        'GLOBAL (HKLM)'
    }
    users = map_sid_to_users()
    for sid in Reg.get_users_keys():
        keys[
            f'hkey_users/{sid}/software/microsoft/windows/currentversion/run'] = users[
                sid]
        keys[
            f'hkey_users/{sid}/software/microsoft/windows/currentversion/runonce'] = users[
                sid]
        keys[
            f'hkey_users/{sid}/Software/Microsoft/Windows NT/CurrentVersion/Windows/Run'] = users[
                sid]
        userpaths[sid] = Reg.get_value(
            f'HKLM/SOFTWARE/Microsoft/Windows NT/CurrentVersion/ProfileList/{sid}',
            'ProfileImagePath').value
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
                autoruns[keys[key]][
                    f'{exception} ("{os.path.basename(key)}" KEY)'] = None
            else:
                for val in vals:
                    autoruns[keys[key]][val] = vals[val]
    startupentries = []
    for sid in userpaths:
        folder = os.path.join(
            userpaths[sid],
            r'appdata\roaming\microsoft\windows\start menu\programs\startup')
        for root, _, files in os.walk(folder):
            for file in files:
                startupentries.append(
                    [users[sid], 'STARTUP_FOLDER',
                     os.path.join(root, file)])

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
        def __init__(self,
                     name,
                     displayname,
                     svctype,
                     start,
                     path,
                     user='LocalSystem',
                     servicedll='N/A'):
            startopts = {
                0: 'BOOT',
                1: 'SYSTEM',
                2: 'AUTOLOAD',
                3: 'MANUAL',
                4: 'DISABLED'
            }
            typeopts = {
                1: 'Kernel Driver',
                2: 'File System Driver',
                4: 'Network Adapter',
                0x10: 'Win32 Own Process',
                0x20: 'Win32 Shared Process',
                0x100: 'Interactive Process'
            }
            self.name = name
            self.type = typeopts[
                svctype] if svctype in typeopts else f'UNKNOWN (0x {svctype:02x})'
            self.displayname = displayname
            self.start = startopts[start]
            self.path = path
            self.user = user  # ObjectName
            self.servicedll = servicedll

        def __str__(self):
            return (
                f'Service: {self.name}\n    DisplayName: {self.displayname}\n    Type: {self.type}\n    '
                f'ImagePath: {self.path}\n    Start: {self.start}\n    RunAs: {self.user}\n    ServiceDLL: {self.servicedll}'
            )

        def __row__(self):
            return [
                self.name, self.displayname, self.type, self.path, self.start,
                self.user, self.servicedll
            ]

        @staticmethod
        def __tableheader__():
            return [
                'name', 'displayname', 'type', 'path', 'start', 'user',
                'servicedll'
            ]

    rows = []
    subkeys = Reg.list_subkeys('HKLM/system/currentcontrolset/services')
    for subkey in subkeys:
        vals = {
            'name': subkey,
            'displayname': subkey,
            'type': None,
            'start': None,
            'imagepath': None,
            'objectname': 'LocalSystem',
            'servicedll': 'N/A'
        }
        for valname in vals.keys():
            try:
                vals[valname] = Reg.get_value(
                    f'HKLM/system/currentcontrolset/services/{subkey}',
                    valname).value
                #print(val)
            except:
                continue
        #print(vals)
        if vals['type'] is None:
            continue
        if vals['imagepath'] and vals['imagepath'].lower().find(
                'svchost.exe') >= 0:
            try:
                vals['servicedll'] = Reg.get_value(
                    f'HKLM/system/currentcontrolset/services/{subkey}/Parameters',
                    'servicedll').value
            except:
                pass
        svc = Service(vals['name'], vals['displayname'], vals['type'],
                      vals['start'], vals['imagepath'], vals['objectname'],
                      vals['servicedll'])
        rows.append(svc.__row__())

    return (rows, Service.__tableheader__())


def enum_winlogon():
    '''Enumerates values in the 
       HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\WinLogon key'''
    ret = []
    values = Reg.get_subkey_values(
        r'HKLM\Software\Microsoft\Windows NT\CurrentVersion\WinLogon')['\\']
    for value in values:
        #print(value)
        ret.append([value, values[value]])

    return [ret, ['WinLogon Value Name', 'Value']]


def enum_installed_software():
    rootkeys = [
        r'HKLM\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall',
        r'HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall'
    ]
    valuenames = [
        'DisplayName', 'DisplayVersion', 'Publisher', 'VersionMajor',
        'VersionMinor'
    ]
    ret = []
    for key in rootkeys:
        x64 = key.lower().find('\\wow6432node\\') > 0
        apps = sorted(Reg.list_subkeys(key))
        for app in apps:
            info = []
            for valuename in valuenames:
                try:
                    value = Reg.get_value(os.path.join(key, app),
                                          valuename).value
                except:
                    value = None
                info.append(value)
            info.append(x64)
            ret.append(info)
    headers = valuenames + ['x64']
    return ([ret, headers])


def enum_scheduled_tasks():
    # https://docs.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-schema
    ret = []

    headers = [
        'TaskFileName', 'TaskName', 'TaskDir', 'Description', 'Author',
        'PrincipalId', 'PrincipalSID', 'RunLevel', 'Action', 'ActionContext',
        'Exec/Handler', 'Arguments/Data'
    ]
    for root, _, files in os.walk(
            os.path.expandvars(r'%windir%\system32\tasks')):
        for file in files:
            taskpath = os.path.join(root, file)
            try:
                taskinfo = xmltodict.parse(open(taskpath, 'rb').read())
                #print(taskinfo)
            except PermissionError:
                continue
            except:
                print(f'Exception with Task File: {taskpath}')
                print(traceback.format_exc())
                continue

            taskname = os.path.basename(
                taskinfo['Task']['RegistrationInfo']['URI'])
            taskdir = os.path.dirname(
                taskinfo['Task']['RegistrationInfo']['URI'])
            author = "" if 'Author' not in taskinfo['Task'][
                'RegistrationInfo'] else taskinfo['Task']['RegistrationInfo'][
                    'Author']
            principalid = taskinfo['Task']['Principals']['Principal']['@id']
            usersid = taskinfo['Task']['Principals']['Principal'].get(
                'UserId', '')
            runlevel = taskinfo['Task']['Principals']['Principal'].get(
                'RunLevel', '')
            description = taskinfo['Task']['RegistrationInfo'].get(
                'Description', '')
            actions = taskinfo['Task']['Actions']
            actioncontext = actions['@Context']
            keys = ([x for x in actions])
            keys.remove('@Context')
            actiontype = keys[0]
            action1 = action2 = ''
            if actiontype == 'Exec':
                action1 = actions['Exec']['Command']
                action2 = actions['Exec'].get('Arguments', '')
            elif actiontype == 'ComHandler':
                action1 = actions['ComHandler']['ClassId']
                action2 = actions['ComHandler'].get('Data', '')
            else:
                # SendEmail, ShowMessage
                action1 = str(actions[actiontype])
                action2 = ''
            # TODO multiple rows for multiple actions/triggers?

            ret.append([
                file, taskname, taskdir, description, author, principalid,
                usersid, runlevel, actiontype, actioncontext, action1, action2
            ])
    return (ret, headers)


def enum_windows_packages(full=False):
    rootkey = r'hklm\software\microsoft\windows\currentversion\component based servicing\packages'
    valuenames = [
        'CurrentState', 'InstallName', 'InstallTimeHigh', 'InstallTimeLow',
        'InstallUser', 'Visibility'
    ]
    headers = [
        'CurrentState', 'InstallName', 'Architecture', 'Locale', 'Version',
        'InstallTimeHigh', 'InstallTimeLow', 'InstallUser', 'Visibility'
    ]
    ret = []
    users = map_sid_to_users()
    states = {
        0: 'Absent',
        5: 'Uninstall Pending',
        0x10: 'Resolving',
        0x20: 'Resolved',
        0x30: 'Staging',
        0x40: 'Staged',
        0x50: 'Superseded',
        0x60: 'Install Pending',
        0x65: 'Partially Installed',
        0x70: 'Installed',
        0x80: 'Permanent'
    }
    for subkey in Reg.list_subkeys(rootkey):
        key = os.path.join(rootkey, subkey)
        packages = Reg.get_subkey_values(key)['\\']
        row = []
        if not full and Reg.get_value(key, 'CurrentState').value != 0x70:
            continue
        for valuename in valuenames:
            value = packages.get(valuename, '')
            if valuename == 'InstallUser' and len(value):
                value = users.get(value, value)
            elif valuename == 'CurrentState':
                value = states.get(value, f'0x{value:02x}')
            if valuename == 'InstallName':
                pkgname, _, pkgarch, pkglocale, pkgversion = value.rstrip(
                    '.mum').split('~')
                row.append(pkgname)
                row.append(pkgarch)
                row.append(pkglocale)
                row.append(pkgversion)
            else:
                row.append(value)
            #print(row)
        ret.append(row)
        #break
    return (ret, headers)


def get_args():
    parser = argparse.ArgumentParser(
        description='A tool that extracts information about a host')
    parser.add_argument('--accounts',
                        '-a',
                        required=False,
                        default=False,
                        action='store_true',
                        help='Extract user information from the host')
    parser.add_argument(
        '--autoruns',
        '-r',
        required=False,
        default=False,
        action='store_true',
        help='Extract autostart information from registry and startup folders')
    parser.add_argument('--services',
                        '-S',
                        required=False,
                        default=False,
                        action='store_true',
                        help='Extract details about services')
    parser.add_argument('--tasks',
                        '-t',
                        required=False,
                        default=False,
                        action='store_true',
                        help='Extract scheduled task information')
    parser.add_argument('--sysinfo',
                        '-i',
                        required=False,
                        default=False,
                        action='store_true',
                        help='Extract OS information from the host')
    parser.add_argument('--software',
                        '-s',
                        required=False,
                        default=False,
                        action='store_true',
                        help='Extract details about installed applications')
    parser.add_argument(
        '--winlogon',
        '-w',
        required=False,
        default=False,
        action='store_true',
        help='Extract information from the winlogon registry key')
    parser.add_argument('--updates',
                        '-u',
                        required=False,
                        default=False,
                        action='store_true',
                        help='Extract details about installed windows updates')
    parser.add_argument(
        '--updates-full',
        '-U',
        required=False,
        default=False,
        action='store_true',
        help=
        'Extract details about windows updates/packages (regardless of installation state)'
    )
    parser.add_argument('--all',
                        '-A',
                        required=False,
                        default=False,
                        action='store_true',
                        help='Extract all information from the host')
    parser.add_argument('--loglevel',
                        '-L',
                        required=False,
                        default=False,
                        type=str,
                        help='Log level: DEBUG, INFO, WARNING, etc...')

    args = parser.parse_args()
    if not (args.accounts or args.autoruns or args.services or args.tasks
            or args.sysinfo or args.software or args.winlogon or args.updates
            or args.updates_full):
        args.all = True
    if args.all:
        args.accounts = args.autoruns = args.services = args.tasks = \
        args.software = args.winlogon = args.updates = args.updates_full = \
        args.sysinfo = True
    return args


def main(args=None):
    if not args:
        args = get_args()

    if args.accounts:
        users = enum_users()
        sidinfo = map_sid_to_users()
        printer.print_table_ex([[user] for user in users], ['Username'],
                               'Users')
        printer.print_table_ex([[sidinfo[x], x] for x in sidinfo.keys()],
                               headers=['user', 'SID'],
                               title='User SID Info')
    if args.autoruns:
        autoruns = enum_autoruns()
        printer.print_table(autoruns, "AutoRuns")

    if args.sysinfo:
        systeminfo = enum_system()
        printer.print_table(systeminfo, 'System Information')

    if args.winlogon:
        winlogon = enum_winlogon()
        printer.print_table(winlogon, 'WinLogon Settings')

    if args.services:
        services = enum_services()
        printer.print_table(services, 'Services')

    if args.software:
        installedsoftware = enum_installed_software()
        printer.print_table(installedsoftware, 'Installed Apps')

    if args.tasks:
        tasks = enum_scheduled_tasks()
        printer.print_table(tasks, 'Scheduled Tasks')

    if args.updates or args.updates_full:
        packages = enum_windows_packages(args.updates_full)
        printer.print_table(packages, 'Installed Updates')


if __name__ == '__main__':
    main()
