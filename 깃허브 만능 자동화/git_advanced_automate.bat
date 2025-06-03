@echo off
chcp 65001 > nul
title Git 고급 자동 동기화 시스템 v2.0

echo.
echo ============================================================
echo   Git 고급 자동 동기화 시스템 v2.0
echo ============================================================
echo   새로운 기능:
echo   ✅ 자동 merge/rebase 처리
echo   ✅ 충돌 시 자동 에디터 실행  
echo   ✅ 초기 저장소 설정 완전 자동화
echo   ✅ 원격 변경사항 자동 pull 및 merge
echo ============================================================
echo.

REM 필요한 라이브러리 설치 확인
echo 📦 필요한 Python 라이브러리를 확인하고 설치합니다...
pip install gitpython schedule pywin32 > nul 2>&1

if %errorlevel% neq 0 (
    echo ❌ 라이브러리 설치에 실패했습니다. 인터넷 연결을 확인하세요.
    pause
    exit /b 1
)

echo ✅ 라이브러리 설치 완료!
echo.

REM Python 스크립트 실행
echo 🚀 Git 고급 자동 동기화 시스템을 시작합니다...
python "%~dp0git_advanced_automate.py" --from-bat

pause