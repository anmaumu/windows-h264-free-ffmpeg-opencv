import argparse
import json
import os
import statistics
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('video', type=Path)
    parser.add_argument('--label', required=True)
    parser.add_argument('--dll-dir', action='append', default=[])
    parser.add_argument('--warmup', type=int, default=3)
    parser.add_argument('--runs', type=int, default=25)
    args = parser.parse_args()

    handles = [os.add_dll_directory(str(Path(p).resolve())) for p in args.dll_dir]
    import cv2

    def decode_once():
        cap = cv2.VideoCapture(str(args.video.resolve()), cv2.CAP_FFMPEG)
        if not cap.isOpened():
            raise RuntimeError('VideoCapture failed to open')
        backend = cap.getBackendName()
        frames = 0
        checksum = 0
        start = time.perf_counter()
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if frame is None or frame.shape != (240, 320, 3):
                raise RuntimeError(f'invalid frame: {None if frame is None else frame.shape}')
            checksum = (checksum + int(frame[0, 0, 0])) & 0xFFFFFFFF
            frames += 1
        elapsed = time.perf_counter() - start
        cap.release()
        if frames != 120 or backend != 'FFMPEG':
            raise RuntimeError(f'unexpected result: frames={frames}, backend={backend}')
        return elapsed, checksum, backend

    for _ in range(args.warmup):
        decode_once()
    samples = []
    checksums = []
    backend = None
    for _ in range(args.runs):
        elapsed, checksum, backend = decode_once()
        samples.append(elapsed)
        checksums.append(checksum)
    total_frames = 120 * len(samples)
    result = {
        'label': args.label,
        'cv2_version': cv2.__version__,
        'cv2_file': cv2.__file__,
        'backend': backend,
        'video': str(args.video.resolve()),
        'warmup_runs': args.warmup,
        'measured_runs': len(samples),
        'frames_per_run': 120,
        'total_frames': total_frames,
        'median_seconds_per_run': statistics.median(samples),
        'mean_seconds_per_run': statistics.mean(samples),
        'median_fps': 120 / statistics.median(samples),
        'aggregate_fps': total_frames / sum(samples),
        'min_seconds': min(samples),
        'max_seconds': max(samples),
        'samples_seconds': samples,
        'checksums_identical': len(set(checksums)) == 1,
        'build_information': cv2.getBuildInformation(),
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
