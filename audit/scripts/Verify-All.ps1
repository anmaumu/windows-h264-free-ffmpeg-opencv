$ErrorActionPreference = 'Stop'
$AuditRoot = Split-Path $PSScriptRoot -Parent
$env:PATH = "$AuditRoot\prefix\ffmpeg\bin;$AuditRoot\prefix\opencv\x64\mingw\bin;C:\Program Files (x86)\mingw64\bin"
$ErrorActionPreference = 'Continue'
& "$AuditRoot\.venv\Scripts\python.exe" "$PSScriptRoot\verify_ffmpeg.py" 1> "$AuditRoot\logs\verify-all-ffmpeg.stdout.txt" 2> "$AuditRoot\logs\verify-all-ffmpeg.stderr.txt"
if ($LASTEXITCODE -ne 0) { throw 'FFmpeg verification failed' }
& "$AuditRoot\.venv\Scripts\python.exe" "$PSScriptRoot\verify_opencv.py" 1> "$AuditRoot\logs\verify-all-opencv.stdout.txt" 2> "$AuditRoot\logs\verify-all-opencv.stderr.txt"
if ($LASTEXITCODE -ne 0) { throw 'OpenCV verification failed' }
Get-Content "$AuditRoot\logs\verify-all-ffmpeg.stdout.txt"
Get-Content "$AuditRoot\logs\verify-all-opencv.stdout.txt"
