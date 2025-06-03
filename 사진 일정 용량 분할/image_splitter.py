#!/usr/bin/env python3
# 디렉터리 정보: 이미지 파일들을 512MB 이하 크기의 폴더로 분할하고 압축하는 스크립트
import os
import shutil
import zipfile
from pathlib import Path

# 여기에 경로를 입력하세요
source_dir = r"이미지 경로"  # 원본 이미지가 있는 디렉토리 경로
output_dir = r"저장할 경로"    # 분할된 이미지를 저장할 디렉토리 경로
max_size_mb = 512                # 폴더당 최대 크기(MB)

def get_all_image_files(source_dir):
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    image_files = []
    
    for root, _, files in os.walk(source_dir):
        for file in files:
            if os.path.splitext(file)[1].lower() in image_extensions:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                image_files.append((file_path, file_size))
    
    return image_files

def create_output_folders(output_dir, num_folders):
    folders = []
    for i in range(1, num_folders + 1):
        folder_name = os.path.join(output_dir, f"images_{i:03d}")
        os.makedirs(folder_name, exist_ok=True)
        folders.append(folder_name)
    return folders

def distribute_images(image_files, output_folders, max_size_bytes):
    current_folder_index = 0
    current_size = 0
    distribution = {folder: [] for folder in output_folders}
    
    image_files.sort(key=lambda x: x[1], reverse=True)
    
    for file_path, file_size in image_files:
        if current_size + file_size > max_size_bytes and current_folder_index + 1 < len(output_folders):
            current_folder_index += 1
            current_size = 0
        
        distribution[output_folders[current_folder_index]].append(file_path)
        current_size += file_size
    
    return distribution

def copy_images(distribution):
    total_files = sum(len(files) for files in distribution.values())
    copied_files = 0
    
    for folder, files in distribution.items():
        for file_path in files:
            dest_path = os.path.join(folder, os.path.basename(file_path))
            shutil.copy2(file_path, dest_path)
            copied_files += 1
            print(f"진행률: {copied_files}/{total_files} ({(copied_files/total_files)*100:.1f}%) - {file_path} -> {dest_path}")

def zip_folders(output_folders):
    print("폴더 압축 중...")
    for folder in output_folders:
        zip_path = f"{folder}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(folder))
                    zipf.write(file_path, arcname)
        print(f"압축 완료: {zip_path}")

def calculate_required_folders(image_files, max_size_bytes):
    total_size = sum(size for _, size in image_files)
    num_folders = (total_size + max_size_bytes - 1) // max_size_bytes
    return max(1, int(num_folders))

def main():
    max_size_bytes = max_size_mb * 1024 * 1024
    
    print(f"소스 디렉터리: {source_dir}")
    print(f"출력 디렉터리: {output_dir}")
    print(f"폴더당 최대 크기: {max_size_mb}MB")
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("이미지 파일 스캔 중...")
    image_files = get_all_image_files(source_dir)
    print(f"총 {len(image_files)}개의 이미지 파일을 찾았습니다.")
    
    if not image_files:
        print("이미지 파일을 찾을 수 없습니다. 종료합니다.")
        return
    
    num_folders = calculate_required_folders(image_files, max_size_bytes)
    print(f"필요한 폴더 수: {num_folders}")
    
    output_folders = create_output_folders(output_dir, num_folders)
    
    print("이미지 파일 분배 계획 생성 중...")
    distribution = distribute_images(image_files, output_folders, max_size_bytes)
    
    print("이미지 파일 복사 중...")
    copy_images(distribution)
    
    # 폴더를 압축파일로 만들기
    zip_folders(output_folders)
    
    # 압축 후 폴더 정보 출력
    print("작업 완료!")
    
    for folder in output_folders:
        folder_size_bytes = sum(os.path.getsize(os.path.join(folder, f)) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)))
        folder_size_mb = folder_size_bytes / (1024 * 1024)
        zip_size_bytes = os.path.getsize(f"{folder}.zip") if os.path.exists(f"{folder}.zip") else 0
        zip_size_mb = zip_size_bytes / (1024 * 1024)
        print(f"{folder}: {len(os.listdir(folder))}개 파일, {folder_size_mb:.2f}MB (압축 파일: {zip_size_mb:.2f}MB)")
    
    # 압축 후 원본 폴더 삭제 여부 묻기
    delete_folders = input("압축이 완료되었습니다. 원본 폴더를 삭제하시겠습니까? (y/n): ")
    if delete_folders.lower() == 'y':
        for folder in output_folders:
            shutil.rmtree(folder)
            print(f"삭제됨: {folder}")

if __name__ == "__main__":
    main()