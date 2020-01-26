import winreg as wr
import os, sys
import traceback

class Value:
    def __init__(self, val):
        self.name, self.value, self.type = val

    def __str__(self):
        return (f'[{self.name}] = {self.value}')
    
    def __repr__(self):
        return str(self)

class Reg:
    def __init__(self):
        pass

    @staticmethod
    def normalize_path(path):
        return path.replace('/', '\\').lower()

    @staticmethod
    def get_root_key(path):
        path = Reg.normalize_path(path)
        keymap = {
            'hklm': wr.HKEY_LOCAL_MACHINE,
            'hkey_local_machine': wr.HKEY_LOCAL_MACHINE,
            'hkcu': wr.HKEY_CURRENT_USER,
            'hkey_current_user': wr.HKEY_CURRENT_USER,
            'hkey_users': wr.HKEY_USERS,
            'hkey_classes_root': wr.HKEY_CLASSES_ROOT,
            'hkcr': wr.HKEY_CLASSES_ROOT,
            'hkey_performance_data': wr.HKEY_PERFORMANCE_DATA,
            'hkpd': wr.HKEY_PERFORMANCE_DATA
        }

        split = path.split('\\')
        root_name = split[0]
        #print(root_name)
        rest = '\\'
        if len(split) > 1:
            rest = '\\'.join(split[1:])
            #print(rest)
        try:
            return (keymap[root_name], rest)
        except:
            return

    @staticmethod
    def get_value_by_index(hkey, idx):
        pass

    @staticmethod
    def get_key_by_path(path):
        # returns a hkey
        pass

    @staticmethod
    def get_key_by_index(hkey, idx):
        # returns a hkey
        pass
    
    @staticmethod
    def enum_key(hkey, idx):
        hkey = Reg.open_key(hkey) if type(hkey) == str else hkey
        try:
            ret = wr.EnumKey(key, idx)
        except OSError:
            ret = None
        finally:
            return ret

    @staticmethod
    def enum_value(hkey, idx):
        hkey = Reg.open_key(hkey) if type(hkey) == str else hkey
        try:
            ret = wr.EnumValue(hkey, idx)
        except OSError:
            ret = None
        finally:
            return ret
    
    @staticmethod
    def open_key(path):
        if type(path) != str:
            return path
        (rootkey, subkey) = Reg.get_root_key(path)
        return wr.OpenKey(rootkey, subkey)
    
    @staticmethod
    def get_value(hkey, valuename):
        hkey = Reg.open_key(hkey) if type(hkey) == str else hkey
        val = wr.QueryValueEx(hkey, valuename)
        return Value((valuename, val[0], val[1]))

    @staticmethod
    def get_hkey_values(hkey):
        hkey = Reg.open_key(hkey) if type(hkey) == str else hkey
        ret = {}
        for i in range(0xFFFF):
            try:
                v = Value(wr.EnumValue(hkey, i))
                ret[v.name] = v.value
                
            except:
                #print(traceback.format_exc())
                break
        return ret
        
    @staticmethod
    def get_subkey_values(hkey):
        hkey = Reg.open_key(hkey) if type(hkey) == str else hkey

        ret = {'\\': Reg.get_hkey_values(hkey)}
        for i in range(0xFFFF):
            try:
                subkey = wr.EnumKey(hkey, i)
                key = wr.OpenKey(hkey, subkey)
                ret[subkey] = Reg.get_hkey_values(key)
            except:
                #print(traceback.format_exc())
                break
        return ret

    @staticmethod
    def list_subkeys(hkey):
        hkey = Reg.open_key(hkey) if type(hkey) == str else hkey
        ret = []
        for i in range(0xFFFF):
            try:
                ret.append(wr.EnumKey(hkey, i))
            except:
                break
        return ret


    @staticmethod
    def get_users_keys():
        keys = []
        for sid in Reg.list_subkeys(r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList'):
            if sid.lower().endswith('_classes'):
                continue
            keys.append(sid)
        return keys

def main():

    regkeyS = 'hkey_current_user/software/microsoft/windows/currentversion/run'
    (r, subkey) = Reg.get_root_key(regkeyS)
    print(r)
    print(subkey)
    print(hex(r))
    reg = wr.OpenKey(r, subkey)
    print(dir(reg))
    vals = Reg.get_subkey_values(reg)
    print(Reg.get_value(reg, 'Box Edit'))
    print(vals)
    return

if __name__ == '__main__':
    main()
    sys.exit(0)
