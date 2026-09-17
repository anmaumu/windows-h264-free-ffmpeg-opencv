$ErrorActionPreference = 'Stop'
$AuditRoot = Split-Path $PSScriptRoot -Parent
$Exe = (Resolve-Path "$AuditRoot\nuitka\onefile-build\no_ffmpeg_onefile.exe").Path
$Video = (Resolve-Path "$AuditRoot\media\vp9.mkv").Path
$FFmpegDir = (Resolve-Path "$AuditRoot\prefix\ffmpeg\bin").Path
$EmptyDir = (Resolve-Path "$AuditRoot\nuitka\empty-ffmpeg").Path
$LogDir = "$AuditRoot\logs"
$Required = @('avcodec-60.dll','avformat-60.dll','avutil-58.dll','swscale-7.dll')

$OldPath = $env:PATH
try {
  $env:PATH = 'C:\Windows\System32'
  & $Exe $Video $FFmpegDir 1> "$LogDir\nuitka-onefile-run-external.stdout.txt" 2> "$LogDir\nuitka-onefile-run-external.stderr.txt"
  $ExternalExit = $LASTEXITCODE
  & $Exe $Video $EmptyDir 1> "$LogDir\nuitka-onefile-run-no-ffmpeg.stdout.txt" 2> "$LogDir\nuitka-onefile-run-no-ffmpeg.stderr.txt"
  $MissingExit = $LASTEXITCODE
} finally {
  $env:PATH = $OldPath
}

$Run = Get-Content "$LogDir\nuitka-onefile-run-external.stdout.txt" -Raw | ConvertFrom-Json
$LoadedPathsValid = $true
foreach ($Name in $Required) {
  $Actual = $Run.loaded_ffmpeg_dlls.$Name
  $Expected = Join-Path $FFmpegDir $Name
  if (-not $Actual -or ([IO.Path]::GetFullPath($Actual) -ne [IO.Path]::GetFullPath($Expected))) {
    $LoadedPathsValid = $false
  }
}
$AdjacentFFmpeg = @(Get-ChildItem (Split-Path $Exe) -File | Where-Object Name -Match '^(avcodec|avformat|avutil|swscale|swresample|avfilter).*\.dll$')
$Result = [ordered]@{
  pass = ($ExternalExit -eq 0 -and $MissingExit -ne 0 -and $Run.backend -eq 'FFMPEG' -and
          $Run.valid_frames -eq 100 -and $Run.frames_valid -and $LoadedPathsValid -and $AdjacentFFmpeg.Count -eq 0)
  exe = $Exe
  exe_sha256 = (Get-FileHash $Exe -Algorithm SHA256).Hash
  exe_bytes = (Get-Item $Exe).Length
  adjacent_ffmpeg_dll_count = $AdjacentFFmpeg.Count
  sanitized_path = 'C:\Windows\System32'
  external_run_exit = $ExternalExit
  missing_ffmpeg_run_exit = $MissingExit
  backend = $Run.backend
  valid_frames = $Run.valid_frames
  cv2_file = $Run.cv2_file
  loaded_ffmpeg_dlls = $Run.loaded_ffmpeg_dlls
  loaded_paths_match_external_dir = $LoadedPathsValid
}
$Result | ConvertTo-Json -Depth 5 | Set-Content "$LogDir\nuitka-onefile-verification.json" -Encoding UTF8
$Result | ConvertTo-Json -Depth 5
if (-not $Result.pass) { exit 1 }
