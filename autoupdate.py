import urllib.request
import subprocess
import os
import zipfile
import json
import shutil

with urllib.request.urlopen("https://raw.githubusercontent.com/qrhrqiohj/Fleasion-Backend/main/requirements.txt") as response:
    requirements = response.read().decode('utf-8').splitlines()

for package in requirements:
    try:
        subprocess.check_call([ "pip", "show", package ])
        print(f"{package} is installed.")
    except subprocess.CalledProcessError:
        print(f"{package} is NOT installed. Installing...")
        subprocess.check_call([ "pip", "install", package ])
    os.system('cls')

urllib.request.urlretrieve("https://raw.githubusercontent.com/qrhrqiohj/Fleasion-Backend/refs/heads/main/run.bat", "../run.bat")
urllib.request.urlretrieve("https://raw.githubusercontent.com/qrhrqiohj/Fleasion-Backend/main/main.py", "../main.py")
urllib.request.urlretrieve("https://raw.githubusercontent.com/qrhrqiohj/Fleasion-Backend/main/settings.json", "../storage/settings.json")
urllib.request.urlretrieve("https://raw.githubusercontent.com/qrhrqiohj/Fleasion-Backend/refs/heads/main/autoupdate.py", "../storage/autoupdate.py")

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

response = urllib.request.urlopen(json_url)
data = json.loads(response.read())
def process_category(category, base_dir):
    for key, url in category.items():
        repo_url = f"https://github.com/{url.split('/')[3]}/{url.split('/')[4]}/archive/refs/heads/main.zip"
        folder_name = os.path.join(base_dir, key)
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

process_category(data["games"], "../assets/games")
process_category(data["community"], "../assets/community")

os.system('cls')
subprocess.run(["python", "main.py"], cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
