# FFmpeg DLL非同梱 Nuitka EXE検証

実施日: 2026-09-17、Windows 11 x64

## 結論

PASS。Nuitka standalone配布フォルダーにFFmpeg DLLを同梱せず、外部の自作FFmpeg DLLディレクトリを明示することでEXEを起動し、OpenCVのFFmpegバックエンドからVP9/MKVを100フレーム読み出せた。

これは「FFmpeg DLLが不要」という意味ではない。DLLはEXE配布物の外部に必要であり、見つからなければ`cv2.pyd`のロード時にEXEは失敗する。

| 項目 | 結果 |
|---|---|
| 配布フォルダー内のavcodec/avformat/avutil/swscale/swresample/avfilter DLL | 0件 |
| PATH | `C:\Windows\System32`だけに制限 |
| 外部自作FFmpegディレクトリを指定 | 終了コード0 |
| OpenCVバックエンド | `FFMPEG` |
| VP9有効フレーム | 100、各320x240x3 |
| 空の外部DLLディレクトリを指定 | 非ゼロ終了、`cv2`ネイティブモジュールのDLLロード失敗 |

## 構成

- Nuitka 2.7.16 standalone
- Python 3.12.14
- NumPy 1.26.4
- 自作OpenCV 4.10.0の`cv2.cp312-win_amd64.pyd`
- 外部FFmpeg: 前回検証したFFmpeg 6.1.2共有DLL
- C backend: Nuitka指定WinLibs GCC 14.2.0

配布フォルダーにはEXE、Python/NumPyランタイム、cv2.pyd、OpenCV DLL、MinGWランタイムを置いた。FFmpeg DLLだけは`--noinclude-dlls`で除外し、ステージ処理でも0件を検査する。

自作OpenCVのPythonパッケージは標準wheelと異なる`cv2/python-3.12`配置であるため、Nuitkaはネイティブpydを自動収集できなかった。`Stage-Nuitka-NoFFmpeg.ps1`でcv2.pydとOpenCV/MinGW DLLを明示配置し、プログラムからpydを明示ロードしている。

## 再実行

```powershell
powershell -ExecutionPolicy Bypass -File .\audit\scripts\Build-Nuitka-NoFFmpeg.ps1
powershell -ExecutionPolicy Bypass -File .\audit\scripts\Verify-Nuitka-NoFFmpeg.ps1
```

生成EXE:

`audit/nuitka/short-build/no_ffmpeg_app.dist/no_ffmpeg_app.exe`

実行形式:

```powershell
.\no_ffmpeg_app.exe <VP9動画の絶対パス> <外部FFmpeg DLLディレクトリの絶対パス>
```

## ログ

- `logs/nuitka-build.stdout.txt`, `logs/nuitka-build.stderr.txt`
- `logs/nuitka-run-external-ffmpeg.stdout.txt`, `logs/nuitka-run-external-ffmpeg.stderr.txt`
- `logs/nuitka-run-no-ffmpeg.stdout.txt`, `logs/nuitka-run-no-ffmpeg.stderr.txt`
- `logs/nuitka-verification.json`

ビルド途中では、Visual Studio 2026がNuitka 2.7.16に認識されない問題と、深いWinLibsキャッシュパスでWindowsヘッダーの内部includeが解決できない問題が発生した。WinLibs GCCを使用し、コンパイラーinclude配置を補正した後にビルドは成功した。これらの失敗ログも保存している。
