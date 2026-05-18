# Daily snapshot of the wine_vault to GitHub.
# Invoked by the WineVaultDailySnapshot scheduled task.
# Silently no-ops when there are no changes.

$ErrorActionPreference = "Continue"
$vault  = "G:\My Drive\wine_vault"
$logDir = Join-Path $env:LOCALAPPDATA "wine_vault_snapshot"
$log    = Join-Path $logDir "snapshot.log"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

function Log($msg) {
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"), $msg
    Add-Content -Path $log -Value $line
}

if (-not (Test-Path $vault)) { Log "vault path missing: $vault"; exit 1 }
Set-Location -LiteralPath $vault

Log "begin snapshot"

& git add -A
if ($LASTEXITCODE -ne 0) { Log "git add failed ($LASTEXITCODE)"; exit 1 }

& git diff --cached --quiet
if ($LASTEXITCODE -eq 0) { Log "no changes; skipping commit"; exit 0 }

$stamp = Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"
$msg   = "snapshot $stamp"
& git -c user.email="evanakarp@gmail.com" -c user.name="Evan Karp" commit -m $msg 2>&1 | ForEach-Object { Log $_ }
if ($LASTEXITCODE -ne 0) { Log "git commit failed ($LASTEXITCODE)"; exit 1 }

& git push origin main 2>&1 | ForEach-Object { Log $_ }
if ($LASTEXITCODE -ne 0) { Log "git push failed ($LASTEXITCODE)"; exit 1 }

Log "snapshot complete: $msg"
