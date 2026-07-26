$Start = Get-Date
"START_TIME=$($Start.ToString('o'))"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $ProjectRoot

$CockpitUrl = 'http://127.0.0.1:8765/'
Start-Process $CockpitUrl
python -m orchestrator.founder_cockpit --serve --port 8765

$End = Get-Date
"END_TIME=$($End.ToString('o'))"
"ELAPSED=$($End - $Start)"
