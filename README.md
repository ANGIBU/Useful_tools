<img src="https://www.spriters-resource.com/resources/sheet_icons/168/171517.gif?updated=1648938576" alt="도트 커비 5" width="100"/>

## 📁 `깃 자동 업데이트 (git auto update)`

### 📌 목적  
로컬 Git 저장소의 변경 사항을 자동 커밋 및 푸시하여 백업과 협업을 간편하게 만듭니다.

### 📄 구성 파일  
- `git_commit.py`  
  - 변경된 파일을 감지하고 자동으로 커밋합니다.  
  - 커밋 메시지 포맷: `Automated Commit Update at YYYY-MM-DD HH:MM:SS`

- `git_push.py`  
  - 커밋된 내용을 지정된 원격 브랜치에 **강제 푸시(force push)** 합니다.

- `run_automate.bat`  
  - 위 두 스크립트를 실행하여 자동화를 시작하는 배치 파일입니다.
  - 윈도우 시작 프로그램에 등록하여 자동 실행 가능

### ⚙️ 특징
- `GitPython`, `pywin32`, `schedule` 라이브러리 사용
- 10분 간격 자동 실행
- 콘솔 및 로그 파일 출력 지원

---

## 📁 `동영상 정리 (organize videos)`

### 📌 목적  
동영상 파일들을 생성/수정일 기준으로 `YYYY-MM` 형식의 폴더로 정리하고, 각각을 ZIP 파일로 압축합니다.

### 📄 구성 파일  
- `organize_videos.py`  
  - 동영상 파일을 연/월 폴더로 이동 및 정리  
  - 각 폴더를 ZIP으로 압축

### ⚙️ 특징
- 지원 확장자: `.mp4`, `.avi`, `.mov`, `.mkv` 등
- 날짜 기준 폴더 생성 (`2024-04`, `2024-05`, ...)
- 정리 후 원본 삭제 여부 선택 가능

---

## 📁 `사진 일정 용량 분할 (split images by size)`

### 📌 목적  
이미지 파일들을 설정한 용량 만큼 폴더로 나눈 후, 각각 ZIP 파일로 압축합니다.

### 📄 구성 파일  
- `filephoto.py`  
  - 이미지 파일들을 분석하여 용량 기준으로 분배  
  - 자동으로 ZIP 압축 수행

### ⚙️ 특징
- 지원 확장자: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`
- 크기 기준 정렬 분배 알고리즘 사용
- 진행률 출력 및 압축 후 폴더 삭제 여부 선택 가능


---------------------------------------------------------------------------


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
