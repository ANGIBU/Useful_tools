# git_sync.py
# 깃허브에 자동으로 push하는 윈도우 서비스
# 설정값을 잘 확인하여 사용하세요
# run_git_sync.py = 경로를 수정하여 시작프로그램으로 설정 가능

import os
import time
import traceback
from datetime import datetime
from git import Repo
import schedule
import sys
import logging
from pathlib import Path
import servicemanager
import socket
import win32event
import win32service
import win32serviceutil


class GitAutoSync:
    def __init__(self, repo_path, remote_url, branch="gb"):
        self.repo_path = Path(repo_path)
        self.remote_url = remote_url
        self.branch = branch
        self.setup_logging()

        try:
            if (self.repo_path / ".git").exists():
                self.repo = Repo(self.repo_path)
                self.logger.info("Repository loaded successfully")
            else:
                self.repo = Repo.init(self.repo_path)
                self.logger.info("New repository initialized")

            try:
                origin = self.repo.remote("origin")
                current_url = next(origin.urls)
                if current_url != remote_url:
                    origin.set_url(remote_url)
                    self.logger.info("Remote URL updated")
            except ValueError:
                self.repo.create_remote("origin", remote_url)
                self.logger.info("Remote 'origin' created")

        except Exception as e:
            self.logger.error(f"Failed to initialize repository: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def setup_logging(self):
        self.logger = logging.getLogger("GitAutoSync")
        self.logger.setLevel(logging.INFO)

        log_path = self.repo_path.parent / "git_sync.log"
        file_handler = logging.FileHandler(log_path)
        console_handler = logging.StreamHandler()

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def ensure_branch(self):
        """현재 브랜치를 확인하고 필요시 대상 브랜치로 전환"""
        try:
            current_branch = self.repo.active_branch.name
            self.logger.info(f"Current branch: {current_branch}")
            
            local_branches = [b.name for b in self.repo.branches]
            self.logger.info(f"Local branches: {local_branches}")
            
            if self.branch not in local_branches:
                self.logger.info(f"Creating new local branch '{self.branch}'")
                self.repo.git.checkout("-b", self.branch)
                self.logger.info(f"Created and checked out branch '{self.branch}'")
            elif current_branch != self.branch:
                self.repo.git.checkout(self.branch)
                self.logger.info(f"Checked out branch '{self.branch}'")
                
            return True
        except Exception as e:
            self.logger.error(f"Error ensuring branch: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False

    def force_push(self):
        """로컬 파일만 강제로 커밋하고 푸시 (원격 변경사항 무시)"""
        try:
            if not self.ensure_branch():
                self.logger.error("Failed to ensure correct branch, skipping push")
                return False
            
            self.repo.git.add(".")
            
            commit_message = f"Initial sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self.repo.git.commit("-m", commit_message, "--allow-empty")
            self.logger.info(f"Created commit: {commit_message}")
            
            try:
                self.logger.info(f"Force pushing to origin/{self.branch}...")
                origin = self.repo.remote("origin")
                push_info = origin.push(self.branch, force=True)
                for info in push_info:
                    self.logger.info(f"Push result: {info.summary}")
                self.logger.info("Successfully pushed initial commit")
                return True
            except Exception as e:
                self.logger.error(f"Push failed: {str(e)}")
                self.logger.error(traceback.format_exc())
                return False
                
        except Exception as e:
            self.logger.error(f"Error during force push: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False

    def sync(self):
        """일반 동기화 - 로컬 변경사항만 커밋 및 푸시"""
        try:
            if not self.ensure_branch():
                self.logger.error("Failed to ensure correct branch, skipping sync")
                return

            self.repo.git.add(".")
            
            if self.repo.is_dirty() or len(self.repo.untracked_files) > 0:
                commit_message = (
                    f"Auto sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                self.repo.index.commit(commit_message)

                try:
                    self.logger.info(f"Pushing to origin/{self.branch}...")
                    origin = self.repo.remote("origin")
                    push_info = origin.push(self.branch, force=True)
                    for info in push_info:
                        self.logger.info(f"Push result: {info.summary}")
                    self.logger.info("Successfully pushed changes")
                except Exception as e:
                    self.logger.error(f"Push failed: {str(e)}")
                    self.logger.error(traceback.format_exc())
            else:
                self.logger.info("No changes to sync")

        except Exception as e:
            self.logger.error(f"Error during sync: {str(e)}")
            self.logger.error(traceback.format_exc())


class GitAutoSyncService(win32serviceutil.ServiceFramework):
    _svc_name_ = "GitAutoSyncService"
    _svc_display_name_ = "Git Auto Sync Service"
    _svc_description_ = "자동으로 Git 저장소를 동기화하는 서비스"

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
        # 설정 값
        repo_path = r"C:\Users\facec\Desktop\smart_city"  # 푸시할 파일 위치 (알맞게 수정)
        remote_url = "https://github.com/junhyuk000/smart_city.git"  # 푸시할 깃허브 주소 (알맞게 수정)
        branch = "gb"  # 사용할 브랜치 (알맞게 수정)
        
        try:
            git_sync = GitAutoSync(repo_path, remote_url, branch)
            
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                0,
                ("초기 푸시 시작", "")
            )
            
            if git_sync.force_push():
                servicemanager.LogMsg(
                    servicemanager.EVENTLOG_INFORMATION_TYPE,
                    0,
                    ("초기 푸시 완료", "")
                )
            else:
                servicemanager.LogMsg(
                    servicemanager.EVENTLOG_WARNING_TYPE,
                    0,
                    ("초기 푸시 실패", "")
                )
            
            # 10분마다 동기화 설정 (업데이트 주기의 수정을 원할 경우 수정)
            schedule.every(10).minutes.do(git_sync.sync)
            
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                0,
                (f"Git 자동 동기화가 시작되었습니다. 10분마다 {branch} 브랜치를 동기화합니다.", "")
            )
            
            while not self.stop_requested:
                schedule.run_pending()
                if win32event.WaitForSingleObject(self.hWaitStop, 1000) == win32event.WAIT_OBJECT_0:
                    break
            
        except Exception as e:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_ERROR_TYPE,
                0,
                (f"서비스 오류: {str(e)}", "")
            )


# 설정 값값
def run_as_script():
    """일반 스크립트로 실행할 때 호출되는 함수"""
    repo_path = r"C:\Users\facec\Desktop\smart_city"  # 푸시할 파일 위치 (알맞게 수정)
    remote_url = "https://github.com/junhyuk000/smart_city.git"  # 푸시할 깃허브 주소 (알맞게 수정)
    branch = "gb"  # 사용할 브랜치 (알맞게 수정)

    try:
        git_sync = GitAutoSync(repo_path, remote_url, branch)
        
        print("프로그램 시작 시 즉시 푸시 중... (원격 변경사항을 무시하고 로컬 파일만 푸시합니다)")
        if git_sync.force_push():
            print("초기 푸시 완료!")
        else:
            print("초기 푸시 실패. 로그를 확인하세요.")
        
        if len(sys.argv) > 1 and sys.argv[1] == "--background":
            print(f"Git 자동 동기화가 시작되었습니다. 10분마다 {branch} 브랜치를 동기화합니다.")
            print("※ 주의: 원격 변경사항을 가져오지 않고 로컬 파일만 푸시합니다.")
            print("프로그램을 종료하려면 Ctrl+C를 누르세요.")
            
            schedule.every(10).minutes.do(git_sync.sync)
            while True:
                schedule.run_pending()
                time.sleep(1)
        else:
            schedule.every(10).minutes.do(git_sync.sync)
            
            print(f"Git 자동 동기화가 설정되었습니다. 10분마다 {branch} 브랜치를 동기화합니다.")
            print("※ 주의: 원격 변경사항을 가져오지 않고 로컬 파일만 푸시합니다.")
            print("프로그램이 백그라운드에서 실행됩니다. 이 창은 3초 후 자동으로 닫힙니다.")
            time.sleep(3)
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다...")
        sys.exit(0)
    except Exception as e:
        print(f"치명적 오류 발생: {str(e)}")
        time.sleep(10)
        sys.exit(1)


if __name__ == "__main__":
    if "--service" in sys.argv:
        win32serviceutil.HandleCommandLine(GitAutoSyncService)
    else:
        run_as_script()