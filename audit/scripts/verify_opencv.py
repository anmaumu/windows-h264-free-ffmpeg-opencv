import ctypes, json, os, sys
from ctypes import wintypes
from pathlib import Path
from common import *

FFBIN=(ROOT/'prefix/ffmpeg/bin').resolve()
OCVBIN=(ROOT/'prefix/opencv/x64/mingw/bin').resolve()
MINGW=Path(r'C:\Program Files (x86)\mingw64\bin').resolve()
handles=[os.add_dll_directory(str(p)) for p in (FFBIN,OCVBIN,MINGW)]
os.environ['PATH']=';'.join(map(str,(FFBIN,OCVBIN,MINGW)))
import cv2

build=cv2.getBuildInformation()
(LOG/'opencv_build_information.txt').write_text(build,encoding='utf-8')
(LOG/'opencv_identity.txt').write_text(f'cv2.__file__={cv2.__file__}\ncv2.__version__={cv2.__version__}\n',encoding='utf-8')

def read_video(name, limit):
    path=(ROOT/'media'/name).resolve()
    cap=cv2.VideoCapture(str(path),cv2.CAP_FFMPEG)
    opened=cap.isOpened()
    backend=cap.getBackendName() if opened else None
    good=0; shapes=[]; invalid=None
    while good < limit:
        ok,frame=cap.read()
        if not ok: break
        valid=frame is not None and frame.ndim==3 and frame.shape[0]==240 and frame.shape[1]==320 and frame.shape[2]==3 and frame.size>0
        if not valid:
            invalid={'index':good,'shape':None if frame is None else list(frame.shape),'size':None if frame is None else int(frame.size)}
            break
        shapes.append(list(frame.shape)); good+=1
    cap.release()
    return {'path':str(path),'isOpened':opened,'backend':backend,'valid_frames':good,'invalid_frame':invalid,'first_shape':shapes[0] if shapes else None}

vp9=read_video('vp9.mkv',100)
h264=read_video('h264.mkv',1)

psapi=ctypes.WinDLL('psapi',use_last_error=True); kernel=ctypes.WinDLL('kernel32',use_last_error=True)
EnumProcessModules=psapi.EnumProcessModules; EnumProcessModules.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.HMODULE),wintypes.DWORD,ctypes.POINTER(wintypes.DWORD)]
GetModuleFileNameExW=psapi.GetModuleFileNameExW; GetModuleFileNameExW.argtypes=[wintypes.HANDLE,wintypes.HMODULE,wintypes.LPWSTR,wintypes.DWORD]
proc=kernel.GetCurrentProcess(); needed=wintypes.DWORD(); arr=(wintypes.HMODULE*4096)()
if not EnumProcessModules(proc,arr,ctypes.sizeof(arr),ctypes.byref(needed)): raise ctypes.WinError(ctypes.get_last_error())
mods=[]
for mod in arr[:needed.value//ctypes.sizeof(wintypes.HMODULE)]:
    buf=ctypes.create_unicode_buffer(32768)
    if GetModuleFileNameExW(proc,mod,buf,len(buf)): mods.append(str(Path(buf.value).resolve()))
(LOG/'opencv_loaded_modules.txt').write_text('\n'.join(mods)+'\n',encoding='utf-8')

ff_names=['avcodec-60.dll','avformat-60.dll','avutil-58.dll','swscale-7.dll','swresample-4.dll']
required_loaded={'avcodec-60.dll','avformat-60.dll','avutil-58.dll','swscale-7.dll'}
loaded_by_name={Path(p).name.lower():p for p in mods}
ff_evidence=[]
for name in ff_names:
    loaded=loaded_by_name.get(name.lower())
    expected=FFBIN/name
    ff_evidence.append({'name':name,'expected':digest(expected),'loaded':digest(loaded) if loaded else None,'same_path':loaded is not None and Path(loaded).resolve()==expected})
opencv_ffmpeg_wrappers=[p for p in mods if 'opencv_videoio_ffmpeg' in Path(p).name.lower()]
foreign_ffmpeg=[p for p in mods if Path(p).name.lower() in [x.lower() for x in ff_names] and not str(Path(p).resolve()).lower().startswith(str(FFBIN).lower())]
cv2_native=next((p for p in mods if Path(p).name.lower().startswith('cv2.') and Path(p).suffix.lower()=='.pyd'),None)

result={'python':sys.version,'python_executable':sys.executable,'cv2_file':cv2.__file__,'cv2_version':cv2.__version__,
 'ffmpeg_build_info':next((line.strip() for line in build.splitlines() if 'FFMPEG:' in line),None),
 'vp9':vp9,'h264':h264,'ffmpeg_dll_evidence':ff_evidence,
 'cv2_native_module':digest(cv2_native) if cv2_native else None,
 'opencv_ffmpeg_wrapper_dlls':opencv_ffmpeg_wrappers,'foreign_ffmpeg_dlls':foreign_ffmpeg,
 'pass':vp9['valid_frames']==100 and vp9['backend']=='FFMPEG' and h264['valid_frames']==0 and all(x['same_path'] and x['expected']['sha256']==x['loaded']['sha256'] for x in ff_evidence if x['name'] in required_loaded) and not opencv_ffmpeg_wrappers and not foreign_ffmpeg}
save('opencv_verification',result)
print(json.dumps(result,indent=2,ensure_ascii=False))
assert result['pass']
