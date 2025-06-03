## 📁 `Git Advanced Auto Sync System v3.0`

### 📌 Purpose  
Fully automated Git synchronization system that handles code backup, conflict resolution, and team collaboration with one-click setup.

### 📄 Files Included  
- `git_advanced_automate.py`  
  - Main program with automatic module installation
  - Automatic merge/rebase handling and conflict resolution
  - Commit message format: `Auto commit: YYYY-MM-DD HH:MM:SS (N files changed)`

- `Git_Advanced_Automate.bat`  
  - Batch file for program execution
  - Automatic Python module installation and execution

- `Git_Advanced_Automate.vbs`  
  - Background execution (can be registered in startup programs)

- `requirements.txt`  
  - List of required Python modules (auto-generated)

- `Git_Automation_System_Beginner_Guide.md`  
  - Detailed usage guide for beginners

### ⚙️ Key Features
- **Full Auto Initialization**: Automatic folder creation, Git init, remote clone
- **Auto Module Installation**: Automatic check and install of `gitpython`, `schedule`, `pywin32`
- **Bidirectional Sync**: Auto pull remote changes + push local changes
- **Auto Conflict Resolution**: Git Bash vim editor auto-launch on conflicts
- **3-way Merge/Rebase Support**: Automatic detection and handling
- **Customizable Commit Messages**: Configurable prefix, format, file count display
- **Scheduling**: Configurable auto-sync intervals (default 10 minutes)
- **Service Mode**: Can be installed as Windows service
- **Logging**: Detailed automatic operation logs

### 🚀 New Features (v3.0)
- Auto-install missing modules and restart program
- Retry with pip upgrade on installation failure
- Automatic requirements.txt generation
- Beginner-friendly error messages and solutions

### ⚙️ Configuration
Modify CONFIG section in `git_advanced_automate.py`:
```python
REPO_PATH = r"C:\MyProject"  # Local repository path
REMOTE_URL = "https://github.com/username/repository.git"  # GitHub repository
BRANCH = "main"  # Branch name
SYNC_INTERVAL = 10  # Sync interval (minutes)
COMMIT_MESSAGE_TEMPLATE = "Auto commit: {timestamp}"  # Commit message format
CUSTOM_COMMIT_PREFIX = "[AUTO]"  # Commit message prefix
```

### 💡 Use Cases
- **Individual Development**: Auto-backup during work to prevent data loss
- **Team Collaboration**: Auto-guided conflict resolution
- **Beginners**: Safe version control without Git commands knowledge
- **Automation**: Set once, run fully automated