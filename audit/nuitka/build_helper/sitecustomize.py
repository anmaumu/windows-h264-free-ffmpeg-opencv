import os
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
_dll_handles = []
for _path in (_root/'prefix/ffmpeg/bin', _root/'prefix/opencv/x64/mingw/bin', Path(r'C:\Program Files (x86)\mingw64\bin')):
    if _path.is_dir():
        _dll_handles.append(os.add_dll_directory(str(_path)))
