# Windows x64向け 推奨最小・ポータブルビルド構成

## 推奨構成

OpenCV 4.10.0をMSVCで静的ライブラリとしてPython拡張 `cv2.pyd`へ取り込み、FFmpeg 6.1.2だけを共有DLLにする。この構成なら配布物は概ね次の形になる。

```text
cv2.pyd                      # OpenCV core/imgproc/imgcodecs/videoioを内包
ffmpeg/
  avcodec-60.dll
  avformat-60.dll
  avutil-58.dll
  swscale-7.dll
```

公式 `opencv-python` wheelも `BUILD_SHARED_LIBS=OFF` でOpenCV本体を静的に格納している。Windows wheelのビルドはVisual Studioを使い、NASMもセットアップしている。公式headless版はGUIとMSMFを無効にする。

## OpenCV CMakeオプション

```powershell
cmake -S opencv-4.10.0 -B build-opencv-msvc -G Ninja `
  -DCMAKE_BUILD_TYPE=Release `
  -DCMAKE_INSTALL_PREFIX=<install> `
  -DBUILD_LIST=core,imgproc,imgcodecs,videoio,python3 `
  -DBUILD_SHARED_LIBS=OFF `
  -DBUILD_WITH_STATIC_CRT=ON `
  -DBUILD_opencv_python3=ON `
  -DBUILD_opencv_python2=OFF `
  -DBUILD_opencv_apps=OFF `
  -DBUILD_TESTS=OFF `
  -DBUILD_PERF_TESTS=OFF `
  -DBUILD_EXAMPLES=OFF `
  -DBUILD_DOCS=OFF `
  -DBUILD_opencv_java=OFF `
  -DBUILD_opencv_js=OFF `
  -DWITH_IPP=ON `
  -DBUILD_IPP_IW=ON `
  -DCPU_BASELINE=SSE3 `
  -DCPU_DISPATCH=SSE4_1,SSE4_2,FP16,AVX,AVX2 `
  -DWITH_OPENCL=OFF `
  -DWITH_MSMF=OFF `
  -DWITH_DSHOW=OFF `
  -DWITH_GSTREAMER=OFF `
  -DWITH_WIN32UI=OFF `
  -DWITH_QT=OFF `
  -DWITH_OPENGL=OFF `
  -DWITH_VTK=OFF `
  -DWITH_CUDA=OFF `
  -DWITH_EIGEN=OFF `
  -DWITH_LAPACK=OFF `
  -DWITH_ITT=OFF `
  -DWITH_PROTOBUF=OFF `
  -DBUILD_JPEG=ON `
  -DBUILD_PNG=ON `
  -DBUILD_ZLIB=ON `
  -DWITH_TIFF=OFF `
  -DWITH_OPENEXR=OFF `
  -DWITH_OPENJPEG=OFF `
  -DWITH_WEBP=OFF `
  -DOPENCV_FFMPEG_USE_FIND_PACKAGE=FFMPEG `
  -DOPENCV_FFMPEG_SKIP_DOWNLOAD=ON `
  -DPYTHON3_EXECUTABLE=<python.exe> `
  -DPYTHON3_INCLUDE_DIR=<python-include> `
  -DPYTHON3_LIBRARY=<python312.lib> `
  -DPYTHON3_NUMPY_INCLUDE_DIRS=<numpy-include>
```

`BUILD_LIST`は今回使用するPython API、画像配列処理、動画入力に必要な範囲。`videoio`の依存により`imgcodecs`も含める。JPEG/PNG/ZlibはOpenCV同梱ソースから静的に組み込み、対象PCの別DLLへ依存させない。

`CPU_BASELINE=SSE3`と`CPU_DISPATCH=SSE4_1,SSE4_2,FP16,AVX,AVX2`は測定した公式4.10.0 wheelと同じ。`NATIVE`や`DETECT`を指定するとビルドPC固有命令がbaselineへ入る可能性があるため使用しない。追加命令はdispatchなので、対応していないCPUでもSSE3経路で動く。

