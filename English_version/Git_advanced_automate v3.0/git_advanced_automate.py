# git_advanced_automate.py

"""
Git Advanced Auto Sync Service v3.0

New Features:
✔️ Auto-install required modules (requirements.txt based)
✔️ Automatic merge/rebase handling
✔️ Auto-launch editor when conflicts occur
✔️ 3-way merge and rebase situation auto-detection and handling
✔️ Complete automation of initial repository setup (folder creation, clone, init)
✔️ Automatic pull and merge of remote changes
✔️ Auto commit/continue after conflict resolution
📌 Configuration Location: Lines 137-151 (CONFIG Section)
📌 Once you’ve set the path, create a shortcut for the VBS file and place it in the Startup folder so it runs automatically at system startup.
"""

import os
import sys
import subprocess
import time
import traceback
import tempfile
from datetime import datetime
from pathlib import Path

# Function to auto-install required modules
def check_and_install_requirements():
    """Check and automatically install required modules"""
    required_modules = {
        'git': 'gitpython>=3.1.40',
        'schedule': 'schedule>=1.2.0',
        'win32service': 'pywin32>=306',
        'win32serviceutil': 'pywin32>=306',
        'win32event': 'pywin32>=306',
        'servicemanager': 'pywin32>=306'
    }
    
    missing_modules = []
    
    print("🔍 Checking required modules...")
    
    # Check each module
    for module, package in required_modules.items():
        try:
            __import__(module)
            print(f"✅ {module} - Installed")
        except ImportError:
            print(f"❌ {module} - Missing")
            if package not in missing_modules:
                missing_modules.append(package)
    
    # Install missing modules
    if missing_modules:
        print(f"\n📦 Installing missing modules: {', '.join(missing_modules)}")
        
        for package in missing_modules:
            try:
                print(f"⬇️ Installing: {package}")
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package
                ], capture_output=True, text=True, check=True)
                
                print(f"✅ {package} installation completed")
                
            except subprocess.CalledProcessError as e:
                print(f"❌ {package} installation failed: {e}")
                print(f"Error output: {e.stderr}")
                
                # Try upgrading pip
                print("🔄 Upgrading pip and retrying...")
                try:
                    subprocess.run([
                        sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
                    ], check=True, capture_output=True)
                    
                    subprocess.run([
                        sys.executable, '-m', 'pip', 'install', package
                    ], check=True, capture_output=True)
                    
                    print(f"✅ {package} installation completed (retry)")
                    
                except subprocess.CalledProcessError as e2:
                    print(f"💥 {package} final installation failure: {e2}")
                    return False
        
        print("\n🔄 Module installation completed. Restarting program...")
        time.sleep(2)
        
        # Restart program
        subprocess.Popen([sys.executable] + sys.argv)
        sys.exit(0)
    
    else:
        print("✅ All required modules are installed.\n")
    
    return True

