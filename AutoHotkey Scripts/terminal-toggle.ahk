#Requires AutoHotkey v2.0

app := "wt.exe"  ; Windows Terminal executable

if WinExist("ahk_exe " app)
{
    WinActivate
}
else
{
    Run(app)
}