import urllib.request
import subprocess
import os
import zipfile
import json
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
import getpass as gp
from pathlib import Path

temp_roblox_http_dir = os.path.join(os.getenv('TEMP'), 'Roblox', 'http')
os.makedirs(temp_roblox_http_dir, exist_ok=True)
print(f"Ensured directory exists: {temp_roblox_http_dir}")

LOCAL_ROBLOX_FOLDER = Path('~/AppData/Local/Roblox').expanduser()
DB_PATH = LOCAL_ROBLOX_FOLDER / 'rbx-storage.db'
USERS_TO_REMOVE: list[str] = ['Users', 'Everyone', 'Authenticated Users', gp.getuser(), 'Administrators']

def RollBack() -> None:
    try:
        with DB_PATH.open('wb') as f:
            f.write(b'')
    except OSError:
        print(
            'Cannot write to rbx-storage.db file. You probably attempted to run this twice.\n'
            'Please delete the file manually with admin permissions if you really want to do this.'
        )
        return

    cmds: list[list[str]] = [
        ['icacls', str(DB_PATH), '/inheritance:r'],
    ]

    for user in USERS_TO_REMOVE:
        cmds.append(['icacls', str(DB_PATH), '/remove', user])

    for cmd in cmds:
        subprocess.run(cmd, check=True)

def kill_roblox_processes():
    print("Killing all Roblox processes...")
    roblox_processes = [
        "RobloxPlayerBeta.exe",
        "RobloxStudioBeta.exe",
        "RobloxPlayerLauncher.exe"
    ]
    for proc in roblox_processes:
        subprocess.call(['taskkill', '/f', '/im', proc], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def check_if_rolled_back(file_path):
    print(f"Checking: {file_path}...\n")

    if not os.path.exists(file_path):
        print("File not found.")
        return

    # 1. Check if the file was wiped (Size should be 0)
    try:
        file_size = os.path.getsize(file_path)
        is_wiped = (file_size == 0)
    except PermissionError:
        print("Permission Denied: You cannot read the file properties.")
        print("This is a strong indicator that permissions were revoked (The script likely ran).")
        return

    # 2. Check for inheritance using icacls
    # If the script ran, inheritance was removed using '/inheritance:r'
    # Standard inherited permissions usually show "(I)" in the icacls output.
    try:
        result = subprocess.run(['icacls', file_path], capture_output=True, text=True)
        # We look for "(I)" which stands for "Inherited". 
        # If it is missing, inheritance was likely broken.
        has_inheritance = "(I)" in result.stdout
    except FileNotFoundError:
        print("Could not run icacls (Are you on Windows?)")
        return

    # --- RESULTS ---
    print(f"File Size: {file_size} bytes")
    print(f"Inheritance Present: {has_inheritance}")
    print("-" * 30)

    if is_wiped and not has_inheritance:
        print("YES. The RollBack script has been run on this file.")
        print("(The file is empty AND inheritance is disabled).")
    elif is_wiped and has_inheritance:
        print("UNCLEAR. The file is empty, but permissions look normal.")
        print("(The file might have just been created empty or cleared manually).")
        kill_roblox_processes()
        RollBack()
    else:
        print("NO. The file has data or normal permissions.")
        kill_roblox_processes()
        RollBack()

check_if_rolled_back(DB_PATH)

with urllib.request.urlopen("https://raw.githubusercontent.com/qrhrqiohj/Fleasion-Backend/main/requirements.txt") as response:
    requirements = response.read().decode('utf-8').splitlines()

for package in requirements:
    try:
        subprocess.check_call(["pip", "show", package])
        print(f"{package} is installed.")
    except subprocess.CalledProcessError:
        print(f"{package} is NOT installed. Installing...")
        subprocess.check_call(["pip", "install", package])
    os.system('cls')

urllib.request.urlretrieve("https://raw.githubusercontent.com/qrhrqiohj/Fleasion-Backend/refs/heads/main/run.bat", "../run.bat")
urllib.request.urlretrieve("https://raw.githubusercontent.com/qrhrqiohj/Fleasion-Backend/main/main.py", "../main.py")
urllib.request.urlretrieve("https://raw.githubusercontent.com/qrhrqiohj/Fleasion-Backend/refs/heads/main/cached_files_downloader.py", "../storage/cached_files_downloader.py")
urllib.request.urlretrieve("https://raw.githubusercontent.com/qrhrqiohj/Fleasion-Backend/refs/heads/main/autoupdate.py", "../storage/autoupdate.py")

settings_url = "https://raw.githubusercontent.com/qrhrqiohj/Fleasion-Backend/main/settings.json"
local_settings_path = "../storage/settings.json"

try:
    with urllib.request.urlopen(settings_url) as response:
        remote_settings_content = json.loads(response.read().decode('utf-8'))
    print("Successfully fetched remote settings.json.")

    if os.path.exists(local_settings_path):
        print("Local settings.json found. Checking for new entries...")
        try:
            with open(local_settings_path, 'r') as f:
                local_settings_content = json.load(f)
            
            updated_settings = local_settings_content.copy()
            for key, value in remote_settings_content.items():
                if key not in updated_settings:
                    updated_settings[key] = value
                    print(f"Added new entry to settings.json: {key}")
            
            with open(local_settings_path, 'w') as f:
                json.dump(updated_settings, f, indent=4)
            print("Local settings.json updated with new entries.")

        except json.JSONDecodeError:
            print(f"Error reading local settings.json as JSON. Overwriting with remote version.")
            urllib.request.urlretrieve(settings_url, local_settings_path)
            print("settings.json downloaded and replaced.")
        except Exception as e:
            print(f"An error occurred during local settings.json processing: {e}")
            urllib.request.urlretrieve(settings_url, local_settings_path)
            print("settings.json downloaded and replaced.")
    else:
        print("Local settings.json not found. Downloading...")
        urllib.request.urlretrieve(settings_url, local_settings_path)
        print("settings.json downloaded.")

except Exception as e:
    print(f"Failed to fetch remote settings.json or process it: {e}")
    if not os.path.exists(local_settings_path):
        print("Local settings.json does not exist and remote fetch failed. Attempting to download directly as fallback.")
        try:
            urllib.request.urlretrieve(settings_url, local_settings_path)
            print("settings.json downloaded (fallback).")
        except Exception as e_fallback:
            print(f"Fallback download of settings.json also failed: {e_fallback}")

json_url = "https://raw.githubusercontent.com/qrhrqiohj/Fleasion-Backend/main/CLOG"

def download_file(url, filename):
    try:
        urllib.request.urlretrieve(url, filename)
        print(f"Downloaded: {filename}")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")

def unzip_file(zip_file, extract_to):
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"Unzipped to: {extract_to}")
    except Exception as e:
        print(f"Error unzipping {zip_file}: {e}")

