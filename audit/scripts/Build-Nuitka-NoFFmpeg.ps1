$ErrorActionPreference = 'Stop'
$AuditRoot = Split-Path $PSScriptRoot -Parent
$Py = "$AuditRoot\.venv\Scripts\python.exe"
$env:NUITKA_CACHE_DIR = "$AuditRoot\nuitka\cache"
$env:PYTHONPATH = "$AuditRoot\nuitka\build_helper"
$env:PATH = "$AuditRoot\prefix\ffmpeg\bin;$AuditRoot\prefix\opencv\x64\mingw\bin;C:\Program Files (x86)\mingw64\bin;$env:PATH"
New-Item -ItemType Directory -Force "$AuditRoot\nuitka\short-build",$env:NUITKA_CACHE_DIR | Out-Null
# Nuitka imports cv2 while analysing its package configuration. Python 3.12
# searches beside python.exe for extension dependencies, so stage build-only
# DLLs in this dedicated venv. The --noinclude-dlls rules below keep FFmpeg out
# of the resulting distribution.
Copy-Item "$AuditRoot\prefix\ffmpeg\bin\*.dll" "$AuditRoot\.venv\Scripts" -Force
Copy-Item "$AuditRoot\prefix\opencv\x64\mingw\bin\*.dll" "$AuditRoot\.venv\Scripts" -Force
Copy-Item 'C:\Program Files (x86)\mingw64\bin\libgcc_s_seh-1.dll' "$AuditRoot\.venv\Scripts" -Force
Copy-Item 'C:\Program Files (x86)\mingw64\bin\libstdc++-6.dll' "$AuditRoot\.venv\Scripts" -Force
Copy-Item 'C:\Program Files (x86)\mingw64\bin\libwinpthread-1.dll' "$AuditRoot\.venv\Scripts" -Force
$ErrorActionPreference = 'Continue'
& $Py -m nuitka `
  --standalone --assume-yes-for-downloads --mingw64 `
  --output-dir="$AuditRoot\nuitka\short-build" `
  --output-filename=no_ffmpeg_app.exe `
  --noinclude-dlls=avcodec-60.dll `
  --noinclude-dlls=avformat-60.dll `
  --noinclude-dlls=avutil-58.dll `
  --noinclude-dlls=swscale-7.dll `
  --noinclude-dlls=swresample-4.dll `
  --noinclude-dlls=avfilter-9.dll `
  "$AuditRoot\nuitka\no_ffmpeg_app.py" `
  1> "$AuditRoot\logs\nuitka-build.stdout.txt" `
  2> "$AuditRoot\logs\nuitka-build.stderr.txt"
if ($LASTEXITCODE -ne 0) { throw 'Nuitka build failed; see audit/logs/nuitka-build.*.txt' }
& "$PSScriptRoot\Stage-Nuitka-NoFFmpeg.ps1"
