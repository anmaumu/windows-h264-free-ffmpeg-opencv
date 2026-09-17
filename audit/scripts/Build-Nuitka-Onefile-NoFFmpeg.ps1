$ErrorActionPreference = 'Stop'
$AuditRoot = Split-Path $PSScriptRoot -Parent
$Py = "$AuditRoot\.venv\Scripts\python.exe"
$PayloadRoot = "$AuditRoot\nuitka\onefile-data"
$Payload = "$PayloadRoot\cv2\python-3.12"
$PayloadZip = "$AuditRoot\nuitka\opencv_payload.zip"
$Output = "$AuditRoot\nuitka\onefile-build"
$env:NUITKA_CACHE_DIR = "$AuditRoot\nuitka\cache"
$env:PYTHONPATH = "$AuditRoot\nuitka\build_helper"
$env:PATH = "$AuditRoot\prefix\ffmpeg\bin;$AuditRoot\prefix\opencv\x64\mingw\bin;C:\Program Files (x86)\mingw64\bin;$env:PATH"
New-Item -ItemType Directory -Force $Payload,$Output | Out-Null
$Files = @(
  "$AuditRoot\.venv\Lib\site-packages\cv2\python-3.12\cv2.cp312-win_amd64.pyd",
  "$AuditRoot\prefix\opencv\x64\mingw\bin\libopencv_core4100.dll",
  "$AuditRoot\prefix\opencv\x64\mingw\bin\libopencv_imgcodecs4100.dll",
  "$AuditRoot\prefix\opencv\x64\mingw\bin\libopencv_imgproc4100.dll",
  "$AuditRoot\prefix\opencv\x64\mingw\bin\libopencv_videoio4100.dll",
  'C:\Program Files (x86)\mingw64\bin\libgcc_s_seh-1.dll',
  'C:\Program Files (x86)\mingw64\bin\libstdc++-6.dll',
  'C:\Program Files (x86)\mingw64\bin\libwinpthread-1.dll'
)
foreach ($File in $Files) { Copy-Item $File (Join-Path $Payload ((Split-Path $File -Leaf) + '.bin')) -Force }
$Forbidden = @('avcodec-60.dll','avformat-60.dll','avutil-58.dll','swscale-7.dll','swresample-4.dll','avfilter-9.dll')
$PayloadFFmpeg = @(Get-ChildItem $PayloadRoot -Recurse -File | Where-Object { ($_.Name -replace '\.bin$','') -in $Forbidden })
if ($PayloadFFmpeg.Count -ne 0) { throw 'FFmpeg DLL found in onefile payload' }
Compress-Archive -Path "$PayloadRoot\*" -DestinationPath $PayloadZip -Force
$ErrorActionPreference = 'Continue'
& $Py -m nuitka `
  --onefile --assume-yes-for-downloads --mingw64 `
  --output-dir=$Output `
  --output-filename=no_ffmpeg_onefile.exe `
  --include-data-files="$PayloadZip=opencv_payload.zip" `
  --noinclude-dlls=avcodec-60.dll `
  --noinclude-dlls=avformat-60.dll `
  --noinclude-dlls=avutil-58.dll `
  --noinclude-dlls=swscale-7.dll `
  --noinclude-dlls=swresample-4.dll `
  --noinclude-dlls=avfilter-9.dll `
  "$AuditRoot\nuitka\no_ffmpeg_app.py" `
  1> "$AuditRoot\logs\nuitka-onefile-build.stdout.txt" `
  2> "$AuditRoot\logs\nuitka-onefile-build.stderr.txt"
if ($LASTEXITCODE -ne 0) { throw 'Nuitka onefile build failed; see logs' }
