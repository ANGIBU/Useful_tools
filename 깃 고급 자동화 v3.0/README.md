<img src="https://www.spriters-resource.com/resources/sheet_icons/168/171517.gif?updated=1648938576" alt="도트 커비 5" width="100"/>

## 📁 `Git 고급 자동화 시스템 v3.0 (Git Advanced Auto Sync)`

### 📌 목적  
완전 자동화된 Git 동기화 시스템으로 코드 백업, 충돌 해결, 팀 협업을 원클릭으로 처리합니다.

### 📄 구성 파일  
- `git_advanced_automate.py`  
  - 메인 프로그램 (필수 모듈 자동 설치 포함)
  - 자동 merge/rebase 처리 및 충돌 해결
  - 커밋 메시지 포맷: `자동 커밋: YYYY-MM-DD HH:MM:SS (N개 파일 변경)`

- `Git_Advanced_Automate.bat`  
  - 프로그램 실행용 배치 파일
  - Python 모듈 자동 설치 및 실행

- `Git_Advanced_Automate.vbs`  
  - 백그라운드 실행용 (시작프로그램 등록 가능)

- `requirements.txt`  
  - 필요한 Python 모듈 목록 (자동 생성)

- `Git_자동화_시스템_초보자_가이드.md`  
  - 초보자를 위한 상세 사용 가이드

### ⚙️ 주요 특징
- **완전 자동 초기화**: 폴더 생성, Git init, 원격 clone 자동 처리
- **필수 모듈 자동 설치**: `gitpython`, `schedule`, `pywin32` 자동 확인 및 설치
- **양방향 동기화**: 원격 변경사항 자동 pull + 로컬 변경사항 push
- **충돌 자동 해결**: 충돌 시 Git Bash에서 vim 에디터 자동 실행
- **3-way merge/rebase 지원**: 상황별 자동 감지 및 처리
- **커밋 메시지 커스터마이징**: 접두사, 형식, 파일 개수 표시 설정 가능
- **스케줄링**: 설정 가능한 간격으로 자동 동기화 (기본 10분)
- **서비스 모드**: Windows 서비스로 설치 가능
- **로그 기록**: 상세한 작업 로그 자동 생성

### 🚀 새로운 기능 (v3.0)
- 필요 모듈 없으면 자동 설치 후 프로그램 재시작
- 설치 실패 시 pip 업그레이드 후 재시도
- requirements.txt 파일 자동 생성
- 초보자 친화적 오류 메시지 및 해결 방법 안내

### ⚙️ 설정 방법
`git_advanced_automate.py` 파일의 CONFIG 섹션 수정:
```python
REPO_PATH = r"C:\MyProject"  # 로컬 저장소 경로
REMOTE_URL = "https://github.com/username/repository.git"  # GitHub 저장소
BRANCH = "main"  # 브랜치명
SYNC_INTERVAL = 10  # 동기화 간격 (분)
COMMIT_MESSAGE_TEMPLATE = "자동 커밋: {timestamp}"  # 커밋 메시지 형식
CUSTOM_COMMIT_PREFIX = "[AUTO]"  # 커밋 메시지 앞부분
```

### 💡 사용 시나리오
- **개인 개발**: 작업 중 자동 백업으로 데이터 손실 방지
- **팀 협업**: 충돌 발생 시 자동 해결 가이드
- **초보자**: Git 명령어 몰라도 안전한 버전 관리
- **자동화**: 한 번 설정 후 완전 자동 운영