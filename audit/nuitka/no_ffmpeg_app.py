import json
import importlib.util
import os
import sys
from pathlib import Path
import numpy

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
    bundled_cv2_dir = Path(sys.executable).resolve().parent / 'cv2' / 'python-3.12'
    if bundled_cv2_dir.is_dir():
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
                      'frames_valid': valid}, ensure_ascii=False))
    return 0 if opened and backend == 'FFMPEG' and frames == 100 and valid else 1

if __name__ == '__main__':
    raise SystemExit(main())
