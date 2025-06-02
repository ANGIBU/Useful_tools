"""
Git 고급 자동 동기화 시스템 v2.0

✨ 새로운 기능:
    ✔️ 자동 폴더 생성 및 초기화
    ✔️ 원격 저장소 자동 클론
    ✔️ 충돌 자동 감지 및 Bash 에디터 연동
    ✔️ 3-way merge 자동 커밋
    ✔️ Rebase 자동 continue
    ✔️ 지능형 충돌 해결 시스템
    ✔️ Pull 및 Push 통합 관리

📌 설정 위치:
    ▶ 278줄, 334줄 - 저장소 설정
    ▶ 필요한 패키지: pip install gitpython schedule pywin32
"""

import os
import time
import traceback
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from git import Repo, GitCommandError
import schedule
import sys
import logging
import servicemanager
import socket
import win32event
import win32service
import win32serviceutil
import shutil
import re

# bat 파일에서 실행했는지 확인하기 위한 플래그
from_bat = "--from-bat" in sys.argv

class GitAdvancedAutoSync:
    def __init__(self, repo_path, remote_url, branch="main", auto_resolve_conflicts=True):
        self.repo_path = Path(repo_path)
        self.remote_url = remote_url
        self.branch = branch
        self.auto_resolve_conflicts = auto_resolve_conflicts
        self.temp_merge_file = None
        self.setup_logging()
        
        # 저장소 초기화 또는 로드
        self.initialize_repository()

    def setup_logging(self):
        """로깅 시스템 설정"""
        self.logger = logging.getLogger("GitAdvancedAutoSync")
        self.logger.setLevel(logging.INFO)

        # 로그 디렉토리 생성
        log_dir = self.repo_path.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_path = log_dir / f"git_advanced_sync_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        console_handler = logging.StreamHandler()

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def initialize_repository(self):
        """저장소 초기화 또는 기존 저장소 로드"""
        try:
            # 디렉토리가 존재하지 않으면 생성
            if not self.repo_path.exists():
                self.logger.info(f"Creating directory: {self.repo_path}")
                self.repo_path.mkdir(parents=True, exist_ok=True)
                print(f"📁 디렉토리 생성: {self.repo_path}")

            # Git 저장소가 존재하는지 확인
            if (self.repo_path / ".git").exists():
                self.repo = Repo(self.repo_path)
                self.logger.info("Existing repository loaded successfully")
                print("✅ 기존 저장소를 로드했습니다.")
            else:
                # 원격 저장소에서 클론 시도
                if self.clone_repository():
                    self.repo = Repo(self.repo_path)
                    print("✅ 원격 저장소에서 클론 완료")
                else:
                    # 클론 실패 시 새 저장소 초기화
                    self.repo = Repo.init(self.repo_path)
                    self.setup_remote()
                    print("✅ 새 저장소 초기화 완료")

            self.setup_branch()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize repository: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def clone_repository(self):
        """원격 저장소에서 클론"""
        try:
            self.logger.info(f"Attempting to clone from {self.remote_url}")
            print(f"🔄 원격 저장소에서 클론 중: {self.remote_url}")
            
            # 임시로 빈 폴더를 삭제하고 클론
            if self.repo_path.exists() and not any(self.repo_path.iterdir()):
                self.repo_path.rmdir()
            
            Repo.clone_from(self.remote_url, self.repo_path, branch=self.branch)
            return True
            
        except GitCommandError as e:
            self.logger.warning(f"Clone failed: {str(e)}")
            print(f"⚠️ 클론 실패 (새 저장소로 초기화): {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during clone: {str(e)}")
            print(f"❌ 예상치 못한 클론 오류: {str(e)}")
            return False

    def setup_remote(self):
        """원격 저장소 설정"""
        try:
            # 기존 origin 제거 후 새로 설정
            try:
                origin = self.repo.remote("origin")
                self.repo.delete_remote(origin)
            except ValueError:
                pass
            
            self.repo.create_remote("origin", self.remote_url)
            self.logger.info("Remote 'origin' configured")
            
        except Exception as e:
            self.logger.error(f"Failed to setup remote: {str(e)}")
            raise

    def setup_branch(self):
        """브랜치 설정"""
        try:
            # 로컬 브랜치 목록 확인
            local_branches = [b.name for b in self.repo.branches]
            
            # 원격 브랜치 확인 시도
            try:
                self.repo.git.fetch("origin")
                remote_branches = [ref.name.split('/')[-1] for ref in self.repo.remote().refs]
            except:
                remote_branches = []
                
            current_branch = None
            try:
                current_branch = self.repo.active_branch.name
            except:
                pass

            # 브랜치 생성 또는 체크아웃
            if self.branch not in local_branches:
                if self.branch in remote_branches:
                    # 원격 브랜치 추적
                    self.repo.git.checkout("-b", self.branch, f"origin/{self.branch}")
                    self.logger.info(f"Created local branch '{self.branch}' tracking origin/{self.branch}")
                else:
                    # 새 브랜치 생성
                    self.repo.git.checkout("-b", self.branch)
                    self.logger.info(f"Created new branch '{self.branch}'")
            elif current_branch != self.branch:
                self.repo.git.checkout(self.branch)
                self.logger.info(f"Switched to branch '{self.branch}'")
                
        except Exception as e:
            self.logger.error(f"Failed to setup branch: {str(e)}")
            # 브랜치 설정 실패해도 계속 진행
            pass

    def detect_merge_conflict(self):
        """병합 충돌 감지"""
        try:
            # Git 상태 확인
            status = self.repo.git.status("--porcelain")
            conflicts = [line for line in status.split('\n') if line.startswith('UU ') or line.startswith('AA ')]
            
            if conflicts:
                self.logger.warning(f"Merge conflicts detected: {len(conflicts)} files")
                return [conflict.split(' ', 1)[1] for conflict in conflicts]
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error detecting conflicts: {str(e)}")
            return []

    def resolve_conflicts_with_editor(self, conflicted_files):
        """충돌 파일을 에디터로 해결"""
        try:
            print("🔧 충돌이 감지되었습니다. 자동으로 에디터를 엽니다...")
            self.logger.info(f"Opening editor for conflict resolution: {conflicted_files}")
            
            for file_path in conflicted_files:
                full_path = self.repo_path / file_path
                print(f"📝 충돌 해결 중: {file_path}")
                
                # Git Bash에서 vim 에디터로 열기
                try:
                    # Windows에서 Git Bash 실행
                    git_bash_cmd = f'start "Git Conflict Resolution" "C:\\Program Files\\Git\\bin\\bash.exe" -c "cd \\"{self.repo_path}\\" && vim \\"{file_path}\\"; read -p \\"Press Enter to continue...\\" && exit"'
                    
                    # PowerShell을 통해 실행
                    subprocess.run(['powershell', '-Command', git_bash_cmd], check=True)
                    
                    # 사용자가 편집을 완료할 때까지 대기
                    input(f"'{file_path}' 편집을 완료한 후 Enter를 누르세요...")
                    
                except subprocess.CalledProcessError:
                    # Git Bash가 없는 경우 기본 텍스트 에디터 사용
                    print(f"⚠️ Git Bash를 찾을 수 없습니다. 시스템 에디터를 사용합니다.")
                    os.system(f'notepad "{full_path}"')
                    input(f"'{file_path}' 편집을 완료한 후 Enter를 누르세요...")
                
                # 파일이 해결되었는지 확인
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if '<<<<<<<' in content or '=======' in content or '>>>>>>>' in content:
                        print(f"⚠️ {file_path}에 아직 충돌 마커가 있습니다.")
                        continue_edit = input("다시 편집하시겠습니까? (y/N): ")
                        if continue_edit.lower() == 'y':
                            continue
                
                # 해결된 파일을 스테이징
                self.repo.git.add(file_path)
                print(f"✅ {file_path} 충돌 해결 완료")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error resolving conflicts: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False

    def handle_merge_state(self):
        """병합 상태 처리"""
        try:
            git_dir = self.repo_path / ".git"
            
            # Rebase 상태 확인
            if (git_dir / "rebase-merge").exists() or (git_dir / "rebase-apply").exists():
                self.logger.info("In rebase state")
                print("🔄 Rebase 상태입니다.")
                
                conflicts = self.detect_merge_conflict()
                if conflicts:
                    if self.auto_resolve_conflicts:
                        if self.resolve_conflicts_with_editor(conflicts):
                            # Rebase continue
                            self.repo.git.rebase("--continue")
                            print("✅ Rebase 계속 진행")
                            return True
                    else:
                        print("❌ 충돌 해결이 필요합니다.")
                        return False
                else:
                    # 충돌이 없으면 rebase continue
                    self.repo.git.rebase("--continue")
                    return True
            
            # Merge 상태 확인
            elif (git_dir / "MERGE_HEAD").exists():
                self.logger.info("In merge state")
                print("🔄 Merge 상태입니다.")
                
                conflicts = self.detect_merge_conflict()
                if conflicts:
                    if self.auto_resolve_conflicts:
                        if self.resolve_conflicts_with_editor(conflicts):
                            # 3-way merge 완료 후 커밋
                            commit_message = f"Merge conflict resolved at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            self.repo.git.commit("-m", commit_message)
                            print("✅ Merge 커밋 완료")
                            return True
                    else:
                        print("❌ 충돌 해결이 필요합니다.")
                        return False
                else:
                    # 충돌이 없으면 merge commit 생성
                    commit_message = f"Automated merge at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    self.repo.git.commit("-m", commit_message)
                    print("✅ 자동 Merge 완료")
                    return True
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error handling merge state: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False

    def smart_pull(self):
        """지능형 Pull 작업"""
        try:
            self.logger.info("Starting smart pull operation")
            print("🔄 원격 저장소에서 변경사항을 가져오는 중...")
            
            # Fetch 먼저 실행
            self.repo.git.fetch("origin")
            
            # 원격 브랜치와 비교
            try:
                local_commit = self.repo.head.commit
                remote_commit = self.repo.commit(f"origin/{self.branch}")
                
                if local_commit == remote_commit:
                    print("✅ 이미 최신 상태입니다.")
                    return True
                    
            except:
                # 원격 브랜치가 없는 경우
                print("📤 새 브랜치를 원격에 푸시합니다.")
                return True
            
            # Pull 시도 (rebase 방식)
            try:
                self.repo.git.pull("origin", self.branch, "--rebase")
                print("✅ Rebase pull 완료")
                return True
                
            except GitCommandError as e:
                self.logger.warning(f"Rebase pull failed: {str(e)}")
                
                # 충돌이 발생한 경우 처리
                if "CONFLICT" in str(e) or self.detect_merge_conflict():
                    print("⚠️ Pull 중 충돌 발생")
                    return self.handle_merge_state()
                
                # Rebase 실패 시 일반 merge 시도
                try:
                    self.repo.git.rebase("--abort")  # rebase 중단
                    self.repo.git.pull("origin", self.branch)
                    print("✅ Merge pull 완료")
                    return True
                    
                except GitCommandError as merge_error:
                    self.logger.error(f"Merge pull also failed: {str(merge_error)}")
                    
                    # Merge 충돌 처리
                    if "CONFLICT" in str(merge_error) or self.detect_merge_conflict():
                        print("⚠️ Merge 중 충돌 발생")
                        return self.handle_merge_state()
                    
                    return False
            
        except Exception as e:
            self.logger.error(f"Error during smart pull: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False

    def smart_push(self):
        """지능형 Push 작업"""
        try:
            self.logger.info("Starting smart push operation")
            
            # 변경사항 커밋
            self.repo.git.add(".")
            
            if self.repo.is_dirty() or len(self.repo.untracked_files) > 0:
                commit_message = f"Automated Commit Update at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                self.repo.index.commit(commit_message)
                self.logger.info(f"Created commit: {commit_message}")
                print(f"📝 새 커밋 생성: {commit_message}")
            
            # Push 시도
            try:
                origin = self.repo.remote("origin")
                push_info = origin.push(self.branch)
                
                for info in push_info:
                    self.logger.info(f"Push result: {info.summary}")
                    print(f"📤 Push 결과: {info.summary}")
                
                return True
                
            except GitCommandError as e:
                self.logger.warning(f"Push failed: {str(e)}")
                
                # Push 실패 시 pull 후 재시도
                if "rejected" in str(e).lower():
                    print("⚠️ Push 거부됨. 원격 변경사항을 먼저 가져옵니다.")
                    
                    if self.smart_pull():
                        # Pull 성공 후 다시 Push 시도
                        try:
                            push_info = origin.push(self.branch)
                            for info in push_info:
                                print(f"📤 재시도 Push 결과: {info.summary}")
                            return True
                        except GitCommandError as retry_error:
                            self.logger.error(f"Retry push failed: {str(retry_error)}")
                            return False
                    else:
                        return False
                else:
                    return False
            
        except Exception as e:
            self.logger.error(f"Error during smart push: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False

    def sync(self):
        """통합 동기화 작업"""
        try:
            print(f"\n{'='*60}")
            print(f"🔄 동기화 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}")
            
            # 1. 원격 변경사항 가져오기
            if not self.smart_pull():
                print("❌ Pull 작업 실패")
                return False
            
            # 2. 로컬 변경사항 푸시
            if not self.smart_push():
                print("❌ Push 작업 실패")
                return False
            
            # 다음 실행 시간 표시
            next_run = schedule.next_run()
            if next_run:
                print(f"⏰ 다음 동기화: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("✅ 동기화 완료!")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during sync: {str(e)}")
            self.logger.error(traceback.format_exc())
            print(f"❌ 동기화 중 오류: {str(e)}")
            return False

    def force_push_initial(self):
        """초기 강제 푸시 (기존 기능 유지)"""
        try:
            self.repo.git.add(".")
            
            commit_message = f"Initial Automated Commit at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self.repo.git.commit("-m", commit_message, "--allow-empty")
            
            origin = self.repo.remote("origin")
            push_info = origin.push(self.branch, force=True)
            
            for info in push_info:
                self.logger.info(f"Force push result: {info.summary}")
                print(f"📤 강제 Push 결과: {info.summary}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error during force push: {str(e)}")
            return False


class GitAdvancedSyncService(win32serviceutil.ServiceFramework):
    _svc_name_ = "GitAdvancedSyncService" 
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
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, "")
        )
        self.main()

    def main(self):
        # ========== 서비스 설정 (여기를 수정하세요) ==========
        repo_path = r"C:\Users\YourName\Documents\MyRepo"  # 저장소 경로
        remote_url = "https://github.com/username/repository.git"  # GitHub URL
        branch = "main"  # 브랜치명
        # ================================================
        
        try:
            git_sync = GitAdvancedAutoSync(repo_path, remote_url, branch)
            
            servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, 0, ("초기 동기화 시작", ""))
            
            if git_sync.sync():
                servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, 0, ("초기 동기화 완료", ""))
            else:
                servicemanager.LogMsg(servicemanager.EVENTLOG_WARNING_TYPE, 0, ("초기 동기화 실패", ""))
            
            # 10분마다 동기화
            schedule.every(10).minutes.do(git_sync.sync)
            
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                0,
                (f"Git 고급 자동 동기화 시작. 10분마다 {branch} 브랜치 동기화", "")
            )
            
            while not self.stop_requested:
                schedule.run_pending()
                time.sleep(1)
                if win32event.WaitForSingleObject(self.hWaitStop, 1000) == win32event.WAIT_OBJECT_0:
                    break
                    
        except Exception as e:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_ERROR_TYPE,
                0,
                (f"서비스 오류: {str(e)}", "")
            )


