"""
비디오 파일 정리 프로그램 (압축 제거 버전)

지정된 폴더에서 비디오 파일을 생성일 기준 YYYY-MM 폴더로 이동 정리합니다.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
import logging
from tqdm import tqdm

# 사용자 설정
SOURCE_DIR = r"경로를 입력하세요"  # 이 경로를 실제 비디오 폴더로 수정하세요
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
        logger.warning(f"파일 {file_path}의 생성일자를 가져오는 중 오류 발생: {e}")
        timestamp = file_path.stat().st_mtime
    
    return datetime.fromtimestamp(timestamp)

def get_folder_name(file_path: Path, folder_format: str) -> str:
    dt = get_file_creation_date(file_path)
    return dt.strftime(folder_format)

def move_videos_to_folders(src_dir: Path, folder_format: str, logger):
    logger.info(f"'{src_dir}' 폴더의 비디오 파일을 날짜별 폴더로 정리합니다.")
    
    video_files = [f for f in src_dir.iterdir() 
                  if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS]
    
    if not video_files:
        logger.info("이동할 비디오 파일이 없습니다.")
        return []
    
    moved_folders = set()
    
    for file in tqdm(video_files, desc="파일 이동 중"):
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
            logger.debug(f"이동 완료: {file.name} → {target_file}")
            
        except Exception as e:
            logger.error(f"파일 '{file.name}' 이동 중 오류 발생: {e}")
    
    logger.info(f"총 {len(video_files)}개 파일이 {len(moved_folders)}개 폴더로 정리되었습니다.")
    return list(moved_folders)

def main():
    try:
        global logger
        logger = setup_logger()
        logger.info("비디오 파일 정리 프로그램 시작")
        
        source_dir = Path(SOURCE_DIR)
        folder_format = '%Y-%m'
        
        if not source_dir.exists():
            raise FileNotFoundError(f"경로가 존재하지 않습니다: {source_dir}")
        if not source_dir.is_dir():
            raise NotADirectoryError(f"지정한 경로는 폴더가 아닙니다: {source_dir}")
        
        logger.info(f"대상 폴더: {source_dir}")
        move_videos_to_folders(source_dir, folder_format, logger)
        
        logger.info("모든 작업이 완료되었습니다.")
        
    except Exception as e:
        if 'logger' in globals():
            logger.error(f"프로그램 실행 중 오류 발생: {e}")
        else:
            print(f"초기화 중 오류 발생: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
