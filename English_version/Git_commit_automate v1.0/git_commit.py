# Git_Automate_EN.py
"""
Git Automatic Sync Service

✔️ Commit messages follow this format:
    Automated Commit Update at (updated time)

📌 Please modify the path, URL, and branch format appropriately at the locations below before use!:
    ▶ Lines 205, 260
"""
# ─────────────────────────────────────────────────────
# Essential checks before use:
# 1. You must have push permissions to the GitHub repository.
#    - You need to be invited as a Collaborator by the repository owner.
#    - Or connect to your own repository.
# 2. Modify the remote repository URL (remote_url) to match your needs.
# 3. Authentication can be done via HTTPS (PAT required) or SSH.
# 4. This code ignores remote changes and only pushes local changes (force push).
# ─────────────────────────────────────────────────────
# Library installation: pip install gitpython schedule pywin32 <-- Copy and paste this into cmd
# Register Git_Automate.vbs in startup programs for automatic execution on boot.
# Create a shortcut for Git_Automate.vbs and register it in startup programs!
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
import subprocess

# Flag to check if executed from bat file
from_bat = "--from-bat" in sys.argv

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
            print(f"Scheduled sync started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            if not self.ensure_branch():
                self.logger.error("Failed to ensure correct branch, skipping sync")
                return

            self.repo.git.add(".")

            if self.repo.is_dirty() or len(self.repo.untracked_files) > 0:
                commit_message = f"Automated Commit Update at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                self.repo.index.commit(commit_message)
                self.logger.info(f"Created scheduled commit: {commit_message}")
                print(f"New commit created: {commit_message}")

                try:
                    self.logger.info(f"Pushing to origin/{self.branch}...")
                    origin = self.repo.remote("origin")
                    push_info = origin.push(self.branch, force=True)
                    for info in push_info:
                        self.logger.info(f"Push result: {info.summary}")
                        print(f"Push result: {info.summary}")
                except Exception as e:
                    self.logger.error(f"Push failed: {str(e)}")
                    self.logger.error(traceback.format_exc())
                    print(f"Push failed: {str(e)}")
            else:
                self.logger.info("No changes to sync")
                print("No changes to sync.")

            # Display next execution time
            next_run = schedule.next_run()
            if next_run:
                print(f"Next sync scheduled at: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print("No next sync scheduled.")

        except Exception as e:
            self.logger.error(f"Error during sync: {str(e)}")
            self.logger.error(traceback.format_exc())
            print(f"Error occurred during sync: {str(e)}")


class GitAutoSyncService(win32serviceutil.ServiceFramework):
    _svc_name_ = "GitAutoSyncService"
    _svc_display_name_ = "Git Auto Sync Service"
    _svc_description_ = "Service that automatically syncs Git repository"

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
        repo_path = r"File Path"
        remote_url = "GitHub Address.git"
        branch = "GitHub Branch"
        
#######################################################################
        try:
            git_sync = GitAutoSync(repo_path, remote_url, branch)

            servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, 0, ("Initial push started", ""))

            if git_sync.force_push():
                servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, 0, ("Initial push completed", ""))
            else:
                servicemanager.LogMsg(servicemanager.EVENTLOG_WARNING_TYPE, 0, ("Initial push failed", ""))

            schedule.every(10).minutes.do(git_sync.sync)

            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                0,
                (f"Git auto sync started. Syncing {branch} branch every 10 minutes.", "")
            )

            while not self.stop_requested:
                schedule.run_pending()
                time.sleep(1)  # Check scheduler every 1 second
                if win32event.WaitForSingleObject(self.hWaitStop, 1000) == win32event.WAIT_OBJECT_0:
                    break

        except Exception as e:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_ERROR_TYPE,
                0,
                (f"Service error: {str(e)}", "")
            )

def restart_as_background():
    """Restart itself as a new process and terminate current process after 3 seconds"""
    script_path = os.path.abspath(sys.argv[0])
    
    # Remove --from-bat flag and add --background flag
    args = [arg for arg in sys.argv[1:] if arg != "--from-bat"]
    if "--background" not in args:
        args.append("--background")
    
    # Start new process
    subprocess.Popen([sys.executable, script_path] + args)
    
    # Terminate current process after 3 seconds
    print("\nProgram will run in background. This window will close automatically in 3 seconds.")
    time.sleep(3)
    sys.exit(0)
#######################################################################

def run_foreground():
    repo_path = r"File Path"
    remote_url = "GitHub Address.git"
    branch = "GitHub Branch"
                
#######################################################################
    # If executed from bat file, restart in background
    if from_bat and "--background" not in sys.argv:
        restart_as_background()
        return
    
    try:
        git_sync = GitAutoSync(repo_path, remote_url, branch)
        
        print("=" * 50)
        print("Git Auto Sync Started")
        print("=" * 50)
        print(f"Repository path: {repo_path}")
        print(f"Branch: {branch}")
        
        # Execute initial push
        print("\nExecuting immediate push on program start... (Ignoring remote changes and pushing local files only)")
        if git_sync.force_push():
            print("Initial push completed!")
        else:
            print("Initial push failed. Please check the logs.")
        
        # Setup scheduler
        print(f"\nGit auto sync has been configured. Syncing {branch} branch every 10 minutes.")
        print("※ Warning: Does not fetch remote changes, only pushes local files.")
        print("※ Closing this window will stop auto sync. Keep this window open.")
        print("\nPress 'Ctrl+C' in the command window to exit the program.\n")
        
        # Register scheduler
        schedule.every(10).minutes.do(git_sync.sync)
        
        # Calculate first scheduled execution time
        next_run = schedule.next_run()
        if next_run:
            print(f"Next sync scheduled at: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run infinite loop
        try:
            count = 0
            print("\nProgram is running. Auto sync will be performed every 10 minutes...")
            print("-" * 50)
            
            while True:
                schedule.run_pending()
                
                # Log output every minute
                if count % 60 == 0 and count > 0:
                    now = datetime.now()
                    next_run = schedule.next_run()
                    time_left = int((next_run - now).total_seconds()) if next_run else 0
                    
                    minutes = time_left // 60
                    seconds = time_left % 60
                    print(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - {minutes} minutes {seconds} seconds until next sync.")
                
                time.sleep(1)
                count += 1
                
        except KeyboardInterrupt:
            print("\nTerminating program...")
            sys.exit(0)
            
    except Exception as e:
        print(f"\nFatal error occurred: {str(e)}")
        print(traceback.format_exc())
        print("Program will terminate in 10 seconds...")
        time.sleep(10)
        sys.exit(1)

if __name__ == "__main__":
    if "--service" in sys.argv:
        win32serviceutil.HandleCommandLine(GitAutoSyncService)
    else:
        run_foreground()