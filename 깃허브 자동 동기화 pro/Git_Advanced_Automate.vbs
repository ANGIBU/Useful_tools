' Git 고급 자동 동기화 시스템 VBS 런처 v2.0
' 이 파일을 시작프로그램에 등록하면 부팅 시 자동 실행됩니다.
' 바로가기 생성 후 시작프로그램 폴더에 복사하세요!
'
' 사용법:
' 1. git_advanced_sync.py와 같은 폴더에 이 파일을 저장
' 2. 이 파일의 바로가기 생성
' 3. Win+R -> shell:startup -> 바로가기 복사
' 4. 재부팅 시 자동 실행됩니다.

Set WshShell = CreateObject("WScript.Shell")

' Python 스크립트 경로 (현재 VBS 파일과 같은 폴더)
Dim ScriptPath
ScriptPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & "\git_advanced_sync.py"

' 백그라운드에서 Python 스크립트 실행 (창 숨김)
WshShell.Run "python """ & ScriptPath & """ --from-bat", 0, False