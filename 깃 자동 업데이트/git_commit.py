"""
Git 자동 동기화 서비스

✔️ 커밋 메시지는 아래와 같은 형식입니다:
    Automated Commit Update at (업데이트 된 시간)

📌 아래 위치에서 경로와 URL, 브랜치 양식을 알맞게 수정 후 사용하세요!:
    ▶ 200줄
"""
# ─────────────────────────────────────────────────────
# 사용 전 필수 확인 사항:
# 1. 해당 GitHub 저장소에 push 권한이 있는 계정이어야 합니다.
#    - 저장소 소유자로부터 Collaborator(협업자)로 초대받아야 합니다.
#    - 또는 본인 저장소에 연결하여 사용하세요.
# 2. 원격 저장소 URL(remote_url)을 본인에게 맞게 수정하세요.
# 3. 인증은 HTTPS(PAT 필요) 또는 SSH 방식이 가능합니다.
# 4. 이 코드는 원격 변경 사항을 무시하고 로컬 변경만 푸시합니다 (force push).
# ─────────────────────────────────────────────────────
# 라이브러리 설치 : pip install gitpython schedule pywin32 <-- 복사해서 cmd에 붙여넣으세요
# ─────────────────────────────────────────────────────

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
        try:
            current_branch = self.repo.active_branch.name
            self.logger.info(f"Current branch: {current_branch}")
            local_branches = [b.name for b in self.repo.branches]

            if self.branch not in local_branches:
                self.logger.info(f"Creating new local branch '{self.branch}'")
                self.repo.git.checkout("-b", self.branch)
            elif current_branch != self.branch:
                self.repo.git.checkout(self.branch)
                self.logger.info(f"Checked out branch '{self.branch}'")

            return True
        except Exception as e:
            self.logger.error(f"Error ensuring branch: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False

    def force_push(self):
        try:
            if not self.ensure_branch():
                self.logger.error("Failed to ensure correct branch, skipping push")
                return False

            self.repo.git.add(".")

            commit_message = f"Automated Commit Update at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self.repo.git.commit("-m", commit_message, "--allow-empty")
            self.logger.info(f"Created commit: {commit_message}")

            try:
                self.logger.info(f"Force pushing to origin/{self.branch}...")
                origin = self.repo.remote("origin")
                push_info = origin.push(self.branch, force=True)
                for info in push_info:
                    self.logger.info(f"Push result: {info.summary}")
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
        try:
            print(f"스케줄된 동기화 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            if not self.ensure_branch():
                self.logger.error("Failed to ensure correct branch, skipping sync")
                return

            self.repo.git.add(".")

            if self.repo.is_dirty() or len(self.repo.untracked_files) > 0:
                commit_message = f"Automated Commit Update at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                self.repo.index.commit(commit_message)
                self.logger.info(f"Created scheduled commit: {commit_message}")
                print(f"새 커밋 생성: {commit_message}")

                try:
                    self.logger.info(f"Pushing to origin/{self.branch}...")
                    origin = self.repo.remote("origin")
                    push_info = origin.push(self.branch, force=True)
                    for info in push_info:
                        self.logger.info(f"Push result: {info.summary}")
                        print(f"푸시 결과: {info.summary}")
                except Exception as e:
                    self.logger.error(f"Push failed: {str(e)}")
                    self.logger.error(traceback.format_exc())
                    print(f"푸시 실패: {str(e)}")
            else:
                self.logger.info("No changes to sync")
                print("동기화할 변경 사항이 없습니다.")

            # 다음 실행 시간 표시
            next_run = schedule.next_run()
            if next_run:
                print(f"다음 동기화 예정 시간: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print("다음 동기화 일정이 없습니다.")

        except Exception as e:
            self.logger.error(f"Error during sync: {str(e)}")
            self.logger.error(traceback.format_exc())
            print(f"동기화 중 오류 발생: {str(e)}")


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
#######################################################################

    def main(self):
        repo_path = r"파일 경로"
        remote_url = "깃허브 주소"
        branch = "깃허브 브랜치"
        
#######################################################################
        try:
            git_sync = GitAutoSync(repo_path, remote_url, branch)

            servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, 0, ("초기 푸시 시작", ""))

            if git_sync.force_push():
                servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, 0, ("초기 푸시 완료", ""))
            else:
                servicemanager.LogMsg(servicemanager.EVENTLOG_WARNING_TYPE, 0, ("초기 푸시 실패", ""))

            schedule.every(10).minutes.do(git_sync.sync)

            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                0,
                (f"Git 자동 동기화가 시작되었습니다. 10분마다 {branch} 브랜치를 동기화합니다.", "")
            )

            while not self.stop_requested:
                schedule.run_pending()
                time.sleep(1)  # 1초마다 스케줄러 확인
                if win32event.WaitForSingleObject(self.hWaitStop, 1000) == win32event.WAIT_OBJECT_0:
                    break

        except Exception as e:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_ERROR_TYPE,
                0,
                (f"서비스 오류: {str(e)}", "")
            )

