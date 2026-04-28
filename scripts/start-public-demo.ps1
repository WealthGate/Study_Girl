param(
    [string]$Port = "8000"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$env:DEBUG = "True"
$env:ALLOWED_HOSTS = "127.0.0.1,localhost,.trycloudflare.com,.loca.lt"
$env:CSRF_TRUSTED_ORIGINS = "https://*.trycloudflare.com,https://*.loca.lt"

Write-Host "Preparing Study_girl demo database..."
python manage.py migrate --noinput
python manage.py seed_demo

$localUrl = "http://127.0.0.1:$Port/"
$serverIsRunning = $false
try {
    $response = Invoke-WebRequest -Uri $localUrl -UseBasicParsing -TimeoutSec 3
    $serverIsRunning = $response.StatusCode -eq 200
} catch {
    $serverIsRunning = $false
}

if (-not $serverIsRunning) {
    Write-Host "Starting local Daphne server at $localUrl"
    Start-Process `
        -FilePath python `
        -ArgumentList @("-m", "daphne", "study_girl.asgi:application", "--bind", "127.0.0.1", "--port", $Port) `
        -WorkingDirectory $root `
        -RedirectStandardOutput "$root\daphne.out.log" `
        -RedirectStandardError "$root\daphne.err.log" `
        -WindowStyle Hidden

    Start-Sleep -Seconds 3
} else {
    Write-Host "Local server is already running at $localUrl"
}

Write-Host ""
Write-Host "Starting a temporary public tunnel."
Write-Host "Keep this PowerShell window open while students are testing."
Write-Host "Share the https://...trycloudflare.com URL that appears below."
Write-Host ""

$toolsDir = Join-Path $root "tools"
$cloudflared = Join-Path $toolsDir "cloudflared.exe"

if (-not (Get-Command cloudflared -ErrorAction SilentlyContinue) -and -not (Test-Path $cloudflared)) {
    New-Item -ItemType Directory -Force -Path $toolsDir | Out-Null
    Write-Host "Downloading Cloudflare Tunnel helper..."
    curl.exe -L `
        -o $cloudflared `
        "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
}

if (Get-Command cloudflared -ErrorAction SilentlyContinue) {
    cloudflared tunnel --url $localUrl
} else {
    & $cloudflared tunnel --url $localUrl
}
