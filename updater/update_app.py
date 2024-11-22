import requests
import os
import zipfile
from dotenv import load_dotenv
import time
import sys
import subprocess

d = str(os.getcwd()).replace('\\', '/')  # Запоминаем где были
os.chdir(getattr(sys, '_MEIPASS', os.getcwd()))  # Сменяем рабочудеррикторию, чтобы подгрузить окошки и .env
# ls = os.listdir()
load_dotenv()
TOKEN = os.getenv('TOKEN_GIT')
repo_owner = os.getenv('REPO_OWNER')  # Имя владельца репозитория
repo_name = os.getenv('REPO_NAME')   # Имя репозитория
url = os.getenv('GIT_LINK')
d2 = str(os.getcwd()).replace('\\', '/')  # Запоминаем где были
os.chdir(d) #
# load_dotenv()
# TOKEN = os.getenv('TOKEN_GIT')
# repo_owner = os.getenv('REPO_OWNER')  # Имя владельца репозитория
# repo_name = os.getenv('REPO_NAME')   # Имя репозитория

# # # Получите информацию о последнем релизе
headers = {'Authorization': f'Bearer {TOKEN}'}

# def download_update():
response = requests.get(url, headers=headers)
release_data = response.json()
download_url = release_data['body'].replace('\r\n', '')  # Получите URL для загрузки файла asset_name
# print(download_url)
download_folder = os.getcwd()  # Получите путь к текущей папке
asset_response = requests.get(download_url, headers=headers, stream=True)  # Загрузите файл asset_name
if asset_response.status_code == 200:
    file_path = os.path.join(download_folder, 'u.zip')  # Сохраните файл asset_name в текущей папке
    with open(file_path, 'wb') as f:
        for chunk in asset_response.iter_content(chunk_size=8192):  
            f.write(chunk)
    print(f"Файл asset_name загружен.")
else:
    print(f"Ошибка при загрузке asset_name: {asset_response.status_code}")
# os.remove('BD.exe')
with zipfile.ZipFile('u.zip', 'r') as zip_ref:
    zip_ref.extractall()
# time.sleep(3)
os.remove('u.zip')

# path = getattr(sys, '_MEIPASS', os.getcwd())
# d = str(os.getcwd()).replace('\\', '/').replace('')
# os.chdir(path)
# subprocess.Popen('markov.exe')