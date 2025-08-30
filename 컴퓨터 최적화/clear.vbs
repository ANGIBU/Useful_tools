' clear.vbs

Dim WshShell, strCommand, strScriptPath

Set WshShell = CreateObject("WScript.Shell")

' 현재 스크립트 경로 가져오기
strScriptPath = Replace(WScript.ScriptFullName, WScript.ScriptName, "")

' Python 스크립트 경로
strCommand = "python """ & strScriptPath & "clear.py"" --background"

' 백그라운드에서 실행 (창 숨김)
WshShell.Run strCommand, 0, False

Set WshShell = Nothing