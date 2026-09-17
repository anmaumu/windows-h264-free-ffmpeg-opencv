$ErrorActionPreference = 'Stop'
$AuditRoot = Split-Path $PSScriptRoot -Parent
$Dist = "$AuditRoot\nuitka\short-build\no_ffmpeg_app.dist"
$Cv2Target = "$Dist\cv2\python-3.12"
New-Item -ItemType Directory -Force $Cv2Target | Out-Null
Copy-Item "$AuditRoot\.venv\Lib\site-packages\cv2\python-3.12\cv2.cp312-win_amd64.pyd" $Cv2Target -Force
Copy-Item "$AuditRoot\prefix\opencv\x64\mingw\bin\*.dll" $Dist -Force
Copy-Item "$AuditRoot\prefix\opencv\x64\mingw\bin\*.dll" $Cv2Target -Force
Copy-Item 'C:\Program Files (x86)\mingw64\bin\libgcc_s_seh-1.dll' $Dist -Force
Copy-Item 'C:\Program Files (x86)\mingw64\bin\libstdc++-6.dll' $Dist -Force
Copy-Item 'C:\Program Files (x86)\mingw64\bin\libwinpthread-1.dll' $Dist -Force
Copy-Item 'C:\Program Files (x86)\mingw64\bin\libgcc_s_seh-1.dll' $Cv2Target -Force
Copy-Item 'C:\Program Files (x86)\mingw64\bin\libstdc++-6.dll' $Cv2Target -Force
Copy-Item 'C:\Program Files (x86)\mingw64\bin\libwinpthread-1.dll' $Cv2Target -Force
$Forbidden = @('avcodec-60.dll','avformat-60.dll','avutil-58.dll','swscale-7.dll','swresample-4.dll','avfilter-9.dll')
$Found = @(Get-ChildItem $Dist -Recurse -File | Where-Object { $_.Name -in $Forbidden })
if ($Found.Count -ne 0) { throw "FFmpeg DLL was bundled: $($Found.FullName -join ', ')" }