def run_foreground():
    # 실제 작업을 수행하는 단일 함수
    repo_path = r"C:\Users\facec\Desktop\LIVON"
    remote_url = "https://github.com/Jinyechan/LIVON-PROJECT"
    branch = "gibu"
    
    try:
        git_sync = GitAutoSync(repo_path, remote_url, branch)
        
        print("=" * 50)
        print("깃 자동 동기화 시작")
        print("=" * 50)
        print(f"저장소 경로: {repo_path}")
        print(f"브랜치: {branch}")
        
        # 초기 푸시 실행
        print("\n프로그램 시작 시 즉시 푸시 중... (원격 변경사항을 무시하고 로컬 파일만 푸시합니다)")
        if git_sync.force_push():
            print("초기 푸시 완료!")
        else:
            print("초기 푸시 실패. 로그를 확인하세요.")
        
        # 스케줄러 설정
        print(f"\nGit 자동 동기화가 설정되었습니다. 10분마다 {branch} 브랜치를 동기화합니다.")
        print("※ 주의: 원격 변경사항을 가져오지 않고 로컬 파일만 푸시합니다.")
        print("※ 이 창을 닫으면 자동 동기화가 중단됩니다. 창을 계속 열어두세요.")
        print("\n커맨드창에 'Ctrl+C'를 누르면 프로그램이 종료됩니다.\n")
        
        # 스케줄러 등록
        schedule.every(10).minutes.do(git_sync.sync)
        
        # 첫 예약 실행 시간 계산
        next_run = schedule.next_run()
        if next_run:
            print(f"다음 동기화 예정 시간: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 무한 루프 실행
        try:
            count = 0
            print("\n프로그램이 실행 중입니다. 10분마다 자동 동기화를 수행합니다...")
            print("-" * 50)
            
            while True:
                schedule.run_pending()
                
                # 1분마다 한 번씩 로그 출력 (화면이 계속 움직이는 것처럼 보이게)
                if count % 60 == 0 and count > 0:
                    now = datetime.now()
                    next_run = schedule.next_run()
                    time_left = int((next_run - now).total_seconds()) if next_run else 0
                    
                    minutes = time_left // 60
                    seconds = time_left % 60
                    print(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - 다음 동기화까지 {minutes}분 {seconds}초 남았습니다.")
                
                time.sleep(1)
                count += 1
                
        except KeyboardInterrupt:
            print("\n프로그램을 종료합니다...")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n치명적 오류 발생: {str(e)}")
        print(traceback.format_exc())
        print("10초 후 프로그램이 종료됩니다...")
        time.sleep(10)
        sys.exit(1)

if __name__ == "__main__":
    if "--service" in sys.argv:
        win32serviceutil.HandleCommandLine(GitAutoSyncService)
    else:
        run_foreground()