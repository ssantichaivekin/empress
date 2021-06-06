# -*- mode: python ; coding: utf-8 -*-

# Build empress as macOS app bundle

block_cipher = None


a = Analysis(['../empress_gui.py'],
             pathex=['pyinstaller_spec'],
             binaries=[],
             # copy data from ../assets to ./assets in the executable folder
             datas=[("../assets", "./assets")],
             # pkg_resources.py2_warn hidden import needed if setuptools>=45.0.0
             # https://github.com/pypa/setuptools/issues/1963#issuecomment-574265532
             hiddenimports=['pkg_resources.py2_warn'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

# Windows and Linux
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='empress_gui',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          icon='../assets/jane_icon.ico',
          console=False)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='empress')

# macOS
app = BUNDLE(coll,
             name='empress.app',
             icon='../assets/jane_icon.icns',
             bundle_identifier=None,
             info_plist={
                 # Enable retina display
                 'NSPrincipalClass': 'NSApplication',
                 # Enable Siri and Spotlight to search this app
                 'CFBundleName': 'Empress DTL Computational Biology Tool',
                 # Set bundle id so gatekeeper can find it
                 'CFBundleIdentifier': 'com.hmc.empress',
             }
            )
