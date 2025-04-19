# 동영상 파일을 생성일 기준으로 YYYY-MM 폴더로 정리하고, 각 폴더를 zip 파일로 압축하는 스크립트

import os
import shutil
from datetime import datetime
from pathlib import Path
import zipfile

SOURCE_DIR = r"D:\your\video\folder\path"  # 여기에 정리할 동영상 폴더 경로 입력
VIDEO_EXTENSIONS = ('.mp4', '.mov', '.avi', '.mkv', '.flv')

def get_file_month(file_path: Path) -> str:
    try:
        timestamp = file_path.stat().st_ctime
    except AttributeError:
        timestamp = file_path.stat().st_mtime
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m')

def move_videos_to_month_folders(src_dir: Path):
    for file in src_dir.iterdir():
        if file.is_file() and file.suffix.lower() in VIDEO_EXTENSIONS:
            month_folder = get_file_month(file)
            target_dir = src_dir / month_folder
            target_dir.mkdir(exist_ok=True)

            target_file = target_dir / file.name
            count = 1
            while target_file.exists():
                target_file = target_dir / f"{file.stem}_{count}{file.suffix}"
                count += 1

            shutil.move(str(file), str(target_file))
            print(f"Moved: {file.name} → {target_file}")

def compress_month_folders(src_dir: Path):
    for folder in src_dir.iterdir():
        if folder.is_dir() and folder.name[:4].isdigit() and '-' in folder.name:
            zip_path = src_dir / f"{folder.name}.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(folder):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(folder.parent)
                        zipf.write(file_path, arcname)
            shutil.rmtree(folder)
            print(f"Compressed and removed: {folder.name}")

def organize_and_compress(src_path_str: str):
    src_path = Path(src_path_str)
    if not src_path.exists():
        print(f"경로가 존재하지 않습니다: {src_path}")
        return
    move_videos_to_month_folders(src_path)
    compress_month_folders(src_path)
    print("모든 파일이 정리 및 압축되었습니다.")

if __name__ == "__main__":
    organize_and_compress(SOURCE_DIR)