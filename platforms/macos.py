import os
import plistlib
import re
import subprocess
import sys

import xmltodict
try:
    from utils import printer
except:
    sys.path.insert(0, '.')
    from utils import printer


def get_launchdaemons(user='root'):
    keepfields = [
        'Label', 'MachServices', 'Program', 'ProgramArguments', 'RunAtLoad',
        'Sockets', 'UserName'
    ]
    plists = {}
    for root, _, filenames in os.walk('/Library/LaunchDaemons'):
        for filename in filenames:
            ldpath = os.path.join(root, filename)
            ld = plistlib.load(open(ldpath, 'rb'))
            for key in list(ld.keys()):
                if key not in keepfields:
                    del ld[key]
            plists[ldpath] = ld
    printer.print_table_from_dicts(plists.values(),
                                   f"Launch Daemons for User: {user}")
    return plists


def get_launchagents(user='root'):
    keepfields = [
        'Label', 'MachServices', 'Program', 'ProgramArguments', 'RunAtLoad',
        'Sockets'
    ]
    plists = {}
    for root, _, filenames in os.walk('/Library/LaunchAgents'):
        for filename in filenames:
            lapath = os.path.join(root, filename)
            la = plistlib.load(open(lapath, 'rb'))
            for key in list(la.keys()):
                if key not in keepfields:
                    del la[key]
            plists[lapath] = la
    printer.print_table_from_dicts(plists.values(), "Launch Agents")
    return plists


def get_users():
    proc = subprocess.Popen(['dscl', '.', 'list', '/Users'],
                            stdout=subprocess.PIPE)
    users = proc.stdout.read().strip().decode().split('\n')
    userinfo_re = re.compile(
        'NFSHomeDirectory: (.*)\\nPrimaryGroupID: ([\\-0-9]+)\\nRealName:(\\n |)(.*)\\nUniqueID: ([\\-0-9]+)$',
        re.MULTILINE)
    userinfo = {}
    for user in users:
        proc = subprocess.Popen([
            'dscl', '.', 'read', f'/Users/{user}', 'NFSHomeDirectory',
            'RealName', 'UniqueID', 'PrimaryGroupID'
        ],
                                stdout=subprocess.PIPE)
        tmp = proc.stdout.read().strip().decode()
        ret = userinfo_re.search(tmp)
        #print(userinfo.encode('unicode_escape'))
        homedir, groupid, _, name, uniqueid = ret.groups()
        #print(f'{homedir} | {groupid} | {name}')
        userinfo[user] = {
            'Username': user,
            'Home': homedir,
            'PrimaryGroupID': groupid,
            'UserID': uniqueid,
            'DisplayName': name.strip()
        }
    printer.print_table_from_dicts(userinfo.values(), "Users")
    return userinfo

def get_args():
    # TODO
    return None

def main(args=None):
    launch_agents = get_launchagents()
    launch_daemons = get_launchdaemons()
    users = get_users()


if __name__ == '__main__':
    main()
