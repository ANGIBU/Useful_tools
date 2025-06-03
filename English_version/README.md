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

- `Git_Advanced_Automate.vbs`  
  - Background execution (can be registered in startup programs)

- `Git_Automation_System_Beginner_Guide.md`  
  - Detailed usage guide for beginners

### ⚙️ Features
- Automatic installation of required modules (`gitpython`, `schedule`, `pywin32`)
- Bidirectional sync (pull + push)
- Auto Git Bash vim editor launch on conflicts
- Automatic 3-way merge/rebase detection and handling
- Customizable commit message support
- Configurable auto-sync intervals (default 10 minutes)
- Windows service installation available

---

## 📁 `Git Auto Update (git auto update)`

### 📌 Purpose  
Automatically commit and push changes to a local Git repository, making backups and collaboration easier.

### 📄 Files Included  
- `git_commit.py`  
  - Detects changed files and automatically commits them.  
  - Commit message format: `Automated Commit Update at YYYY-MM-DD HH:MM:SS`

- `git_push.py`  
  - Force pushes the committed content to a specified remote branch.

- `run_automate.bat`  
  - A batch file that runs the above two scripts to start the automation.  
  - Can be registered in Windows startup programs for automatic execution.

### ⚙️ Features
- Uses `GitPython`, `pywin32`, and `schedule` libraries  
- Automatically runs every 10 minutes  
- Supports console and log file output

---

## 📁 `Organize Videos (organize videos)`

### 📌 Purpose  
Organizes video files into folders by creation/modification date in `YYYY-MM` format and compresses each into ZIP files.

### 📄 Files Included  
- `organize_videos.py`  
  - Moves and organizes video files into year/month folders.  
  - Compresses each folder into ZIP files.

### ⚙️ Features
- Supported extensions: `.mp4`, `.avi`, `.mov`, `.mkv`, etc.  
- Creates folders based on dates (`2024-04`, `2024-05`, ...)  
- Option to delete the original files after organizing

---

## 📁 `Split Images by Size (split images by size)`

### 📌 Purpose  
Splits image files into folders by a specified size and compresses each folder into a ZIP file.

### 📄 Files Included  
- `filephoto.py`  
  - Analyzes image files and sorts them by size  
  - Automatically compresses them into ZIP files.

### ⚙️ Features
- Supported extensions: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`  
- Uses size-based sorting algorithm  
- Option to display progress and delete folders after compression