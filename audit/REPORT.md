# Windows x64 H.264除外FFmpeg / OpenCV Python 検証報告

実施日: 2026-09-17 (Asia/Tokyo)

## 結論

このWindows x64ホスト上で固定版FFmpeg 6.1.2をH.264関連機能なしでビルドし、その共有DLLへOpenCV 4.10.0 Python版をリンクして実動作を確認した。

| 検証項目 | 結果 | 根拠 |
|---|---|---|
| 自作FFmpegでVP9/MKVをデコード | PASS | `ffmpeg.exe`が100フレームを処理し、終了コード0、progressの`frame=100`を確認 |
| VP9デコーダーとMatroska/WebMデマルチプレクサー | PASS | `-decoders`に`vp9`、`-demuxers`に`matroska,webm` |
| H.264エンコーダー・デコーダー除外 | PASS | 登録一覧にh264/OpenH264/QSV/NVENC/CUVID該当なし。`--disable-everything`後にVP9だけを明示有効化。H.264/MKVはコンテナとcodec_id=27を認識後、デコーダー不在で非ゼロ終了 |
| OpenCVでVP9を100フレーム取得 | PASS | `CAP_FFMPEG`指定、backend=`FFMPEG`、100個すべて320x240x3の有効なNumPy配列 |
| OpenCVでH.264フレームを取得できない | PASS | `read()`成功数0。ログは`Could not find decoder for codec_id=27`。`isOpened()`だけでは判定していない |
| OpenCVが自作FFmpeg DLLを使用 | PASS | Pythonプロセスのロード済みDLLをWindows APIで列挙。avcodec/avformat/avutil/swscaleが自作出力の絶対パス・SHA-256と一致 |
| 標準OpenCV FFmpeg DLLや別FFmpegの混入なし | PASS | `opencv_videoio_ffmpeg*.dll`なし、対象名の外部FFmpeg DLLなし。検証時PATHも専用FFmpeg/OpenCV/MinGWのみに限定 |

この結論は技術的なH.264機能の除外確認に限る。特許・ライセンス上の問題がすべて解決したことを意味しない。

## 環境と固定バージョン

- OS: Windows 11, build 26100, AMD64
- Python: 3.12.14, 64-bit、専用仮想環境 `audit/.venv`
- OpenCV: 4.10.0
- FFmpeg: 6.1.2 (`libavcodec 60.31.102`, `libavformat 60.16.100`, `libavutil 58.29.100`, `libswscale 7.5.100`)
- MinGW GCC/G++: 15.2.0
- CMake: 3.31.6、Ninja: 1.11.1.4
- FFmpegソース: `https://ffmpeg.org/releases/ffmpeg-6.1.2.tar.xz`
- OpenCVソース: `https://github.com/opencv/opencv/archive/refs/tags/4.10.0.zip`
- 素材生成・正常性確認用FFmpeg: `C:\Program Files\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe`。SHA-256 `9260c3627ce1fccda993b683f2fd9fbf532318d8f159831a3b360804b4907510`

調査時、作業ディレクトリに既存の自作成果物はなかった。システム側FFmpegはH.264対応の通常ビルドだったため、素材生成と正常性確認にだけ用いた。既存Python環境へOpenCVは入っていなかった。

## ビルド構成

検証対象FFmpegの絶対パス:

`C:\Users\masaki\Documents\Codex\2026-09-16\windows-x64-h-264-ffmpeg-opencv\audit\prefix\ffmpeg\bin\ffmpeg.exe`

SHA-256: `54f19d120ac0ffcd671947cd57742eaf6d726fb8f3eb684c2ac849828f08373d`

主要configure設定:

```text
--disable-autodetect --disable-everything --disable-static --enable-shared
--enable-decoder=vp9 --enable-parser=vp9 --enable-demuxer=matroska
--enable-protocol=file,pipe --enable-muxer=null
--enable-encoder=wrapped_avframe
--enable-filter=buffer,buffersink,null,format,scale
```

`null` muxer、`wrapped_avframe` encoder、および最小限のfilter/protocolは、`-f null -`で実デコード結果を検証するために追加した。H.264機能は追加していない。完全なコマンドは `scripts/build-ffmpeg.sh` にある。

OpenCVは `OPENCV_FFMPEG_USE_FIND_PACKAGE=FFMPEG` と専用の `FindFFMPEG.cmake` を使い、自作の共有ライブラリーへリンクした。ビルド対象はcore/imgproc/videoio/python3と依存モジュール。MSMFとDirectShowを無効にした。完全なコマンドは `scripts/Build-OpenCV.ps1` にある。

## テスト素材

どちらも同じ `testsrc2=size=320x240:rate=30:duration=4` から生成し、別FFmpeg/ffprobeで120フレームおよび正常デコードを確認した。

