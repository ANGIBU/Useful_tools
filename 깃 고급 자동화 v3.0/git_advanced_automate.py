# git_advanced_automate.py

"""
Git 고급 자동 동기화 서비스 v3.1

새로운 기능:
✔️ 필요 모듈 자동 설치 (requirements.txt 기반)
✔️ 자동 merge/rebase 처리
✔️ 충돌 발생 시 자동으로 에디터 실행
✔️ 3-way merge와 rebase 상황 자동 감지 및 처리
✔️ 초기 저장소 설정 완전 자동화 (폴더 생성, clone, init)
✔️ 원격 변경사항 자동 pull 및 merge
✔️ 충돌 해결 후 자동 commit/continue
✔️ unrelated histories 오류 자동 해결
📌 설정 위치: 139-157줄 (CONFIG 섹션)
📌 경로 설정 후 vbs파일에 바로가기 형식을 생성하여 시작프로그램으로 등록하세요
"""

# 

import os
import sys
import subprocess
import time
import traceback
import tempfile
from datetime import datetime
from pathlib import Path

# 필요한 모듈 자동 설치 함수
def check_and_install_requirements():
    """필요한 모듈을 확인하고 자동으로 설치"""
    required_modules = {
        'git': 'gitpython>=3.1.40',
        'schedule': 'schedule>=1.2.0',
        'win32service': 'pywin32>=306',
        'win32serviceutil': 'pywin32>=306',
        'win32event': 'pywin32>=306',
        'servicemanager': 'pywin32>=306'
    }
    
    missing_modules = []
    
    print("🔍 필요한 모듈을 확인하는 중...")
    
    # 각 모듈 확인
    for module, package in required_modules.items():
        try:
            __import__(module)
            print(f"✅ {module} - 설치됨")
        except ImportError:
            print(f"❌ {module} - 누락됨")
            if package not in missing_modules:
                missing_modules.append(package)
    
    # 누락된 모듈 설치
    if missing_modules:
        print(f"\n📦 누락된 모듈을 설치합니다: {', '.join(missing_modules)}")
        
        for package in missing_modules:
            try:
                print(f"⬇️ 설치 중: {package}")
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package
                ], capture_output=True, text=True, check=True)
                
                print(f"✅ {package} 설치 완료")
                
            except subprocess.CalledProcessError as e:
                print(f"❌ {package} 설치 실패: {e}")
                print(f"오류 출력: {e.stderr}")
                
                # pip 업그레이드 시도
                print("🔄 pip를 업그레이드하고 다시 시도합니다...")
                try:
                    subprocess.run([
                        sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
                    ], check=True, capture_output=True)
                    
                    subprocess.run([
                        sys.executable, '-m', 'pip', 'install', package
                    ], check=True, capture_output=True)
                    
                    print(f"✅ {package} 설치 완료 (재시도)")
                    
                except subprocess.CalledProcessError as e2:
                    print(f"💥 {package} 설치 최종 실패: {e2}")
                    return False
        
        print("\n🔄 모듈 설치가 완료되었습니다. 프로그램을 재시작합니다...")
        time.sleep(2)
        
        # 프로그램 재시작
        subprocess.Popen([sys.executable] + sys.argv)
        sys.exit(0)
    
    else:
        print("✅ 모든 필요한 모듈이 설치되어 있습니다.\n")
    
    return True

