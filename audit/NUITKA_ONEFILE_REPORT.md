# Nuitka onefile: FFmpeg DLLのみ外部配置

## 結論

Windows x64で実証済み。Python、NumPy、OpenCV 4.10.0、OpenCVのMinGWランタイムを単一EXEに格納し、FFmpeg DLLだけを外部ディレクトリからロードできた。

検証対象は `audit/nuitka/onefile-build/no_ffmpeg_onefile.exe`。配布時はこのEXEと、別配置する自作FFmpeg DLLディレクトリを用意する。OpenCVのPEファイルはZIPを通常データとしてEXEへ格納し、Nuitkaの一時ディレクトリへ起動時に展開する。FFmpeg DLLはそのZIPに含めない。

## 実測結果

| 検証 | 結果 | 根拠 |
|---|---|---|
| 単一EXE生成 | PASS | Nuitka `--onefile`で生成 |
| EXE隣接FFmpeg DLL | PASS | 0件 |
| 外部FFmpegでVP9読出し | PASS | `CAP_FFMPEG`、有効画像100フレーム、終了コード0 |
| ロード元 | PASS | `avcodec-60.dll`、`avformat-60.dll`、`avutil-58.dll`、`swscale-7.dll`がすべて指定した `audit/prefix/ffmpeg/bin` |
| 外部FFmpegなし | PASS | PATHを `C:\Windows\System32` のみにして空ディレクトリを指定するとDLL load failure、終了コード1 |
| 別FFmpeg混入防止 | PASS | PATHを限定し、ロード済みDLLの絶対パスを照合 |

実測値とSHA-256は `audit/logs/nuitka-onefile-verification.json` に保存する。標準出力・標準エラーは `audit/logs/nuitka-onefile-*.txt` に保存する。

## 再実行

```powershell
& audit\scripts\Build-Nuitka-Onefile-NoFFmpeg.ps1
& audit\scripts\Verify-Nuitka-Onefile-NoFFmpeg.ps1
```

ビルドスクリプトはOpenCV関連PEを `.bin` 名でステージし、`opencv_payload.zip`へまとめる。ZIP内に禁止対象FFmpeg DLLがないことを検査した後、Nuitkaへデータファイルとして渡す。アプリは起動時にZIPをNuitkaの一時ディレクトリへ展開し、元の拡張子へ復元してから、外部FFmpeg DLLディレクトリを `os.add_dll_directory` で登録する。

この方式ではFFmpeg DLLの場所を起動引数で渡す必要がある。実製品ではEXEの隣の設定ファイルや固定相対パスから解決する形へ変更できる。結論は技術的なDLL分離とH.264除外ビルドの利用確認に限定し、特許・ライセンス上の問題がすべて解決したことを意味しない。