# Auto-generate requirements.txt
def create_requirements_file():
    """Auto-generate requirements.txt file"""
    script_dir = Path(__file__).parent
    requirements_path = script_dir / "requirements.txt"
    
    if not requirements_path.exists():
        print("📝 Creating requirements.txt file...")
        requirements_content = """gitpython>=3.1.40
schedule>=1.2.0
pywin32>=306"""
        
        with open(requirements_path, 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        
        print(f"✅ requirements.txt file created: {requirements_path}")

# Check and install modules at startup
print("🚀 Git Advanced Auto Sync System v3.0 Starting")
print("="*60)

create_requirements_file()
if not check_and_install_requirements():
    print("💥 Failed to install required modules. Terminating program.")
    input("Press Enter to exit...")
    sys.exit(1)

# Now that all modules are installed, import them
from git import Repo, InvalidGitRepositoryError
import schedule
import logging
import servicemanager
import socket
import win32event
import win32service
import win32serviceutil
import shutil

# ===============================================

# CONFIG Section - Only modify this section
REPO_PATH = r"file_path"  # Local repository path
REMOTE_URL = "github_url.git"  # GitHub repository URL (include .git extension)
BRANCH = "branch_name"  # Branch name
SYNC_INTERVAL = 10  # Sync interval (minutes)
AUTO_RESOLVE_CONFLICTS = True  # Auto-launch editor when conflicts occur

# Commit message settings
COMMIT_MESSAGE_TEMPLATE = "Committed at: {timestamp}"  # {timestamp} will be replaced with time
MERGE_MESSAGE_TEMPLATE = "Merged at: {timestamp}"  # Merge commit message
CUSTOM_COMMIT_PREFIX = "Auto-sync"  # Prefix for commit messages

# ===============================================

INCLUDE_FILE_COUNT = True
from_bat = "--from-bat" in sys.argv

class GitAdvancedAutoSync:
    def __init__(self, repo_path, remote_url, branch="main"):
        self.repo_path = Path(repo_path)
        self.remote_url = remote_url
        self.branch = branch
        self.repo = None
        self.setup_logging()
        
        # Initial setup and repository preparation
        self.setup_repository()

    def setup_logging(self):
        self.logger = logging.getLogger("GitAdvancedAutoSync")
        self.logger.setLevel(logging.INFO)

        # Create log directory
        log_dir = self.repo_path.parent if self.repo_path.exists() else Path.cwd()
        log_path = log_dir / "git_advanced_sync.log"
        
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        console_handler = logging.StreamHandler()

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def setup_repository(self):
        """Initial repository setup and automation"""
        try:
            print(f"Repository setup started: {self.repo_path}")
            
            # 1. Check directory existence and create
            if not self.repo_path.exists():
                print(f"Creating directory: {self.repo_path}")
                self.repo_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created directory: {self.repo_path}")

            # 2. Check Git repository and initialize
            if not (self.repo_path / ".git").exists():
                print("No Git repository found. Attempting to clone from remote...")
                
                # Try cloning remote repository
                if self.clone_repository():
                    print("Remote repository clone completed!")
                else:
                    print("Clone failed. Initializing new repository...")
                    self.init_new_repository()
            else:
                # Load existing repository
                self.repo = Repo(self.repo_path)
                print("Existing Git repository loaded.")
                self.logger.info("Existing repository loaded")

            # 3. Check remote repository settings
            self.setup_remote()
            
            # 4. Branch setup
            self.ensure_branch()
            
            print("Repository setup completed!")
            
        except Exception as e:
            self.logger.error(f"Repository setup failed: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def clone_repository(self):
        """Clone remote repository"""
        try:
            # Check if directory is empty
            if any(self.repo_path.iterdir()):
                print("Directory is not empty. Skipping clone.")
                return False
                
            print(f"Clone started: {self.remote_url}")
            self.repo = Repo.clone_from(self.remote_url, self.repo_path, branch=self.branch)
            self.logger.info(f"Repository cloned from {self.remote_url}")
            return True
            
        except Exception as e:
            self.logger.warning(f"Clone failed: {str(e)}")
            return False

    def init_new_repository(self):
        """Initialize new repository"""
        try:
            print("Initializing new Git repository...")
            self.repo = Repo.init(self.repo_path)
            
            # Create README.md file
            readme_path = self.repo_path / "README.md"
            if not readme_path.exists():
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {self.repo_path.name}\n\nAuto-generated Git repository.\n")
                print("README.md file created.")
            
            self.logger.info("New repository initialized")
            
        except Exception as e:
            self.logger.error(f"Repository initialization failed: {str(e)}")
            raise

    def setup_remote(self):
        """Setup remote repository"""
        try:
            if "origin" in [remote.name for remote in self.repo.remotes]:
                origin = self.repo.remote("origin")
                current_url = next(origin.urls)
                if current_url != self.remote_url:
                    origin.set_url(self.remote_url)
                    self.logger.info("Remote URL updated")
                    print("Remote repository URL updated.")
            else:
                self.repo.create_remote("origin", self.remote_url)
                self.logger.info("Remote 'origin' created")
                print("Remote 'origin' created.")
                
        except Exception as e:
            self.logger.error(f"Remote setup failed: {str(e)}")

    def ensure_branch(self):
        """Check and setup branch"""
        try:
            current_branch = self.repo.active_branch.name if self.repo.heads else None
            self.logger.info(f"Current branch: {current_branch}")
            
            local_branches = [b.name for b in self.repo.branches]

            if self.branch not in local_branches:
                if self.repo.heads:  # If existing branches exist
                    self.logger.info(f"Creating new local branch '{self.branch}'")
                    self.repo.git.checkout("-b", self.branch)
                else:  # If no initial commit exists
                    self.logger.info(f"Will create branch '{self.branch}' after first commit")
                    
            elif current_branch != self.branch:
                self.repo.git.checkout(self.branch)
                self.logger.info(f"Checked out branch '{self.branch}'")

            return True
        except Exception as e:
            self.logger.error(f"Error ensuring branch: {str(e)}")
            return False

    def is_merge_in_progress(self):
        """Check if merge is in progress"""
        merge_head = self.repo_path / ".git" / "MERGE_HEAD"
        return merge_head.exists()

    def is_rebase_in_progress(self):
        """Check if rebase is in progress"""
        rebase_dir = self.repo_path / ".git" / "rebase-merge"
        rebase_apply = self.repo_path / ".git" / "rebase-apply"
        return rebase_dir.exists() or rebase_apply.exists()

    def get_conflicted_files(self):
        """Return list of conflicted files"""
        try:
            # Check conflicted files with Git status
            result = self.repo.git.status("--porcelain")
            conflicted_files = []
            
            for line in result.split('\n'):
                if line.startswith('UU ') or line.startswith('AA ') or line.startswith('DD '):
                    file_path = line[3:].strip()
                    conflicted_files.append(file_path)
                    
            return conflicted_files
        except Exception as e:
            self.logger.error(f"Error getting conflicted files: {str(e)}")
            return []

    def resolve_conflicts_interactive(self, conflicted_files):
        """Resolve conflicted files interactively"""
        if not conflicted_files:
            return True
            
        print(f"\nConflicted files: {', '.join(conflicted_files)}")
        print("Launching editor for conflict resolution...")
        
        try:
            for file_path in conflicted_files:
                full_path = self.repo_path / file_path
                print(f"\nEditing conflicted file: {file_path}")
                print("Remove conflict markers (<<<<<<, ======, >>>>>>) in the editor, save the file, and exit.")
                
                # Edit file with vim in Git Bash
                cmd = f'start "Git Bash" "C:\\Program Files\\Git\\bin\\bash.exe" -c "cd \\"{self.repo_path}\\" && vim \\"{file_path}\\"; read -p \\"Press Enter after editing completion...\\" "'
                
                try:
                    subprocess.run(cmd, shell=True, check=True)
                    
                    # Confirm user completed editing
                    while True:
                        user_input = input(f"\nDid you complete editing {file_path}? (y/n): ").lower()
                        if user_input == 'y':
                            # Add file to staging area
                            self.repo.git.add(file_path)
                            print(f"{file_path} conflict resolution completed!")
                            break
                        elif user_input == 'n':
                            print("Please try editing again.")
                            subprocess.run(cmd, shell=True, check=True)
                        else:
                            print("Please enter y or n.")
                            
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"Editor execution failed: {str(e)}")
                    print(f"Editor execution failed: {file_path}")
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Error resolving conflicts: {str(e)}")
            return False

    def generate_commit_message(self, file_count=0):
        """Generate commit message"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Generate basic message
        message = COMMIT_MESSAGE_TEMPLATE.format(timestamp=timestamp)
        
        # Add prefix
        if CUSTOM_COMMIT_PREFIX:
            message = f"{CUSTOM_COMMIT_PREFIX} {message}"
        
        # Add file count
        if INCLUDE_FILE_COUNT and file_count > 0:
            message += f" ({file_count} files changed)"
        
        return message

    def generate_merge_message(self):
        """Generate merge message"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = MERGE_MESSAGE_TEMPLATE.format(timestamp=timestamp)
        
        if CUSTOM_COMMIT_PREFIX:
            message = f"{CUSTOM_COMMIT_PREFIX} {message}"
        
        return message

    def complete_merge_or_rebase(self):
        """Complete merge or rebase"""
        try:
            if self.is_merge_in_progress():
                # Complete 3-way merge
                print("Completing 3-way merge...")
                commit_message = f"Merge completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                self.repo.git.commit("-m", commit_message)
                self.logger.info("Merge completed successfully")
                print("Merge completed!")
                return True
                
            elif self.is_rebase_in_progress():
                # Continue rebase
                print("Continuing rebase...")
                self.repo.git.rebase("--continue")
                self.logger.info("Rebase continued successfully")
                print("Rebase continued!")
                return True
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error completing merge/rebase: {str(e)}")
            print(f"Error completing merge/rebase: {str(e)}")
            return False

    def sync_with_remote(self):
        """Synchronize with remote repository"""
        try:
            print(f"\nRemote repository sync started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Check current branch
            if not self.ensure_branch():
                return False

            # Commit local changes
            self.repo.git.add(".")
            
            if self.repo.is_dirty() or len(self.repo.untracked_files) > 0:
                # Calculate number of changed files
                file_count = len(self.repo.untracked_files) + len([item.a_path for item in self.repo.index.diff(None)])
                commit_message = self.generate_commit_message(file_count)
                self.repo.index.commit(commit_message)
                self.logger.info(f"Local changes committed: {commit_message}")
                print(f"Local changes committed: {commit_message}")

            # Fetch changes from remote repository
            print("Fetching changes from remote repository...")
            try:
                origin = self.repo.remote("origin")
                origin.fetch()
                self.logger.info("Fetched from remote")
                
                # Check remote branch existence
                remote_branch = f"origin/{self.branch}"
                if remote_branch in [str(ref) for ref in self.repo.refs]:
                    print(f"Attempting to merge with remote branch {remote_branch}...")
                    
                    try:
                        # Attempt merge
                        self.repo.git.merge(remote_branch, "--no-ff")
                        print("Remote changes merged successfully!")
                        
                    except Exception as merge_error:
                        if "conflict" in str(merge_error).lower():
                            print("Conflicts detected!")
                            self.logger.warning("Merge conflict detected")
                            
                            # Check conflicted files
                            conflicted_files = self.get_conflicted_files()
                            
                            if conflicted_files and AUTO_RESOLVE_CONFLICTS:
                                print("Starting automatic conflict resolution...")
                                
                                if self.resolve_conflicts_interactive(conflicted_files):
                                    # Complete merge/rebase after conflict resolution
                                    if self.complete_merge_or_rebase():
                                        print("Conflict resolution and merge completed!")
                                    else:
                                        print("Error occurred while completing merge.")
                                        return False
                                else:
                                    print("Conflict resolution failed.")
                                    return False
                            else:
                                print("Manual conflict resolution required.")
                                self.logger.error("Manual conflict resolution required")
                                return False
                        else:
                            raise merge_error
                else:
                    print(f"Remote branch {self.branch} does not exist. Pushing as new branch.")

                # Push to remote
                print("Pushing to remote repository...")
                push_info = origin.push(self.branch)
                
                for info in push_info:
                    self.logger.info(f"Push result: {info.summary}")
                    print(f"Push result: {info.summary}")
                
                print("Synchronization completed!")
                return True
                
            except Exception as e:
                self.logger.error(f"Remote sync failed: {str(e)}")
                print(f"Remote sync failed: {str(e)}")
                return False

        except Exception as e:
            self.logger.error(f"Error during sync: {str(e)}")
            print(f"Error during sync: {str(e)}")
            return False

    def sync(self):
        """Execute scheduled synchronization"""
        try:
            print("\n" + "="*60)
            print(f"Auto sync execution: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60)
            
            success = self.sync_with_remote()
            
            if success:
                print("✅ Sync successful!")
            else:
                print("❌ Sync failed!")
            
            # Display next execution time
            next_run = schedule.next_run()
            if next_run:
                print(f"📅 Next sync scheduled: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("="*60)
            
        except Exception as e:
            self.logger.error(f"Scheduled sync failed: {str(e)}")
            print(f"❌ Scheduled sync failed: {str(e)}")


class GitAdvancedAutoSyncService(win32serviceutil.ServiceFramework):
    _svc_name_ = "GitAdvancedAutoSyncService"
    _svc_display_name_ = "Git Advanced Auto Sync Service"
    _svc_description_ = "Advanced Git Auto Sync Service (includes conflict resolution)"

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
        try:
            git_sync = GitAdvancedAutoSync(REPO_PATH, REMOTE_URL, BRANCH)

            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE, 
                0, 
                ("Initial sync started", "")
            )

            if git_sync.sync_with_remote():
                servicemanager.LogMsg(
                    servicemanager.EVENTLOG_INFORMATION_TYPE, 
                    0, 
                    ("Initial sync completed", "")
                )
            else:
                servicemanager.LogMsg(
                    servicemanager.EVENTLOG_WARNING_TYPE, 
                    0, 
                    ("Initial sync failed", "")
                )

            schedule.every(SYNC_INTERVAL).minutes.do(git_sync.sync)

            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                0,
                (f"Git advanced auto sync started. Syncing {BRANCH} branch every {SYNC_INTERVAL} minutes.", "")
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
                (f"Service error: {str(e)}", "")
            )

def restart_as_background():
    """Restart as background process"""
    script_path = os.path.abspath(sys.argv[0])
    
    args = [arg for arg in sys.argv[1:] if arg != "--from-bat"]
    if "--background" not in args:
        args.append("--background")
    
    subprocess.Popen([sys.executable, script_path] + args)
    
    print("\nProgram will run in background. This window will close automatically in 3 seconds.")
    time.sleep(3)
    sys.exit(0)

def run_foreground():
    """Run in foreground"""
    if from_bat and "--background" not in sys.argv:
        restart_as_background()
        return
    
    try:
        print("✅ All required modules are ready!")
        print("🚀 Git Advanced Auto Sync System v3.0")
        print("="*60)
        print("New Features:")
        print("✅ Auto-install required modules")
        print("✅ Automatic merge/rebase handling")
        print("✅ Auto-launch editor on conflicts")
        print("✅ Complete automation of initial repository setup")
        print("✅ Automatic pull and merge of remote changes")
        print("="*60)
        
        git_sync = GitAdvancedAutoSync(REPO_PATH, REMOTE_URL, BRANCH)
        
        print(f"\n📁 Repository path: {REPO_PATH}")
        print(f"🌐 Remote repository: {REMOTE_URL}")
        print(f"🔀 Branch: {BRANCH}")
        print(f"⏰ Sync interval: {SYNC_INTERVAL} minutes")
        
        # Execute initial sync
        print("\n🔄 Executing immediate sync at program start...")
        if git_sync.sync_with_remote():
            print("✅ Initial sync completed!")
        else:
            print("❌ Initial sync failed. Check logs.")
        
        # Setup scheduler
        print(f"\n⚙️ Auto sync setup completed. Will sync every {SYNC_INTERVAL} minutes.")
        print("💡 Editor will launch automatically when conflicts occur.")
        print("⚠️ Closing this window will stop auto sync.")
        print("\n🛑 Press 'Ctrl+C' to exit.\n")
        
        schedule.every(SYNC_INTERVAL).minutes.do(git_sync.sync)
        
        next_run = schedule.next_run()
        if next_run:
            print(f"📅 Next sync scheduled: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            count = 0
            print("\n🔄 Program running... Waiting for auto sync.")
            print("-" * 60)
            
            while True:
                schedule.run_pending()
                
                if count % 60 == 0 and count > 0:
                    now = datetime.now()
                    next_run = schedule.next_run()
                    if next_run:
                        time_left = int((next_run - now).total_seconds())
                        minutes = time_left // 60
                        seconds = time_left % 60
                        print(f"{now.strftime('%H:%M:%S')} - ⏰ {minutes}m {seconds}s until next sync")
                
                time.sleep(1)
                count += 1
                
        except KeyboardInterrupt:
            print("\n\n🛑 Terminating program...")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n💥 Critical error occurred: {str(e)}")
        print(traceback.format_exc())
        print("Program will terminate in 10 seconds...")
        time.sleep(10)
        sys.exit(1)

if __name__ == "__main__":
    if "--service" in sys.argv:
        win32serviceutil.HandleCommandLine(GitAdvancedAutoSyncService)
    else:
        run_foreground()