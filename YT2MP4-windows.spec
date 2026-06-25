# -*- mode: python ; coding: utf-8 -*-

import os
import shutil

ffmpeg_candidates = [
    os.environ.get('FFMPEG_BINARY'),
    shutil.which('ffmpeg.exe'),
    shutil.which('ffmpeg'),
    os.path.join('bin', 'ffmpeg.exe'),
]

binaries = []
for ffmpeg_path in ffmpeg_candidates:
    if ffmpeg_path and os.path.exists(ffmpeg_path):
        binaries.append((ffmpeg_path, '.'))
        break

a = Analysis(
    ['desktop.py'],
    pathex=[],
    binaries=binaries,
    datas=[('frontend/dist', 'frontend/dist')],
    hiddenimports=['yt_dlp', 'uvicorn', 'webview'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='YT2MP4',
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
)
