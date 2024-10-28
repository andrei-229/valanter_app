import requests
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN_GIT')
repo_owner = 'andrei-229'  # Имя владельца репозитория
repo_name = 'valanter_app'   # Имя репозитория

# Получите информацию о последнем релизе
url = f'https://api.github.com/repos/andrei-229/valanter_app/releases/latest'
headers = {'Authorization': f'Bearer {TOKEN}'}
response = requests.get(url, headers=headers)

release_data = response.json()
download_url = release_data['body'].replace('\r\n', '')  # Получите URL для загрузки файла asset_name
print(download_url)
download_folder = os.getcwd()  # Получите путь к текущей папке
version_release = release_data['tag_name']  # Получите версию релиза
asset_response = requests.get(download_url, headers=headers, stream=True)  # Загрузите файл asset_name
if asset_response.status_code == 200:
    file_path = os.path.join(download_folder, 'asset_name.zip')  # Сохраните файл asset_name в текущей папке
    with open(file_path, 'wb') as f:
        for chunk in asset_response.iter_content(chunk_size=8192):  
            f.write(chunk)
    print(f"Файл asset_name загружен.")
else:
    print(f"Ошибка при загрузке asset_name: {asset_response.status_code}")

print(version_release)



