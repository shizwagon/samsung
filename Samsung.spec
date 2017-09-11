# -*- mode: python -*-

block_cipher = None


a = Analysis(['es.py', 'main.py'],
             pathex=['/Users/Trent/PycharmProjects/untitled'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=['pyinstaller-hooks'],
             runtime_hooks=['pyinstaller-hooks/pyi_rth__tkinter.py'],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='Samsung',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='Samsung')
app = BUNDLE(coll,
             name='Samsung.app',
             icon=None,
             bundle_identifier=None)
