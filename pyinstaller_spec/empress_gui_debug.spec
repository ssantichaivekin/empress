# -*- mode: python ; coding: utf-8 -*-

# Build empress as a directory with debugging on

block_cipher = None


a = Analysis(['../empress_gui.py'],
             pathex=['pyinstaller_spec'],
             binaries=[],
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
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='empress',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='empress_gui_debug')
