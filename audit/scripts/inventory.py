import json, platform, subprocess, sys
from pathlib import Path
from common import *

patterns=[ROOT/'sources/ffmpeg-6.1.2.tar.xz',ROOT/'sources/opencv-4.10.0.zip',ROOT/'media/vp9.mkv',ROOT/'media/h264.mkv']
patterns += sorted((ROOT/'prefix/ffmpeg/bin').glob('*'))
patterns += sorted((ROOT/'prefix/opencv/x64/mingw/bin').glob('*.dll'))
patterns += sorted((ROOT/'.venv/Lib/site-packages/cv2').glob('python-3.12/*.pyd'))
files=[digest(p) for p in patterns if p.is_file()]
save('artifact_inventory',{'host':platform.platform(),'python':sys.version,'files':files})
