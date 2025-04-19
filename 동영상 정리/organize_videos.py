# 동영상 파일을 생성일 기준으로 YYYY-MM 형식 폴더로 정리하는 자동화 스크립트

import os
import shutil
from datetime import datetime
from pathlib import Path

SOURCE_DIR = r"D:\your\video\folder\path"  # 여기에 정리할 동영상 폴더 경로 입력
VIDEO_EXTENSIONS = ('.mp4', '.mov', '.avi', '.mkv', '.flv')

def get_file_month(file_path: Path) -> str:
    try:
        timestamp = file_path.stat().st_ctime
    except AttributeError:
        timestamp = file_path.stat().st_mtime

    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m')

def organize_videos_by_month(src_dir: str):
    src_path = Path(src_dir)

    if not src_path.exists():
        print(f"경로가 존재하지 않습니다: {src_dir}")
        return

    for file in src_path.iterdir():
        if file.is_file() and file.suffix.lower() in VIDEO_EXTENSIONS:
            month_str = get_file_month(file)
            target_dir = src_path / month_str
            target_dir.mkdir(exist_ok=True)

            target_file = target_dir / file.name

            count = 1
            while target_file.exists():
                target_file = target_dir / f"{file.stem}_{count}{file.suffix}"
                count += 1

            shutil.move(str(file), str(target_file))
            print(f"Moved: {file.name} → {target_file}")

    print("정리가 완료되었습니다.")

if __name__ == "__main__":
    organize_videos_by_month(SOURCE_DIR)