def restart_as_background():
    """백그라운드 실행을 위한 프로세스 재시작"""
    script_path = os.path.abspath(sys.argv[0])
    
    args = [arg for arg in sys.argv[1:] if arg != "--from-bat"]
    if "--background" not in args:
        args.append("--background")
    
    subprocess.Popen([sys.executable, script_path] + args)
    
    print("\n🚀 프로그램이 백그라운드에서 실행됩니다. 이 창은 3초 후 자동으로 닫힙니다.")
    time.sleep(3)
    sys.exit(0)


def run_foreground():
    # ========== 포그라운드 실행 설정 (여기를 수정하세요) ==========
    repo_path = r"C:\Users\YourName\Documents\MyRepo"  # 저장소 경로
    remote_url = "https://github.com/username/repository.git"  # GitHub URL  
    branch = "main"  # 브랜치명
    # =========================================================
    
    # bat 파일에서 실행한 경우 백그라운드로 재시작
    if from_bat and "--background" not in sys.argv:
        restart_as_background()
        return
    
    try:
        print("🚀 Git 고급 자동 동기화 시스템 v2.0")
        print("=" * 60)
        print("✨ 새로운 기능:")
        print("   • 자동 폴더 생성 및 초기화")
        print("   • 원격 저장소 자동 클론")
        print("   • 충돌 자동 감지 및 해결")
        print("   • 3-way merge & Rebase 지원")
        print("   • 지능형 Pull/Push 시스템")
        print("=" * 60)
        
        git_sync = GitAdvancedAutoSync(repo_path, remote_url, branch)
        
        print(f"\n📍 저장소 정보:")
        print(f"   경로: {repo_path}")
        print(f"   URL: {remote_url}")
        print(f"   브랜치: {branch}")
        
        # 초기 동기화 실행
        print(f"\n🔄 초기 동기화 실행 중...")
        if git_sync.sync():
            print("✅ 초기 동기화 완료!")
        else:
            print("⚠️ 초기 동기화에 문제가 있었습니다. 로그를 확인하세요.")
        
        # 스케줄러 설정
        print(f"\n⚙️ 자동 동기화 스케줄러 설정 (10분 간격)")
        print("💡 충돌 발생 시 자동으로 에디터가 열립니다.")
        print("💡 이 창을 닫으면 자동 동기화가 중단됩니다.")
        print("\n🛑 종료하려면 Ctrl+C를 누르세요.\n")
        
        schedule.every(10).minutes.do(git_sync.sync)
        
        # 다음 실행 시간 표시
        next_run = schedule.next_run()
        if next_run:
            print(f"⏰ 다음 동기화: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 무한 루프 실행
        try:
            count = 0
            print(f"\n{'='*60}")
            print("🔄 자동 동기화 시스템이 실행 중입니다...")
            print(f"{'='*60}")
            
            while True:
                schedule.run_pending()
                
                # 1분마다 상태 출력
                if count % 60 == 0 and count > 0:
                    now = datetime.now()
                    next_run = schedule.next_run()
                    
                    if next_run:
                        time_left = int((next_run - now).total_seconds())
                        minutes = time_left // 60
                        seconds = time_left % 60
                        print(f"⏰ {now.strftime('%H:%M:%S')} - 다음 동기화까지 {minutes}분 {seconds}초")
                
                time.sleep(1)
                count += 1
                
        except KeyboardInterrupt:
            print("\n\n🛑 사용자에 의해 프로그램이 종료됩니다...")
            print("✅ Git 고급 자동 동기화 시스템을 안전하게 종료했습니다.")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n❌ 치명적 오류 발생: {str(e)}")
        print(traceback.format_exc())
        print("⏳ 10초 후 프로그램이 종료됩니다...")
        time.sleep(10)
        sys.exit(1)


if __name__ == "__main__":
    if "--service" in sys.argv:
        win32serviceutil.HandleCommandLine(GitAdvancedSyncService)
    else:
        run_foreground()