# requirements.txt 자동 생성
def create_requirements_file():
    """requirements.txt 파일 자동 생성"""
    script_dir = Path(__file__).parent
    requirements_path = script_dir / "requirements.txt"
    
    if not requirements_path.exists():
        print("📝 requirements.txt 파일을 생성합니다...")
        requirements_content = """gitpython>=3.1.40
schedule>=1.2.0
pywin32>=306"""
        
        with open(requirements_path, 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        
        print(f"✅ requirements.txt 파일이 생성되었습니다: {requirements_path}")

# 시작 시 모듈 확인 및 설치
print("🚀 Git 고급 자동 동기화 시스템 v3.1 시작")
print("="*60)

create_requirements_file()
if not check_and_install_requirements():
    print("💥 필수 모듈 설치에 실패했습니다. 프로그램을 종료합니다.")
    input("Enter를 눌러 종료하세요...")
    sys.exit(1)

# 이제 모든 모듈이 설치되었으므로 import
from git import Repo, InvalidGitRepositoryError
import schedule
import servicemanager
import socket
import win32event
import win32service
import win32serviceutil
import shutil

# ===============================================

# CONFIG 섹션 - 여기만 수정하세요
REPO_PATH = r"파일경로"  # 로컬 저장소 경로
REMOTE_URL = "깃허브 주소.git"  # 깃허브 저장소 URL (.git 확장자 포함)
BRANCH = "브랜치"  # 브랜치명
SYNC_INTERVAL = 10  # 동기화 간격 (분)
AUTO_RESOLVE_CONFLICTS = True  # 충돌 시 자동 에디터 실행 여부

# VS Code 호환 설정
AUTO_COMMIT = True  # False로 설정하면 VS Code에서 수동 커밋 가능
VSCODE_COMPATIBLE = False  # True로 설정하면 VS Code 워크플로우 우선

# 커밋 메시지 설정
COMMIT_MESSAGE_TEMPLATE = "커밋된 시간: {timestamp}"  # {timestamp}는 자동으로 시간으로 대체
MERGE_MESSAGE_TEMPLATE = "병합한 시간: {timestamp}"  # 병합 커밋 메시지
CUSTOM_COMMIT_PREFIX = "메세지 | "  # 커밋 메시지 앞에 붙일 접두사 (예: "[AUTO]", "[BOT]")

# ===============================================

INCLUDE_FILE_COUNT = True
from_bat = "--from-bat" in sys.argv

class GitAdvancedAutoSync:
    def __init__(self, repo_path, remote_url, branch="main"):
        self.repo_path = Path(repo_path)
        self.remote_url = remote_url
        self.branch = branch
        self.repo = None
        
        # 초기 설정 및 저장소 준비
        self.setup_repository()

    def setup_repository(self):
        """저장소 초기 설정 및 자동화"""
        try:
            print(f"저장소 설정 시작: {self.repo_path}")
            
            # 1. 디렉터리 존재 확인 및 생성
            if not self.repo_path.exists():
                print(f"디렉터리 생성: {self.repo_path}")
                self.repo_path.mkdir(parents=True, exist_ok=True)

            # 2. Git 저장소 확인 및 초기화
            if not (self.repo_path / ".git").exists():
                print("Git 저장소가 없습니다. 원격 저장소에서 클론을 시도합니다...")
                
                # 원격 저장소 클론 시도
                if self.clone_repository():
                    print("원격 저장소 클론 완료!")
                else:
                    print("클론 실패. 새 저장소를 초기화합니다...")
                    self.init_new_repository()
            else:
                # 기존 저장소 로드
                self.repo = Repo(self.repo_path)
                print("기존 Git 저장소를 로드했습니다.")

            # 3. 원격 저장소 설정 확인
            self.setup_remote()
            
            # 4. 브랜치 설정
            self.ensure_branch()
            
            print("저장소 설정 완료!")
            
        except Exception as e:
            print(f"Repository setup failed: {str(e)}")
            print(traceback.format_exc())
            raise

    def clone_repository(self):
        """원격 저장소 클론"""
        try:
            # 빈 디렉터리인지 확인
            if any(self.repo_path.iterdir()):
                print("디렉터리가 비어있지 않습니다. 클론을 건너뜁니다.")
                return False
                
            print(f"클론 시작: {self.remote_url}")
            self.repo = Repo.clone_from(self.remote_url, self.repo_path, branch=self.branch)
            return True
            
        except Exception as e:
            print(f"Clone failed: {str(e)}")
            return False

    def init_new_repository(self):
        """새 저장소 초기화"""
        try:
            print("새 Git 저장소 초기화...")
            self.repo = Repo.init(self.repo_path)
            
            # README.md 파일 생성
            readme_path = self.repo_path / "README.md"
            if not readme_path.exists():
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {self.repo_path.name}\n\n자동 생성된 Git 저장소입니다.\n")
                print("README.md 파일을 생성했습니다.")
            
        except Exception as e:
            print(f"Repository initialization failed: {str(e)}")
            raise

    def setup_remote(self):
        """원격 저장소 설정"""
        try:
            if "origin" in [remote.name for remote in self.repo.remotes]:
                origin = self.repo.remote("origin")
                current_url = next(origin.urls)
                if current_url != self.remote_url:
                    origin.set_url(self.remote_url)
                    print("원격 저장소 URL이 업데이트되었습니다.")
            else:
                self.repo.create_remote("origin", self.remote_url)
                print("원격 저장소 'origin'이 생성되었습니다.")
                
        except Exception as e:
            print(f"Remote setup failed: {str(e)}")

    def ensure_branch(self):
        """브랜치 확인 및 설정"""
        try:
            current_branch = self.repo.active_branch.name if self.repo.heads else None
            
            local_branches = [b.name for b in self.repo.branches]

            if self.branch not in local_branches:
                if self.repo.heads:  # 기존 브랜치가 있는 경우
                    self.repo.git.checkout("-b", self.branch)
                else:  # 첫 커밋이 없는 경우
                    print(f"Will create branch '{self.branch}' after first commit")
                    
            elif current_branch != self.branch:
                self.repo.git.checkout(self.branch)

            return True
        except Exception as e:
            print(f"Error ensuring branch: {str(e)}")
            return False

    def is_merge_in_progress(self):
        """병합이 진행 중인지 확인"""
        merge_head = self.repo_path / ".git" / "MERGE_HEAD"
        return merge_head.exists()

    def is_rebase_in_progress(self):
        """리베이스가 진행 중인지 확인"""
        rebase_dir = self.repo_path / ".git" / "rebase-merge"
        rebase_apply = self.repo_path / ".git" / "rebase-apply"
        return rebase_dir.exists() or rebase_apply.exists()

    def get_conflicted_files(self):
        """충돌이 발생한 파일 목록 반환"""
        try:
            # Git status로 충돌 파일 확인
            result = self.repo.git.status("--porcelain")
            conflicted_files = []
            
            for line in result.split('\n'):
                if line.startswith('UU ') or line.startswith('AA ') or line.startswith('DD '):
                    file_path = line[3:].strip()
                    conflicted_files.append(file_path)
                    
            return conflicted_files
        except Exception as e:
            print(f"Error getting conflicted files: {str(e)}")
            return []

    def resolve_conflicts_interactive(self, conflicted_files):
        """충돌 파일을 대화형으로 해결"""
        if not conflicted_files:
            return True
            
        print(f"\n충돌이 발생한 파일들: {', '.join(conflicted_files)}")
        print("충돌 해결을 위해 에디터를 실행합니다...")
        
        try:
            for file_path in conflicted_files:
                full_path = self.repo_path / file_path
                print(f"\n충돌 파일 편집: {file_path}")
                print("편집기에서 충돌 마커(<<<<<<, ======, >>>>>>)를 제거하고 파일을 저장한 후 종료하세요.")
                
                # Git Bash에서 vim으로 파일 편집
                cmd = f'start "Git Bash" "C:\\Program Files\\Git\\bin\\bash.exe" -c "cd \\"{self.repo_path}\\" && vim \\"{file_path}\\"; read -p \\"편집 완료 후 Enter를 누르세요...\\" "'
                
                try:
                    subprocess.run(cmd, shell=True, check=True)
                    
                    # 사용자가 편집을 완료했는지 확인
                    while True:
                        user_input = input(f"\n{file_path} 편집을 완료하셨나요? (y/n): ").lower()
                        if user_input == 'y':
                            # 파일을 staging area에 추가
                            self.repo.git.add(file_path)
                            print(f"{file_path} 충돌 해결 완료!")
                            break
                        elif user_input == 'n':
                            print("편집을 다시 시도하세요.")
                            subprocess.run(cmd, shell=True, check=True)
                        else:
                            print("y 또는 n을 입력하세요.")
                            
                except subprocess.CalledProcessError as e:
                    print(f"Editor execution failed: {str(e)}")
                    print(f"에디터 실행 실패: {file_path}")
                    return False
                    
            return True
            
        except Exception as e:
            print(f"Error resolving conflicts: {str(e)}")
            return False

    def generate_commit_message(self, file_count=0):
        """커밋 메시지 생성"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 기본 메시지 생성
        message = COMMIT_MESSAGE_TEMPLATE.format(timestamp=timestamp)
        
        # 접두사 추가
        if CUSTOM_COMMIT_PREFIX:
            message = f"{CUSTOM_COMMIT_PREFIX} {message}"
        
        # 파일 개수 추가
        if INCLUDE_FILE_COUNT and file_count > 0:
            message += f" ({file_count}개 파일 변경)"
        
        return message

    def generate_merge_message(self):
        """병합 메시지 생성"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = MERGE_MESSAGE_TEMPLATE.format(timestamp=timestamp)
        
        if CUSTOM_COMMIT_PREFIX:
            message = f"{CUSTOM_COMMIT_PREFIX} {message}"
        
        return message

    def complete_merge_or_rebase(self):
        """병합 또는 리베이스 완료"""
        try:
            if self.is_merge_in_progress():
                # 3-way merge 완료
                print("3-way merge 완료 중...")
                commit_message = f"Merge completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                self.repo.git.commit("-m", commit_message)
                print("병합이 완료되었습니다!")
                return True
                
            elif self.is_rebase_in_progress():
                # 리베이스 계속
                print("리베이스 계속 진행 중...")
                self.repo.git.rebase("--continue")
                print("리베이스가 계속 진행되었습니다!")
                return True
                
            return True
            
        except Exception as e:
            print(f"Error completing merge/rebase: {str(e)}")
            print(f"병합/리베이스 완료 중 오류: {str(e)}")
            return False

    def sync_with_remote(self):
        """원격 저장소와 동기화"""
        try:
            print(f"\n원격 저장소 동기화 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 현재 브랜치 확인
            if not self.ensure_branch():
                return False

            # 진행 중인 병합/리베이스 확인 및 처리
            if self.is_merge_in_progress():
                print("⚠️ 진행 중인 병합을 감지했습니다. 자동으로 해결합니다...")
                conflicted_files = self.get_conflicted_files()
                
                if conflicted_files:
                    print(f"충돌 파일 감지: {', '.join(conflicted_files)}")
                    if AUTO_RESOLVE_CONFLICTS:
                        if self.resolve_conflicts_interactive(conflicted_files):
                            self.complete_merge_or_rebase()
                        else:
                            print("충돌 해결 실패. 병합을 중단합니다.")
                            self.repo.git.merge("--abort")
                    else:
                        print("병합을 중단합니다.")
                        self.repo.git.merge("--abort")
                else:
                    # 충돌이 없는 경우 병합 완료
                    self.complete_merge_or_rebase()
                    
            elif self.is_rebase_in_progress():
                print("⚠️ 진행 중인 리베이스를 감지했습니다. 중단합니다...")
                self.repo.git.rebase("--abort")

            # VS Code 호환 모드 확인
            if VSCODE_COMPATIBLE:
                print("VS Code 호환 모드: 기존 커밋만 동기화합니다.")
                
                # staged 변경사항이 있는지 확인
                if self.repo.index.diff("HEAD"):
                    print("⚠️ staged 변경사항이 있습니다. VS Code에서 먼저 커밋해주세요.")
                    return False
                    
                # unstaged 변경사항이 있는지 확인  
                if self.repo.is_dirty():
                    print("📝 unstaged 변경사항이 있습니다. VS Code에서 작업 후 커밋해주세요.")
                    print("현재는 기존 커밋만 동기화합니다.")
                    
            elif AUTO_COMMIT:
                # 자동 커밋 모드
                self.repo.git.add(".")
                
                if self.repo.is_dirty() or len(self.repo.untracked_files) > 0:
                    # 변경된 파일 개수 계산
                    file_count = len(self.repo.untracked_files) + len([item.a_path for item in self.repo.index.diff(None)])
                    commit_message = self.generate_commit_message(file_count)
                    self.repo.index.commit(commit_message)
                    print(f"로컬 변경사항 커밋: {commit_message}")
                    
            else:
                # 수동 커밋 모드
                if self.repo.is_dirty() or len(self.repo.untracked_files) > 0:
                    print("📝 커밋되지 않은 변경사항이 있습니다.")
                    print("VS Code나 git 명령어로 먼저 커밋해주세요.")
                    print("현재는 기존 커밋만 동기화합니다.")

            # 원격 저장소에서 변경사항 가져오기
            print("원격 저장소에서 변경사항을 가져오는 중...")
            try:
                origin = self.repo.remote("origin")
                origin.fetch()
                
                # 원격 브랜치 존재 확인
                remote_branch = f"origin/{self.branch}"
                if remote_branch in [str(ref) for ref in self.repo.refs]:
                    print(f"원격 브랜치 {remote_branch}와 병합 시도...")
                    
                    try:
                        # 먼저 일반 병합 시도
                        self.repo.git.merge(remote_branch, "--no-ff")
                        print("원격 변경사항이 성공적으로 병합되었습니다!")
                        
                    except Exception as merge_error:
                        error_msg = str(merge_error).lower()
                        
                        if "refusing to merge unrelated histories" in error_msg:
                            print("관련 없는 히스토리 오류 감지. --allow-unrelated-histories 옵션으로 병합을 시도합니다...")
                            try:
                                self.repo.git.merge(remote_branch, "--no-ff", "--allow-unrelated-histories")
                                print("관련 없는 히스토리가 성공적으로 병합되었습니다!")
                            except Exception as force_merge_error:
                                if "conflict" in str(force_merge_error).lower():
                                    print("히스토리 병합 시 충돌이 발생했습니다!")
                                    
                                    # 충돌 파일 확인
                                    conflicted_files = self.get_conflicted_files()
                                    
                                    if conflicted_files and AUTO_RESOLVE_CONFLICTS:
                                        print("자동 충돌 해결을 시작합니다...")
                                        
                                        if self.resolve_conflicts_interactive(conflicted_files):
                                            # 충돌 해결 후 병합/리베이스 완료
                                            if self.complete_merge_or_rebase():
                                                print("충돌 해결 및 병합이 완료되었습니다!")
                                            else:
                                                print("병합 완료 중 오류가 발생했습니다.")
                                                return False
                                        else:
                                            print("충돌 해결에 실패했습니다.")
                                            return False
                                    else:
                                        print("수동으로 충돌을 해결해야 합니다.")
                                        return False
                                else:
                                    raise force_merge_error
                                    
                        elif "conflict" in error_msg:
                            print("일반 병합에서 충돌이 발생했습니다!")
                            
                            # 충돌 파일 확인
                            conflicted_files = self.get_conflicted_files()
                            
                            if conflicted_files and AUTO_RESOLVE_CONFLICTS:
                                print("자동 충돌 해결을 시작합니다...")
                                
                                if self.resolve_conflicts_interactive(conflicted_files):
                                    # 충돌 해결 후 병합/리베이스 완료
                                    if self.complete_merge_or_rebase():
                                        print("충돌 해결 및 병합이 완료되었습니다!")
                                    else:
                                        print("병합 완료 중 오류가 발생했습니다.")
                                        return False
                                else:
                                    print("충돌 해결에 실패했습니다.")
                                    return False
                            else:
                                print("수동으로 충돌을 해결해야 합니다.")
                                return False
                        else:
                            raise merge_error
                else:
                    print(f"원격 브랜치 {self.branch}가 존재하지 않습니다. 새 브랜치로 푸시합니다.")

                # 원격으로 푸시
                print("원격 저장소로 푸시 중...")
                push_info = origin.push(self.branch)
                
                for info in push_info:
                    print(f"푸시 결과: {info.summary}")
                
                print("동기화가 완료되었습니다!")
                return True
                
            except Exception as e:
                print(f"Remote sync failed: {str(e)}")
                print(f"원격 동기화 실패: {str(e)}")
                return False

        except Exception as e:
            print(f"Error during sync: {str(e)}")
            print(f"동기화 중 오류: {str(e)}")
            return False

    def sync(self):
        """스케줄된 동기화 실행"""
        try:
            print(f"🔄 자동 동기화: {datetime.now().strftime('%H:%M:%S')}")
            
            success = self.sync_with_remote()
            
            if success:
                print("✅ 동기화 완료")
            else:
                print("❌ 동기화 실패")
            
        except Exception as e:
            print(f"❌ 동기화 오류: {str(e)}")


class GitAdvancedAutoSyncService(win32serviceutil.ServiceFramework):
    _svc_name_ = "GitAdvancedAutoSyncService"
    _svc_display_name_ = "Git Advanced Auto Sync Service"
    _svc_description_ = "고급 Git 자동 동기화 서비스 (충돌 해결 포함)"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.stop_requested = False

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.stop_requested = True

    def SvcDoRun(self):
        self.main()

    def main(self):
        try:
            git_sync = GitAdvancedAutoSync(REPO_PATH, REMOTE_URL, BRANCH)

            if git_sync.sync_with_remote():
                print("초기 동기화 완료")
            else:
                print("초기 동기화 실패")

            schedule.every(SYNC_INTERVAL).minutes.do(git_sync.sync)

            while not self.stop_requested:
                schedule.run_pending()
                time.sleep(1)
                if win32event.WaitForSingleObject(self.hWaitStop, 1000) == win32event.WAIT_OBJECT_0:
                    break

        except Exception as e:
            print(f"서비스 오류: {str(e)}")

def restart_as_background():
    """백그라운드로 재시작"""
    script_path = os.path.abspath(sys.argv[0])
    
    args = [arg for arg in sys.argv[1:] if arg != "--from-bat"]
    if "--background" not in args:
        args.append("--background")
    
    subprocess.Popen([sys.executable, script_path] + args)
    
    print("\n프로그램이 백그라운드에서 실행됩니다. 이 창은 3초 후 자동으로 닫힙니다.")
    time.sleep(3)
    sys.exit(0)

def run_foreground():
    """포그라운드에서 실행"""
    if from_bat and "--background" not in sys.argv:
        restart_as_background()
        return
    
    try:
        print("✅ Git 자동 동기화 v3.1 시작")
        
        git_sync = GitAdvancedAutoSync(REPO_PATH, REMOTE_URL, BRANCH)
        
        print(f"📁 {REPO_PATH} | 🌐 {BRANCH} | ⏰ {SYNC_INTERVAL}분")
        
        # 초기 동기화 실행
        if git_sync.sync_with_remote():
            print("✅ 초기 동기화 완료")
        else:
            print("❌ 초기 동기화 실패")
        
        # 스케줄러 설정
        schedule.every(SYNC_INTERVAL).minutes.do(git_sync.sync)
        
        next_run = schedule.next_run()
        if next_run:
            print(f"📅 다음: {next_run.strftime('%H:%M')}")
        
        print("🛑 종료: Ctrl+C")
        
        try:
            print("\n🔄 프로그램 실행 중...")
            
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1초 대신 60초로 최적화
                
        except KeyboardInterrupt:
            print("\n\n🛑 프로그램을 종료합니다...")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n💥 치명적 오류 발생: {str(e)}")
        print(traceback.format_exc())
        print("10초 후 프로그램이 종료됩니다...")
        time.sleep(10)
        sys.exit(1)

if __name__ == "__main__":
    if "--service" in sys.argv:
        win32serviceutil.HandleCommandLine(GitAdvancedAutoSyncService)
    else:
        run_foreground()