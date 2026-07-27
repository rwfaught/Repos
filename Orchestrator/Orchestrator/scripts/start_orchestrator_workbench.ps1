$Start = Get-Date
"START_TIME=$($Start.ToString('o'))"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $ProjectRoot
$WorkbenchUrl = 'http://127.0.0.1:8766/workbench'
"Operator Workbench: $WorkbenchUrl"
Start-Process $WorkbenchUrl
python -m orchestrator.operator_workbench --port 8766
$End = Get-Date
"END_TIME=$($End.ToString('o'))"
"ELAPSED=$($End - $Start)"
