import urllib.request
import subprocess
import os

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


urllib.request.urlretrieve("https://raw.githubusercontent.com/qrhrqiohj/Fleasion-Backend/main/main.py", "main.py")
urllib.request.urlretrieve("https://raw.githubusercontent.com/qrhrqiohj/Fleasion-Backend/main/settings.json", "storage\settings.json")
subprocess.run(["python", "main.py"])
