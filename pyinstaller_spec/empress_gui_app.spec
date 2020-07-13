# -*- mode: python ; coding: utf-8 -*-

# Build empress as macOS app bundle

block_cipher = None


a = Analysis(['../empress_gui.py'],
             pathex=['pyinstaller_spec'],
             binaries=[],
             datas=[("../assets", "./assets")],
             hiddenimports=[],
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
          [],
          exclude_binaries=True,
          name='empress_gui',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='empress')
app = BUNDLE(coll,
             name='empress.app',
             icon=None,
             bundle_identifier=None,
             info_plist={
                 'NSPrincipalClass': 'NSApplication',  # Enable retina display
                 'CFBundleName': 'Empress DTL Computational Biology Tool',  # Enable Siri
             }
            )
