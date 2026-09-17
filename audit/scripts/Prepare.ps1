$ErrorActionPreference = 'Stop'
$AuditRoot = Split-Path $PSScriptRoot -Parent
& "$AuditRoot\.venv\Scripts\python.exe" "$PSScriptRoot\prepare.py"
if ($LASTEXITCODE -ne 0) { throw 'Preparation failed; see logs.' }
