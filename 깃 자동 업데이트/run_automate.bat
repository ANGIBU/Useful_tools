@echo off
echo 자동 동기화를 시작합니다...
start cmd /k python "파이썬 경로를 입력하세요요"
echo Python 스크립트가 새 창에서 실행되었습니다.
echo 이 창은 3초 후 자동으로 닫힙니다.
timeout /t 3 /nobreak > nul
exit