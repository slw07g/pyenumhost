# -*- mode: python ; coding: utf-8 -*-
import sys
block_cipher = None

hiddenimports = ['platforms.utils.printer']
name = 'enumhost'
if sys.platform == 'darwin':
    hiddenimports.append('platforms.macos')
    name += '.mac'
elif sys.platform == 'win32':
    hiddenimports.append('platforms.windows')
    hiddenimports.append('platforms.utils.reg')
    name += '.exe'
elif sys.platform == 'nix':
    hiddenimports.append('platforms.nix')
    name += '.nix'

a = Analysis(['enumhost.py'],
             pathex=[os.getcwd(), 'platforms'],
             binaries=[],
             datas=[],
             hiddenimports=hiddenimports,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='enumhost',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
