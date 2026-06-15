param(
    [string]$HostName = "127.0.0.1",
    [int]$Port = 8765,
    [string]$Python = "C:\Program Files (x86)\MYSYS2\ucrt64\bin\python.exe"
)

$ErrorActionPreference = "Stop"
$SiteDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $SiteDir

Set-Location $RepoRoot
& $Python "site\server.py" --host $HostName --port $Port
