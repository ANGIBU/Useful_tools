# Git 고급 자동 동기화 시스템 v2.0

🚀 **완전 자동화된 Git 동기화 시스템**으로, 충돌 해결부터 브랜치 관리까지 모든 것을 자동으로 처리합니다.

## ✨ 주요 기능

### 🆕 새로운 기능 (v2.0)
- **자동 폴더 생성 및 초기화** - 경로가 없으면 자동으로 생성
- **원격 저장소 자동 클론** - 저장소가 없으면 자동으로 클론
- **지능형 충돌 해결** - 충돌 발생 시 자동으로 에디터 열기
- **3-way Merge 자동 처리** - 충돌 해결 후 자동 커밋
- **Rebase 자동 Continue** - 리베이스 충돌 해결 후 자동 계속
- **스마트 Pull/Push** - 상황에 맞는 최적화된 동기화

### 🔧 기존 기능
- **10분마다 자동 동기화** - 설정 가능한 간격
- **Windows 서비스 지원** - 백그라운드 실행
- **시작프로그램 등록** - 부팅 시 자동 시작
- **상세한 로깅** - 모든 작업 기록
- **오류 복구** - 자동 재시도 및 복구

## 📋 사전 요구사항

### 필수 설치
1. **Python 3.6+** - [다운로드](https://www.python.org/downloads/)
2. **Git** - [다운로드](https://git-scm.com/downloads)

### 필수 Python 패키지
```bash
pip install gitpython schedule pywin32
```

## 🚀 빠른 시작

### 1. 자동 설치 (권장)
```bash
# 1. 파일 다운로드
git clone https://github.com/your-repo/git-advanced-sync.git
cd git-advanced-sync

# 2. 설치 스크립트 실행
setup_git_advanced.bat
```

### 2. 수동 설정
1. **설정 수정** - `git_advanced_sync.py` 파일에서 다음 부분 수정:
   ```python
   # 278줄과 334줄 근처
   repo_path = r"C:\Users\YourName\Documents\MyRepo"  # 저장소 경로
   remote_url = "https://github.com/username/repository.git"  # GitHub URL
   branch = "main"  # 브랜치명
   ```

2. **실행**
   ```bash
   # 포그라운드 실행 (창 표시)
   python git_advanced_sync.py
   
   # 백그라운드 실행 (창 숨김)
   Git_Advanced_Automate.vbs
   ```

## 🔧 고급 설정

### Windows 서비스 설치
```bash
# 서비스 설치
python git_advanced_sync.py --service install

# 서비스 시작
python git_advanced_sync.py --service start

# 서비스 제거
python git_advanced_sync.py --service remove
```

### 시작프로그램 등록
1. `Git_Advanced_Automate.vbs` 파일 우클릭
2. "바로가기 만들기" 선택
3. `Win + R` → `shell:startup` 입력
4. 생성된 바로가기를 열린 폴더에 복사

## 🛠️ 충돌 해결 프로세스

### 자동 충돌 해결
1. **충돌 감지** - Pull/Push 중 충돌 자동 감지
2. **에디터 열기** - Git Bash의 vim 에디터 자동 실행
3. **충돌 해결** - 사용자가 충돌 마커 수정
4. **자동 처리**:
   - **3-way Merge**: 해결 후 자동 커밋
   - **Rebase**: 해결 후 자동 continue

### 충돌 마커 예시
```
<<<<<<< HEAD
로컬 변경사항
=======
원격 변경사항
>>>>>>> origin/main
```

## 📊 모니터링 및 로그

### 로그 위치
- **로그 폴더**: `logs/`
- **파일명**: `git_advanced_sync_YYYYMMDD.log`

### 로그 레벨
- **INFO**: 일반 작업 정보
- **WARNING**: 경고 (충돌 등)
- **ERROR**: 오류 정보

## 🔒 보안 설정

### HTTPS 인증 (Personal Access Token)
1. GitHub → Settings → Developer settings → Personal access tokens
2. 새 토큰 생성 (repo 권한 필요)
3. URL 형식: `https://username:token@github.com/username/repo.git`

### SSH 인증
1. SSH 키 생성: `ssh-keygen -t rsa -b 4096 -C "your_email@example.com"`
2. GitHub에 공개키 등록
3. URL 형식: `git@github.com:username/repo.git`

## 🚨 문제 해결

### 일반적인 문제들

#### 1. Push 거부됨
```
✅ 자동 해결: 원격 변경사항을 가져온 후 재시도
```

#### 2. 충돌 발생
```
✅ 자동 해결: 에디터가 열리고 충돌 해결 후 자동 처리
```

#### 3. 권한 없음
```
❌ 수동 해결 필요: 
- GitHub 저장소 권한 확인
- Personal Access Token 또는 SSH 키 설정
```

#### 4. Git Bash 없음
```
✅ 자동 해결: 시스템 기본 에디터(메모장) 사용
```

### 디버깅 팁
1. **로그 파일 확인** - 가장 최근 로그 파일 확인
2. **수동 Git 명령어 테스트** - 터미널에서 직접 테스트
3. **네트워크 연결 확인** - 방화벽 및 프록시 설정
4. **권한 확인** - GitHub 저장소 협업자 권한

## 📈 성능 최적화

### 권장 설정
- **동기화 간격**: 10분 (기본값)
- **큰 파일 관리**: Git LFS 사용 권장
- **브랜치 전략**: 개발용 브랜치 분리

### 시스템 요구사항
- **메모리**: 최소 512MB
- **디스크**: 충분한 여유 공간
- **네트워크**: 안정적인 인터넷 연결

## 🎯 사용 시나리오

### 1. 개인 프로젝트 백업
```python
# 문서, 코드 등을 자동으로 GitHub에 백업
repo_path = r"C:\Users\YourName\Documents"
remote_url = "https://github.com/username/backup.git"
```

### 2. 팀 협업 프로젝트
```python
# 팀원들과 실시간 코드 동기화
repo_path = r"C:\Projects\TeamProject"
remote_url = "https://github.com/team/project.git"
```

### 3. 설정 파일 동기화
```python
# 여러 컴퓨터 간 설정 파일 동기화
repo_path = r"C:\Users\YourName\AppData\Roaming\MyApp"
remote_url = "https://github.com/username/config.git"
```

## 🆘 지원 및 기여

### 이슈 신고
문제가 발생하면 다음 정보와 함께 이슈를 신고해주세요:
- 운영체제 및 버전
- Python 버전
- Git 버전
- 오류 로그
- 재현 단계

### 기여 방법
1. Fork 후 개선사항 개발
2. Pull Request 생성
3. 코드 리뷰 및 테스트
4. 병합

## 📝 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

## 📚 참고 자료

- [Git 공식 문서](https://git-scm.com/docs)
- [GitHub 도움말](https://docs.github.com/)
- [GitPython 문서](https://gitpython.readthedocs.io/)
- [Python Schedule 문서](https://schedule.readthedocs.io/)

---

⭐ 이 프로젝트가 도움이 되셨다면 스타를 눌러주세요!

🐛 버그 신고나 기능 요청은 Issues 탭을 이용해주세요.

💡 궁금한 사항은 Discussions에서 질문해주세요.