# 自作OpenCV画像処理性能比較

## 結論

自作OpenCV 4.10.0の性能は、公式 `opencv-python-headless==4.10.0.84` に対して処理ごとに異なった。1080p画像の単一スレッド測定では、`resize`は自作版が約5.4%高速、`cvtColor`は約9.4%低速、`GaussianBlur`は約15.2%低速だった。自作版が全面的に遅いわけではないが、フィルタ処理には改善余地がある。

## 条件

- Windows x64、Python 3.12、NumPy 1.26.4、OpenCV 4.10.0
- 同じ決定的乱数から生成した1920×1080 BGR `uint8`画像
- `cv2.setUseOptimized(True)`
- `cv2.setNumThreads(1)`（並列ランタイム差を除いてカーネル性能を比較）
- 各処理を5回ウォームアップ後、30回連続実行を1標本として21標本測定
- 出力チェックサムは両構成で一致

## 結果

| 処理 | 自作版 中央値 | 公式版 中央値 | 自作版の速度差 |
|---|---:|---:|---:|
| BGR→Gray `cvtColor` | 2.249 ms | 2.037 ms | 9.4%低速 |
| 1080p→720p `resize` | 4.899 ms | 5.164 ms | 5.4%高速 |
| 5×5 `GaussianBlur` | 10.694 ms | 9.067 ms | 15.2%低速 |

## ビルド差

自作版はMinGW GCC 15.2、`-O3`、SSE～AVX512 dispatch、pthreads。公式wheelはMSVC 19.0、`/O2`、SSE～AVX2 dispatch、Microsoft Concurrencyを使用している。単一スレッドに固定しても差があるため、主因はコンパイラ、OpenCV HAL/SIMDコード経路、各処理の実装最適化の違いと考えられる。

実アプリが動画読出し中心なら、別途実施したVP9ベンチマークでは全体性能が標準版とほぼ同じだった。画像フィルタを多用する場合は、その実処理パイプラインを追加測定するのが適切である。

全21標本とビルド情報は `audit/logs/benchmark-imgproc-custom.json` および `audit/logs/benchmark-imgproc-standard.json`、再実行コードは `audit/scripts/benchmark_opencv_imgproc.py` に保存した。
