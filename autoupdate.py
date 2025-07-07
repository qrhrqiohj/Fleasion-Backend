import json
import sys
import os
import zipfile
import urllib.request
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

file_id = sys.argv[1]
game_pre = sys.argv[2]
BASE_URL = f"https://api.github.com/repos/{file_id}/contents"

def get_files(url, download_dir):
    response = urllib.request.urlopen(url)
    if response.status != 200:
        print(f"Failed to fetch contents from {url}. HTTP Status Code: {response.status}")
        return []
    
    files = json.loads(response.read())
    file_tasks = []
    for file in files:
        if file["type"] == "file" and file["name"].endswith(".zip"):
            file_tasks.append((file["download_url"], file["name"], download_dir))
        elif file["type"] == "dir":
            file_tasks.extend(get_files(file["url"], download_dir))
    return file_tasks

def download_file(file_url, file_name, save_dir):
    save_path = os.path.join(save_dir, file_name)
    print(f"Downloading {file_name}...")
    try:
        with urllib.request.urlopen(file_url) as response:
            if response.status == 200:
                with open(save_path, "wb") as f:
                    f.write(response.read())
                print(f"Saved {file_name} to {save_path}")
            else:
                print(f"Failed to download {file_name}. HTTP Status Code: {response.status}")
    except Exception as e:
        print(f"Error downloading {file_name}: {e}")

def unzip_and_merge_file(zip_file_name, zip_dir, merge_dir):
    zip_path = os.path.join(zip_dir, zip_file_name)
    temp_dir = os.path.join(zip_dir, f"temp_unzip_{zip_file_name}")
    os.makedirs(temp_dir, exist_ok=True)

    print(f"Unzipping {zip_file_name}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        for root, _, files in os.walk(temp_dir):
            for file in files:
                src_file = os.path.join(root, file)
                dest_file = os.path.join(merge_dir, os.path.relpath(src_file, temp_dir))
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                shutil.move(src_file, dest_file)

        shutil.rmtree(temp_dir)
        print(f"Merged contents of {zip_file_name} into {merge_dir}")
    except Exception as e:
        print(f"Error processing {zip_file_name}: {e}")

def cleanup(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
        print(f"Deleted directory: {directory}")

def confirm_download():
    with urllib.request.urlopen(BASE_URL) as response:
        contents = json.load(response)
        total_size = 0
        for item in contents:
            if item['type'] == 'file':
                total_size += item['size']

        total_size_mb = total_size / (1024 * 1024)
    print(f"\nWARNING: The total download size is approximately {total_size_mb:.2f} MB.")
    confirm = input("Do you still want to continue? (yes/no)\n: ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("\nDownload aborted.")
        return False
    return True

def main():
    if not confirm_download():
        return

    global DOWNLOAD_DIR, MERGED_DIR
    DOWNLOAD_DIR = os.path.join(game_pre, "./do_not_delete")
    MERGED_DIR = os.path.join(game_pre, "./cached_files")

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(MERGED_DIR, exist_ok=True)
    print("\nStarting download process...")

    # Collect all file tasks
    file_tasks = get_files(BASE_URL, DOWNLOAD_DIR)

    # Download files concurrently
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(download_file, file_url, file_name, save_dir)
            for file_url, file_name, save_dir in file_tasks
        ]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error in download task: {e}")

    print("Download process complete.")

    print("Starting unzip and merge process...")
    # Unzip and merge files concurrently
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(unzip_and_merge_file, file_name, DOWNLOAD_DIR, MERGED_DIR)
            for _, file_name, _ in file_tasks
        ]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error in unzip/merge task: {e}")

    print(f"All contents have been merged into {MERGED_DIR}")

    print("Cleaning up download directory...")
    cleanup(DOWNLOAD_DIR)

main()
