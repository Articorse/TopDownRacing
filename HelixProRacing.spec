# -*- mode: python ; coding: utf-8 -*-

import sys
import os.path
import shutil
CWD = os.path.abspath(os.path.dirname(sys.executable))

print("Copying working files.")
working_dir_files = [
                ('assets', 'assets')
                ]
for tup in working_dir_files:
        print(tup)
        to_path = os.path.join(DISTPATH, tup[1])
        if os.path.exists(to_path):
                if os.path.isdir(to_path):
                        shutil.rmtree(to_path)
                else:
                        os.remove(to_path)
        if os.path.isdir(tup[0]):
                shutil.copytree(tup[0], to_path )
        else:
                shutil.copyfile(tup[0], to_path )
print("Copied working files.")

block_cipher = None


game = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(game.pure, game.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    game.scripts,
    game.binaries,
	# Tree('assets', prefix='assets/'),
    game.zipfiles,
    game.datas,
    [],
    name='HelixProRacing',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\icon.ico'],
)

importer = Analysis(
    ['trackimporter.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(importer.pure, importer.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    importer.scripts,
    importer.binaries,
    importer.zipfiles,
    importer.datas,
    [],
    name='HPRTrackImporter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\iconimporter.ico'],
)
