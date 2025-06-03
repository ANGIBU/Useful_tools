' Git_Advanced_Automate.vbs
' Run Git Advanced Auto Sync System in background

Dim WshShell, strCommand, strScriptPath

Set WshShell = CreateObject("WScript.Shell")

' Get current script path
strScriptPath = Replace(WScript.ScriptFullName, WScript.ScriptName, "")

' Python script path
strCommand = "python """ & strScriptPath & "git_advanced_automate.py"" --background"

' Run in background (hide window)
WshShell.Run strCommand, 0, False

Set WshShell = Nothing