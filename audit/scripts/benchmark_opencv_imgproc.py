import argparse
import json
import os
import statistics
import time
from pathlib import Path

import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--label', required=True)
    parser.add_argument('--dll-dir', action='append', default=[])
    parser.add_argument('--samples', type=int, default=21)
    parser.add_argument('--iterations', type=int, default=30)
    args = parser.parse_args()
    handles = [os.add_dll_directory(str(Path(p).resolve())) for p in args.dll_dir]
    import cv2

    cv2.setUseOptimized(True)
    cv2.setNumThreads(1)
    rng = np.random.default_rng(20260918)
    image = rng.integers(0, 256, (1080, 1920, 3), dtype=np.uint8)
    operations = {
        'cvtColor_bgr_gray': lambda: cv2.cvtColor(image, cv2.COLOR_BGR2GRAY),
        'resize_1080p_to_720p': lambda: cv2.resize(image, (1280, 720), interpolation=cv2.INTER_LINEAR),
        'gaussian_blur_5x5': lambda: cv2.GaussianBlur(image, (5, 5), 0),
    }
    results = {}
    checksum = 0
    for name, operation in operations.items():
        for _ in range(5):
            operation()
        timings = []
        for _ in range(args.samples):
            start = time.perf_counter()
            output = None
            for _ in range(args.iterations):
                output = operation()
            elapsed = time.perf_counter() - start
            checksum = (checksum + int(output.flat[0])) & 0xFFFFFFFF
            timings.append(elapsed / args.iterations)
        median = statistics.median(timings)
        results[name] = {
            'median_ms': median * 1000,
            'mean_ms': statistics.mean(timings) * 1000,
            'operations_per_second': 1 / median,
            'samples_seconds_per_operation': timings,
        }
    print(json.dumps({
        'label': args.label,
        'cv2_version': cv2.__version__,
        'cv2_file': cv2.__file__,
        'optimized': cv2.useOptimized(),
        'threads': cv2.getNumThreads(),
        'image_shape': list(image.shape),
        'samples': args.samples,
        'iterations_per_sample': args.iterations,
        'checksum': checksum,
        'results': results,
        'build_information': cv2.getBuildInformation(),
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