`WITH_IPP=ON`は公式wheelに近づけるうえで重要。今回遅かった`GaussianBlur`などにはIPP経路がある。IPPICVはOpenCVビルドへ静的に含まれるため、実行先にIPP DLLを要求しない。取得物はキャッシュし、URL・バージョン・SHA-256を記録する。

`WITH_OPENCL=OFF`は公式wheelとの差になるが、GPUドライバーやOpenCL ICDによるPC間差を避けるため。通常のCPU `Mat`処理を主用途とする今回はこちらを推奨する。

## FFmpeg 6.1.2 ランタイムDLL用オプション

Visual Studio Developer Command PromptからMSYS2を `-use-full-path` で起動し、NASMをPATHへ置いてMSVC toolchainでビルドする。

```bash
./configure \
  --prefix=<install> \
  --toolchain=msvc \
  --arch=x86_64 \
  --disable-autodetect \
  --disable-everything \
  --disable-static \
  --enable-shared \
  --disable-programs \
  --disable-doc \
  --disable-debug \
  --disable-network \
  --disable-avdevice \
  --disable-avfilter \
  --disable-swresample \
  --enable-avcodec \
  --enable-avformat \
  --enable-swscale \
  --enable-decoder=vp9 \
  --enable-parser=vp9 \
  --enable-demuxer=matroska \
  --enable-protocol=file \
  --enable-w32threads \
  --enable-x86asm
make -j8
make install
```

現在の `--disable-x86asm` は削除する。NASMを使った最適化を有効にする。`--disable-everything`からVP9とMatroskaだけを明示的に戻すのでH.264系のソフトウェア・ハードウェア実装は入らない。最終判定では従来どおり`-buildconf`、decoder/encoder一覧、DLLロードパス、VP9/H.264実入力を再検証する。

FFmpeg単体の監査用CLIも必要なら、同じソースと設定を基に別ビルドを作り、`--disable-programs`を外して `ffmpeg`/`ffprobe`、null muxer、wrapped_avframe encoder、必要なfiltersだけを追加する。アプリ用DLLと監査用CLIで機能範囲を混ぜない。

## 公式wheelにさらに近づける選択肢

Python 3.7以降で同じwheelを使いたい場合は `-DPYTHON3_LIMITED_API=ON` と `-DINSTALL_CREATE_DISTRIB=ON`を追加する。今回のNuitka EXEはPython 3.12へ固定して配布するため必須ではない。

公式wheelと同じAPI範囲が必要なら `BUILD_LIST`を外す。ただしサイズとビルド時間が増え、今回不要なDNN、calib3d、features2dなども入る。最小構成と完全な公式API互換は同時には満たせない。

## 環境依存の残り

完全な無依存にはできない。`cv2.pyd`はPython ABI、Windows API、Universal CRTに依存する。Nuitka onefileではPythonランタイムを内包できる。Windows 10/11 x64を対象にし、OpenCVを静的CRT、FFmpegをMSVC既定の静的CRTで作れば、MinGWの `libgcc_s_seh-1.dll`、`libstdc++-6.dll`、`libwinpthread-1.dll` とOpenCV DLL群は不要になる。

今回のPCにはVisual Studio Community 2026があるが、NASMはPATH上になく、公式Windows wheel workflowはVisual Studio 2022系を使用している。再現性を優先するならVisual Studio 2022 Build Tools v143とNASMの固定版を用意する。現在のMinGW版FFmpeg import libraryをMSVC版OpenCVへそのまま渡さず、FFmpeg自体を `--toolchain=msvc` で作り直す。

## 参照した一次資料

- [opencv-python setup.py](https://github.com/opencv/opencv-python/blob/4.x/setup.py)
- [opencv-python Windows wheel workflow](https://github.com/opencv/opencv-python/blob/4.x/.github/workflows/build_wheels_windows.yml)
- [opencv-python build and packaging README](https://github.com/opencv/opencv-python/blob/4.x/README.md)
- [OpenCV CPU optimization build options](https://github.com/opencv/opencv/wiki/CPU-optimizations-build-options)
- [FFmpeg Windows/MSVC build instructions](https://ffmpeg.org/platform.html)
