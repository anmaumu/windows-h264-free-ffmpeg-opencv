# H.264-free FFmpeg + OpenCV Python on Windows x64

Windows x64でFFmpeg 6.1.2をH.264関連機能なしでビルドし、その共有DLLを使うOpenCV 4.10.0 Python版を検証した記録です。

確認済みの内容:

- 自作FFmpegでVP9/Matroskaを100フレームデコード
- H.264/OpenH264/QSV/NVENC/CUVID系エンコーダー・デコーダーが未登録
- OpenCV `CAP_FFMPEG`でVP9を100フレーム取得
- PythonプロセスがロードしたFFmpeg DLLを絶対パスとSHA-256で照合
- Nuitka standalone配布物からFFmpeg DLLを除外し、外部DLLディレクトリ指定で起動

詳細:

- [FFmpeg/OpenCV検証報告](audit/REPORT.md)
- [Nuitka DLL非同梱検証報告](audit/NUITKA_REPORT.md)
- [検証スクリプト](audit/scripts)
- [Nuitkaサンプルプログラム](audit/nuitka/no_ffmpeg_app.py)

ビルド済みバイナリやダウンロード済みソース、仮想環境はリポジトリへ含めていません。各スクリプトは固定バージョンと成果物配置を前提にしています。

この検証は技術的なH.264機能の除外確認に限定されます。特許・ライセンス上の問題がすべて解決したことを意味しません。
