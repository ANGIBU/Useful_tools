#!/usr/bin/env python3
# image_splitter.py
import os
import shutil
import zipfile
from pathlib import Path

# Enter the paths here
source_dir = r"image_path"      # Source directory path where original images are located
output_dir = r"save_path"       # Directory path to save divided images
max_size_mb = 512               # Maximum size per folder (MB)

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
            print(f"Progress: {copied_files}/{total_files} ({(copied_files/total_files)*100:.1f}%) - {file_path} -> {dest_path}")

def zip_folders(output_folders):
    print("Compressing folders...")
    for folder in output_folders:
        zip_path = f"{folder}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(folder))
                    zipf.write(file_path, arcname)
        print(f"Compression completed: {zip_path}")

def calculate_required_folders(image_files, max_size_bytes):
    total_size = sum(size for _, size in image_files)
    num_folders = (total_size + max_size_bytes - 1) // max_size_bytes
    return max(1, int(num_folders))

def main():
    max_size_bytes = max_size_mb * 1024 * 1024
    
    print(f"Source directory: {source_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Maximum size per folder: {max_size_mb}MB")
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("Scanning image files...")
    image_files = get_all_image_files(source_dir)
    print(f"Found {len(image_files)} image files in total.")
    
    if not image_files:
        print("No image files found. Exiting.")
        return
    
    num_folders = calculate_required_folders(image_files, max_size_bytes)
    print(f"Number of folders required: {num_folders}")
    
    output_folders = create_output_folders(output_dir, num_folders)
    
    print("Creating image file distribution plan...")
    distribution = distribute_images(image_files, output_folders, max_size_bytes)
    
    print("Copying image files...")
    copy_images(distribution)
    
    # Create zip files from folders
    zip_folders(output_folders)
    
    # Print folder information after compression
    print("Task completed!")
    
    for folder in output_folders:
        folder_size_bytes = sum(os.path.getsize(os.path.join(folder, f)) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)))
        folder_size_mb = folder_size_bytes / (1024 * 1024)
        zip_size_bytes = os.path.getsize(f"{folder}.zip") if os.path.exists(f"{folder}.zip") else 0
        zip_size_mb = zip_size_bytes / (1024 * 1024)
        print(f"{folder}: {len(os.listdir(folder))} files, {folder_size_mb:.2f}MB (zip file: {zip_size_mb:.2f}MB)")
    
    # Ask whether to delete original folders after compression
    delete_folders = input("Compression is complete. Would you like to delete the original folders? (y/n): ")
    if delete_folders.lower() == 'y':
        for folder in output_folders:
            shutil.rmtree(folder)
            print(f"Deleted: {folder}")

if __name__ == "__main__":
    main()