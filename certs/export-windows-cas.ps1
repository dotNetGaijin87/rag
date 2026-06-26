# Exports all trusted root CAs from the Windows certificate store into a single
# PEM bundle (windows-roots.crt) that the Docker containers can trust. This is
# needed when a corporate proxy / antivirus performs TLS inspection, because the
# containers don't otherwise trust the proxy's root certificate.
#
# Run from the repository root (PowerShell):
#   powershell -ExecutionPolicy Bypass -File certs\export-windows-cas.ps1
#
# Then `docker compose up` — Ollama (via SSL_CERT_DIR=/certs) will trust them.

$ErrorActionPreference = "Stop"
$out = Join-Path $PSScriptRoot "windows-roots.crt"
$stores = @("Cert:\LocalMachine\Root", "Cert:\CurrentUser\Root")

$lines = New-Object System.Collections.Generic.List[string]
$count = 0
foreach ($store in $stores) {
    if (-not (Test-Path $store)) { continue }
    Get-ChildItem $store | ForEach-Object {
        $lines.Add("-----BEGIN CERTIFICATE-----")
        $lines.Add([Convert]::ToBase64String($_.RawData, 'InsertLineBreaks'))
        $lines.Add("-----END CERTIFICATE-----")
        $count++
    }
}

Set-Content -Path $out -Value $lines -Encoding ascii
Write-Host "Wrote $count certificate(s) to $out"
Write-Host "Now run: docker compose up"
