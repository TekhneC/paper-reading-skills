param(
    [string]$HostName = "127.0.0.1",
    [int]$Port = 8765,
    [string]$Python = ""
)

$ErrorActionPreference = "Stop"
$SiteDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $SiteDir

Set-Location $RepoRoot

if (-not $Python) {
    $ConfigPath = Join-Path $RepoRoot "config\paths.toml"
    if (Test-Path $ConfigPath) {
        $RuntimeLine = Get-Content $ConfigPath | Where-Object { $_ -match '^\s*python_path\s*=' } | Select-Object -First 1
        if ($RuntimeLine -and $RuntimeLine -match '"([^"]+)"') {
            $Candidate = $Matches[1]
            if (Test-Path $Candidate) {
                $Python = $Candidate
            }
        }
    }
}

if (-not $Python) {
    $Python = "C:\Program Files (x86)\MYSYS2\ucrt64\bin\python.exe"
}

& $Python "site\server.py" --host $HostName --port $Port
