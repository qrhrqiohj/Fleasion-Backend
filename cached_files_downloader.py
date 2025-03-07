import json
import sys
import os
import zipfile
import urllib.request
import shutil

file_id = sys.argv[1]
game_pre = sys.argv[2]
BASE_URL = f"https://api.github.com/repos/{file_id}/contents"

def get_files(url, download_dir):
    response = urllib.request.urlopen(url)
    if response.status != 200:
        print(f"Failed to fetch contents from {url}. HTTP Status Code: {response.status}")
        return
    
    files = json.loads(response.read())
    for file in files:
        if file["type"] == "file" and file["name"].endswith(".zip"):
            download_file(file["download_url"], file["name"], download_dir)
        elif file["type"] == "dir":
            get_files(file["url"], download_dir)

def download_file(file_url, file_name, save_dir):
    save_path = os.path.join(save_dir, file_name)
    print(f"Downloading {file_name}...")
    with urllib.request.urlopen(file_url) as response:
        if response.status == 200:
            with open(save_path, "wb") as f:
                f.write(response.read())
            print(f"Saved {file_name} to {save_path}")
        else:
            print(f"Failed to download {file_name}. HTTP Status Code: {response.status}")

def unzip_and_merge(zip_dir, merge_dir):
    for file_name in os.listdir(zip_dir):
        if file_name.endswith(".zip"):
            zip_path = os.path.join(zip_dir, file_name)
            temp_dir = os.path.join(zip_dir, "temp_unzip")
            os.makedirs(temp_dir, exist_ok=True)

            print(f"Unzipping {file_name}...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            for root, _, files in os.walk(temp_dir):
                for file in files:
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(merge_dir, os.path.relpath(src_file, temp_dir))
                    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                    shutil.move(src_file, dest_file)

            shutil.rmtree(temp_dir)
            print(f"Merged contents of {file_name} into {merge_dir}")

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
        return 0

def main():
    proceed = confirm_download()
    if proceed != 0:
        global DOWNLOAD_DIR, MERGED_DIR

        DOWNLOAD_DIR = os.path.join(game_pre, "./do_not_delete")
        MERGED_DIR = os.path.join(game_pre, "./cached_files")

        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        os.makedirs(MERGED_DIR, exist_ok=True)
        print("\nStarting download process...")
        get_files(BASE_URL, DOWNLOAD_DIR)
        print("Download process complete.")

        print("Starting unzip and merge process...")
        unzip_and_merge(DOWNLOAD_DIR, MERGED_DIR)
        print(f"All contents have been merged into {MERGED_DIR}")

        print("Cleaning up download directory...")
        cleanup(DOWNLOAD_DIR)

main()
