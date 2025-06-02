@echo off
chcp 65001 >nul
title Git 고급 자동 동기화 시스템 설치 도구

echo.
echo ======================================================
echo    🚀 Git 고급 자동 동기화 시스템 v2.0 설치 도구
echo ======================================================
echo.
echo ✨ 이 도구는 다음 작업을 수행합니다:
echo    • Python 필수 패키지 설치
echo    • Git 설치 확인
echo    • 시작프로그램 등록 (선택사항)
echo    • 설정 파일 생성
echo.
pause

echo.
echo 📦 1단계: 필수 패키지 설치 중...
echo ======================================================
pip install gitpython schedule pywin32
if %errorlevel% neq 0 (
    echo ❌ 패키지 설치 실패. Python이 설치되어 있는지 확인하세요.
    echo 💡 https://www.python.org에서 Python을 다운로드하세요.
    pause
    exit /b 1
)
echo ✅ 패키지 설치 완료!

echo.
echo 🔍 2단계: Git 설치 확인 중...
echo ======================================================
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git이 설치되어 있지 않습니다.
    echo 💡 https://git-scm.com에서 Git을 다운로드하세요.
    echo 💡 Git 설치 후 이 스크립트를 다시 실행하세요.
    pause
    exit /b 1
)
echo ✅ Git 설치 확인 완료!

echo.
echo ⚙️ 3단계: 설정 정보 입력
echo ======================================================
set /p REPO_PATH="📁 저장소 경로를 입력하세요 (예: C:\Users\YourName\Documents\MyRepo): "
set /p REMOTE_URL="🌐 GitHub 저장소 URL을 입력하세요 (예: https://github.com/username/repo.git): "
set /p BRANCH="🌿 브랜치명을 입력하세요 (기본값: main): "

if "%BRANCH%"=="" set BRANCH=main

echo.
echo 📋 입력된 정보:
echo    저장소 경로: %REPO_PATH%
echo    GitHub URL: %REMOTE_URL%
echo    브랜치: %BRANCH%
echo.
set /p CONFIRM="이 정보가 맞습니까? (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo ❌ 설정이 취소되었습니다.
    pause
    exit /b 0
)

echo.
echo 📝 4단계: 설정 파일 수정 중...
echo ======================================================

:: Python 파일에서 설정 부분 찾아서 수정
powershell -Command "(Get-Content 'git_advanced_sync.py') -replace 'repo_path = r\"C:\\Users\\YourName\\Documents\\MyRepo\"', 'repo_path = r\"%REPO_PATH%\"' -replace 'remote_url = \"https://github.com/username/repository.git\"', 'remote_url = \"%REMOTE_URL%\"' -replace 'branch = \"main\"', 'branch = \"%BRANCH%\"' | Set-Content 'git_advanced_sync_configured.py'"

if exist "git_advanced_sync_configured.py" (
    echo ✅ 설정 파일 생성 완료: git_advanced_sync_configured.py
) else (
    echo ❌ 설정 파일 생성 실패
    pause
    exit /b 1
)

echo.
echo 🔧 5단계: 시작프로그램 등록 (선택사항)
echo ======================================================
echo 💡 시작프로그램에 등록하면 컴퓨터 부팅 시 자동으로 Git 동기화가 시작됩니다.
set /p AUTO_START="시작프로그램에 등록하시겠습니까? (y/N): "

if /i "%AUTO_START%"=="y" (
    echo 📁 시작프로그램 폴더를 엽니다...
    echo 💡 열린 폴더에 'Git_Advanced_Automate.vbs' 파일의 바로가기를 복사하세요.
    start shell:startup
    echo.
    echo 📋 수동 등록 방법:
    echo    1. Git_Advanced_Automate.vbs 파일을 우클릭
    echo    2. '바로가기 만들기' 선택
    echo    3. 생성된 바로가기를 열린 시작프로그램 폴더로 복사
    pause
)

echo.
echo 🧪 6단계: 테스트 실행
echo ======================================================
echo 설정된 Git 동기화 시스템을 테스트 실행하시겠습니까?
set /p TEST_RUN="테스트 실행 (y/N): "

if /i "%TEST_RUN%"=="y" (
    echo 🚀 테스트 실행 중... (Ctrl+C로 중단 가능)
    python git_advanced_sync_configured.py
)

echo.
echo ======================================================
echo 🎉 Git 고급 자동 동기화 시스템 설치 완료!
echo ======================================================
echo.
echo 📁 생성된 파일:
echo    • git_advanced_sync_configured.py (설정 완료된 메인 스크립트)
echo    • Git_Advanced_Automate.vbs (시작프로그램용 런처)
echo.
echo 🚀 사용 방법:
echo    • 수동 실행: python git_advanced_sync_configured.py
echo    • 백그라운드 실행: Git_Advanced_Automate.vbs 더블클릭
echo    • 서비스 설치: python git_advanced_sync_configured.py --service install
echo.
echo 💡 주요 기능:
echo    ✅ 자동 폴더 생성 및 저장소 초기화
echo    ✅ 원격 저장소 자동 클론
echo    ✅ 충돌 발생 시 자동으로 에디터 열기
echo    ✅ 3-way merge 및 rebase 자동 처리
echo    ✅ 10분마다 자동 동기화
echo.
echo 📚 문제 발생 시:
echo    • 로그 파일 확인: logs/git_advanced_sync_YYYYMMDD.log
echo    • Git 권한 확인 (HTTPS: Personal Access Token, SSH: 키 등록)
echo    • 방화벽 및 네트워크 연결 확인
echo.
pause