def delete_file_or_directory(path):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
            print(f"Deleted directory: {path}")
        else:
            os.remove(path)
            print(f"Deleted file: {path}")
    except Exception as e:
        print(f"Error deleting {path}: {e}")

def process_item(key, url, base_dir):
    log_exist = False
    repo_url = f"https://github.com/{url.split('/')[3]}/{url.split('/')[4]}/archive/refs/heads/main.zip"
    folder_name = os.path.join(base_dir, key)
    log_path = os.path.join(folder_name, "log.txt")
    
    if os.path.exists(log_path):
        with open(log_path, 'r') as log_file:
            log = log_file.read()
        log_exist = True
    
    os.makedirs(folder_name, exist_ok=True)
    zip_file_path = os.path.join(base_dir, f"{key}.zip")
    
    download_file(repo_url, zip_file_path)
    unzip_file(zip_file_path, base_dir)
    
    extracted_folder = os.path.join(base_dir, f"{url.split('/')[4]}-main")
    if os.path.isdir(extracted_folder):
        for item in os.listdir(extracted_folder):
            s = os.path.join(extracted_folder, item)
            d = os.path.join(folder_name, item)
            if os.path.isdir(s):
                shutil.move(s, d)
            else:
                shutil.move(s, d)
        delete_file_or_directory(extracted_folder)
    
    delete_file_or_directory(zip_file_path)
    
    if log_exist:
        with open(log_path, 'w') as file:
            file.write(log)

def process_category(category, base_dir):
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_item, key, url, base_dir)
            for key, url in category.items()
        ]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error processing item: {e}")

response = urllib.request.urlopen(json_url)
data = json.loads(response.read())

process_category(data["games"], "../assets/games")
process_category(data["community"], "../assets/community")

os.system('cls')
subprocess.run(["python", "main.py"], cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
