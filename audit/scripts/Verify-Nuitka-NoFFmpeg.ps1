$ErrorActionPreference = 'Stop'
$AuditRoot = Split-Path $PSScriptRoot -Parent
$Dist = (Resolve-Path "$AuditRoot\nuitka\short-build\no_ffmpeg_app.dist").Path
$Exe = Join-Path $Dist 'no_ffmpeg_app.exe'
$Video = (Resolve-Path "$AuditRoot\media\vp9.mkv").Path
$ExternalFFmpeg = (Resolve-Path "$AuditRoot\prefix\ffmpeg\bin").Path
$EmptyFFmpeg = "$AuditRoot\nuitka\empty-ffmpeg"
New-Item -ItemType Directory -Force $EmptyFFmpeg | Out-Null
$Names = @('avcodec-60.dll','avformat-60.dll','avutil-58.dll','swscale-7.dll','swresample-4.dll','avfilter-9.dll')
$Bundled = @(Get-ChildItem $Dist -Recurse -File | Where-Object { $_.Name -in $Names })
$env:PATH = 'C:\Windows\System32'
$ErrorActionPreference = 'Continue'
& $Exe $Video $ExternalFFmpeg 1> "$AuditRoot\logs\nuitka-run-external-ffmpeg.stdout.txt" 2> "$AuditRoot\logs\nuitka-run-external-ffmpeg.stderr.txt"
$SuccessCode = $LASTEXITCODE
& $Exe $Video $EmptyFFmpeg 1> "$AuditRoot\logs\nuitka-run-no-ffmpeg.stdout.txt" 2> "$AuditRoot\logs\nuitka-run-no-ffmpeg.stderr.txt"
$NoFFmpegCode = $LASTEXITCODE
$Result = [ordered]@{
  executable = $Exe
  executable_sha256 = (Get-FileHash $Exe -Algorithm SHA256).Hash.ToLower()
  distribution_file_count = @(Get-ChildItem $Dist -Recurse -File).Count
  distribution_bytes = (Get-ChildItem $Dist -Recurse -File | Measure-Object Length -Sum).Sum
  bundled_ffmpeg_dll_count = $Bundled.Count
  bundled_ffmpeg_dlls = @($Bundled | ForEach-Object { $_.FullName })
  sanitized_path = $env:PATH
  external_ffmpeg_dir = $ExternalFFmpeg
  with_external_ffmpeg_exit_code = $SuccessCode
  with_external_ffmpeg_stdout = [string](Get-Content "$AuditRoot\logs\nuitka-run-external-ffmpeg.stdout.txt" -Raw)
  without_ffmpeg_exit_code = $NoFFmpegCode
  without_ffmpeg_stderr = [string](Get-Content "$AuditRoot\logs\nuitka-run-no-ffmpeg.stderr.txt" -Raw)
  pass = ($Bundled.Count -eq 0 -and $SuccessCode -eq 0 -and $NoFFmpegCode -ne 0)
}
$Result | ConvertTo-Json -Depth 4 | Set-Content "$AuditRoot\logs\nuitka-verification.json" -Encoding utf8
$Result | ConvertTo-Json -Depth 4
if (-not $Result.pass) { exit 1 }
