$ErrorActionPreference = "Stop"

$VirtualPatterns = @('vEthernet', 'WSL', 'Hyper-V', 'VirtualBox', 'Docker', 'Loopback')

$Candidates = Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
    $_.IPAddress -ne '127.0.0.1' -and
    $_.IPAddress -notlike '169.254.*' -and
    $_.PrefixOrigin -in @('Dhcp', 'Manual')
} | Where-Object {
    $alias = $_.InterfaceAlias
    -not ($VirtualPatterns | Where-Object { $alias -like "*$_*" })
}

# Prefer DHCP (real network) over Manual (static/virtual)
$HostIP = ($Candidates | Sort-Object { if ($_.PrefixOrigin -eq 'Dhcp') { 0 } else { 1 } } | Select-Object -First 1).IPAddress

if (-not $HostIP) {
    Write-Host "ERROR: Could not detect the machine's IP address." -ForegroundColor Red
    Write-Host "Please create a .env file manually:"
    Write-Host "  Set-Content .env 'HOST_IP=<your-ip>'"
    exit 1
}

Set-Content -Path ".env" -Value "HOST_IP=$HostIP"
Write-Host "Detected IP: $HostIP"
Write-Host "Starting AAS services..."

docker compose up -d

Write-Host ""
Write-Host "All services started. Access the Web UI at:"
Write-Host "  http://${HostIP}:3000" -ForegroundColor Green
