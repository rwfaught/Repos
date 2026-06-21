param(
    [Parameter(Mandatory = $true)]
    [string]$DistroName,
    [string]$LinuxUser = "roger",
    [Parameter(Mandatory = $true)]
    [string]$RunTimestamp
)

$logRoot = "/home/$LinuxUser/openclaw_install/logs/$RunTimestamp"
& wsl.exe --distribution $DistroName --user $LinuxUser -- bash -lc "tail -n 80 -F '$logRoot/runner.log' '$logRoot/bootstrap.log' '$logRoot/openclaw_npm_install.log' 2>/dev/null"
exit $LASTEXITCODE
