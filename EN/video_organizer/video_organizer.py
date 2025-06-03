# video_organizer.py

"""
Video File Organizer (Uncompressed Version)

Organizes video files from a specified folder into YYYY-MM folders based on creation date.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
import logging
from tqdm import tqdm

# User Settings
SOURCE_DIR = r"Enter your path here"  # Change this path to your actual video folder
VIDEO_EXTENSIONS = ('.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.webm', '.m4v', '.3gp')

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("video_organizer.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger()

def get_file_creation_date(file_path: Path) -> datetime:
    try:
        if os.name == 'nt':
            timestamp = file_path.stat().st_ctime
        else:
            try:
                timestamp = file_path.stat().st_birthtime
            except AttributeError:
                timestamp = file_path.stat().st_mtime
    except Exception as e:
        logger.warning(f"Error occurred while getting creation date for file {file_path}: {e}")
        timestamp = file_path.stat().st_mtime
    
    return datetime.fromtimestamp(timestamp)

def get_folder_name(file_path: Path, folder_format: str) -> str:
    dt = get_file_creation_date(file_path)
    return dt.strftime(folder_format)

def move_videos_to_folders(src_dir: Path, folder_format: str, logger):
    logger.info(f"Organizing video files in '{src_dir}' folder into date-based folders.")
    
    video_files = [f for f in src_dir.iterdir() 
                  if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS]
    
    if not video_files:
        logger.info("No video files to move.")
        return []
    
    moved_folders = set()
    
    for file in tqdm(video_files, desc="Moving files"):
        try:
            folder_name = get_folder_name(file, folder_format)
            target_dir = src_dir / folder_name
            target_dir.mkdir(exist_ok=True)
            moved_folders.add(target_dir)
            
            target_file = target_dir / file.name
            if target_file.exists():
                base_name = file.stem
                extension = file.suffix
                counter = 1
                while target_file.exists():
                    new_name = f"{base_name}_{counter}{extension}"
                    target_file = target_dir / new_name
                    counter += 1
            
            shutil.move(str(file), str(target_file))
            logger.debug(f"Move completed: {file.name} → {target_file}")
            
        except Exception as e:
            logger.error(f"Error occurred while moving file '{file.name}': {e}")
    
    logger.info(f"Total {len(video_files)} files organized into {len(moved_folders)} folders.")
    return list(moved_folders)

def main():
    try:
        global logger
        logger = setup_logger()
        logger.info("Video file organizer program started")
        
        source_dir = Path(SOURCE_DIR)
        folder_format = '%Y-%m'
        
        if not source_dir.exists():
            raise FileNotFoundError(f"Path does not exist: {source_dir}")
        if not source_dir.is_dir():
            raise NotADirectoryError(f"Specified path is not a directory: {source_dir}")
        
        logger.info(f"Target folder: {source_dir}")
        move_videos_to_folders(source_dir, folder_format, logger)
        
        logger.info("All tasks completed successfully.")
        
    except Exception as e:
        if 'logger' in globals():
            logger.error(f"Error occurred during program execution: {e}")
        else:
            print(f"Error occurred during initialization: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())