| ファイル | codec/container | フレーム | 解像度 | SHA-256 |
|---|---|---:|---:|---|
| `media/vp9.mkv` | VP9 / Matroska | 120 | 320x240 | `f8ba0754531f0ec7710753dfb387cd0682cd98e4983c0fd0d94cb8db2549d8d4` |
| `media/h264.mkv` | H.264 / Matroska | 120 | 320x240 | `46bb031c5e756a347d36a216e529271b4c7f617cb34c6435f4cb248d9870c8b5` |

H.264側もMKVなので、OpenCV/FFmpegの失敗はMP4デマルチプレクサー不足によるものではない。対象FFmpegは実際にMatroskaコンテナとH.264ストリームを認識した後、デコーダー不在で失敗している。

## H.264除外判定

`-decoders`、`-encoders`、`-hwaccels`と`-buildconf`を組み合わせて確認した。

- decoder登録はVP9のみ。H.264、OpenH264、QSV、CUVIDに該当する登録なし。
- encoder登録は検証出力用`wrapped_avframe`のみ。H.264、OpenH264、QSV、NVENCに該当する登録なし。
- hardware acceleration methodsは空。
- ビルドは`--disable-everything`を基点にVP9デコーダーだけを有効化しており、H.264関連の明示enableなし。
- H.264/MKVの実デコードは`Decoding requested, but no decoder found for: h264`で終了。終了コードはWindows上で`4294967274`（符号付きでは負値）だった。

このため、単なる文字列検索ではなく、登録一覧、ビルド設定、正常なH.264素材に対する実動作の三点で除外を判断した。

## OpenCVとロードDLLの証拠

- `cv2.__file__`: `audit\.venv\Lib\site-packages\cv2\__init__.py`
- native module: `audit\.venv\Lib\site-packages\cv2\python-3.12\cv2.cp312-win_amd64.pyd`
- native module SHA-256: `bfdbf9be1950897dd6328546afed6c7c47339cb54781121a81931b9d8f00b469`
- `cv2.__version__`: `4.10.0`
- build information: `FFMPEG: YES (find_package)`、avcodec 60.31.102 / avformat 60.16.100 / avutil 58.29.100 / swscale 7.5.100

Pythonプロセスで実際にロードされたDLL:

| DLL | SHA-256 | 結果 |
|---|---|---|
| `audit/prefix/ffmpeg/bin/avcodec-60.dll` | `a71419b6948c62ad811c4c477b20b89aea77dd2e0a1397eb3f58778ed92f2e0c` | 自作出力と同一 |
| `audit/prefix/ffmpeg/bin/avformat-60.dll` | `6b4cf965d870e0e1b00c5bd9a6d87d1ebeec2f5b458095ad8353e212ced8eb3a` | 自作出力と同一 |
| `audit/prefix/ffmpeg/bin/avutil-58.dll` | `5b05a585e79bb8fe976b15e269a02b524e4765dcbfe55d225217207670d2269b` | 自作出力と同一 |
| `audit/prefix/ffmpeg/bin/swscale-7.dll` | `ccc617f177eedee3204e5f654dd52c83fa17e0a0a8ac3b52cbe7d9b9ea20ea64` | 自作出力と同一 |

`swresample-4.dll`も同じ自作成果物に含まれるが、この映像は音声なしでOpenCVの読出しに不要なためプロセスにはロードされなかった。

## 再実行

前提成果物を含む現在の環境では次で全検証を再実行できる。

```powershell
powershell -ExecutionPolicy Bypass -File .\audit\scripts\Verify-All.ps1
```

素材の再生成・事前調査:

```powershell
powershell -ExecutionPolicy Bypass -File .\audit\scripts\Prepare.ps1
```

FFmpegおよびOpenCVの再ビルド手順はそれぞれ `scripts/build-ffmpeg.sh` と `scripts/Build-OpenCV.ps1` に固定している。FFmpegスクリプトはGit Bashから呼び出す。

## ログと成果物

- `logs/target_version.stdout.txt`, `target_buildconf.stdout.txt`, `target_decoders.stdout.txt`, `target_encoders.stdout.txt`, `target_demuxers.stdout.txt`, `target_hwaccels.stdout.txt`
- `logs/target_decode_vp9.*`, `target_decode_h264.*`
- `logs/opencv_build_information.txt`, `opencv_identity.txt`, `opencv_loaded_modules.txt`, `opencv_verification.json`
- `logs/ffmpeg-native-build.*`, `opencv-configure.txt`, `opencv-build.txt`, `opencv-install.txt`
- `logs/media.json`, `artifact_inventory.json`, `commands.jsonl`
- `logs/verify-all-ffmpeg.*`, `verify-all-opencv.*`

初回FFmpegビルドはGit Bash形式の絶対パスをWindows版makeが解釈できず停止した。`build/ffmpeg-native`内の作業コピーでビルドするよう修正した。初回OpenCV構成はWindowsのバックスラッシュをCMakeがエスケープとして解釈して停止し、スラッシュ表記へ修正した。いずれも修正後のビルドと最終検証は成功しており、失敗ログも保存している。
