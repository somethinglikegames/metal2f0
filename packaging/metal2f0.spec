from pathlib import Path
import sys


PROJECT_ROOT = Path(SPECPATH).parent
SRC_ROOT = PROJECT_ROOT / "src"
ICON_PATH = SRC_ROOT / "metal2f0" / "resources" / "icons" / "metal2f0.ico"


a = Analysis(
    [str(SRC_ROOT / "metal2f0" / "app.py")],
    pathex=[str(SRC_ROOT)],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)


pyz = PYZ(
    a.pure,
    a.zipped_data,
)


if sys.platform == "win32":
    exe_name = "metal2f0.exe"
else:
    exe_name = "metal2f0.x86_64"

exe_kwargs = {
    "name": exe_name,
    "debug": False,
    "bootloader_ignore_signals": False,
    "strip": False,
    "upx": True,
    "console": False,
}

if sys.platform == "win32":
    exe_kwargs["icon"] = str(ICON_PATH)


exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    **exe_kwargs,
)
