import json
import importlib.util
import ctypes
import os
import shutil
import sys
import zipfile
from pathlib import Path
import numpy

FFMPEG_DLLS = ('avcodec-60.dll', 'avformat-60.dll', 'avutil-58.dll',
               'swscale-7.dll', 'swresample-4.dll', 'avfilter-9.dll')

def loaded_ffmpeg_paths():
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel32.GetModuleHandleW.argtypes = [ctypes.c_wchar_p]
    kernel32.GetModuleHandleW.restype = ctypes.c_void_p
    kernel32.GetModuleFileNameW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint]
    kernel32.GetModuleFileNameW.restype = ctypes.c_uint
    result = {}
    for name in FFMPEG_DLLS:
        handle = kernel32.GetModuleHandleW(name)
        if handle:
            buffer = ctypes.create_unicode_buffer(32768)
            if kernel32.GetModuleFileNameW(handle, buffer, len(buffer)):
                result[name] = buffer.value
    return result

def main():
    if len(sys.argv) != 3:
        print('usage: no_ffmpeg_app.exe VIDEO_PATH EXTERNAL_FFMPEG_DLL_DIR', file=sys.stderr)
        return 64
    video = Path(sys.argv[1]).resolve()
    dll_dir = Path(sys.argv[2]).resolve()
    if not dll_dir.is_dir():
        print(json.dumps({'started': True, 'error': 'external FFmpeg DLL directory is missing', 'dll_dir': str(dll_dir)}))
        return 65
    # Keep the handle alive until process exit. This directory is external to
    # the Nuitka distribution and must contain the exact custom FFmpeg DLLs.
    dll_handles = [os.add_dll_directory(str(dll_dir))]
    # In standalone this is the distribution root; in onefile it is Nuitka's
    # temporary extraction root. The external FFmpeg directory remains outside.
    runtime_root = Path(__file__).resolve().parent
    bundled_cv2_dir = runtime_root / 'cv2' / 'python-3.12'
    payload_zip = runtime_root / 'opencv_payload.zip'
    if payload_zip.is_file() and not bundled_cv2_dir.is_dir():
        with zipfile.ZipFile(payload_zip) as archive:
            archive.extractall(runtime_root)
    if bundled_cv2_dir.is_dir():
        # Nuitka filters PE files from generic data inclusion. The onefile
        # build stores OpenCV/MinGW PE files as *.bin and restores their names
        # inside its private extraction directory. FFmpeg DLLs are absent.
        for packed in bundled_cv2_dir.glob('*.bin'):
            restored = packed.with_suffix('')
            if not restored.exists():
                shutil.copyfile(packed, restored)
        dll_handles.append(os.add_dll_directory(str(bundled_cv2_dir)))
    native_cv2 = bundled_cv2_dir / 'cv2.cp312-win_amd64.pyd'
    spec = importlib.util.spec_from_file_location('cv2', native_cv2)
    if spec is None or spec.loader is None:
        print(json.dumps({'started': True, 'error': 'cv2 native module not found', 'path': str(native_cv2)}))
        return 66
    cv2 = importlib.util.module_from_spec(spec)
    sys.modules['cv2'] = cv2
    spec.loader.exec_module(cv2)
    cap = cv2.VideoCapture(str(video), cv2.CAP_FFMPEG)
    opened = cap.isOpened()
    backend = cap.getBackendName() if opened else None
    frames = 0
    valid = True
    while frames < 100:
        ok, frame = cap.read()
        if not ok:
            break
        if frame is None or frame.ndim != 3 or frame.shape != (240, 320, 3) or frame.size == 0:
            valid = False
            break
        frames += 1
    cap.release()
    print(json.dumps({'started': True, 'cv2_version': cv2.__version__, 'cv2_file': cv2.__file__,
                      'video': str(video), 'external_ffmpeg_dir': str(dll_dir),
                      'opened': opened, 'backend': backend, 'valid_frames': frames,
                      'frames_valid': valid,
                      'loaded_ffmpeg_dlls': loaded_ffmpeg_paths()}, ensure_ascii=False))
    return 0 if opened and backend == 'FFMPEG' and frames == 100 and valid else 1

if __name__ == '__main__':
    raise SystemExit(main())
