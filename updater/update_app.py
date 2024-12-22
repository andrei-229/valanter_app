import os
import sys
import subprocess
from PyQt5 import uic

from PyQt5.QtWidgets import QApplication

from PyQt5.QtWidgets import QMainWindow

from google.oauth2 import service_account
from googleapiclient.discovery import build
import io
from googleapiclient.http import MediaIoBaseDownload

class MainWindow(QMainWindow):  # главное окно 
    def __init__(self, *args):
        global d
        super().__init__()
        uic.loadUi('update_successful.ui', self)
        os.chdir(d)
        SERVICE_ACCOUNT_FILE = 'kay_new.json'
        os.remove('BD.exe')

        # Создайте учетные данные
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=['https://www.googleapis.com/auth/drive.readonly'],
        )

        # Создайте сервис
        service = build('drive', 'v3', credentials=credentials)

        # ID папки, из которой хотите скачать файлы
        folder_id = '1z7SInUAcRrVWr8Ltx27iyucqMukh-xNn'

        # Получите список файлов в папке
        results = service.files().list(
            q=f"'{folder_id}' in parents",
            pageSize=10,
            fields="nextPageToken, files(id, name)"
        ).execute()
        items = results.get('files', [])
        # print(items)
        if not items:
            print('Нет файлов в этой папке.')
        else:
            for item in items:
                if item["name"] == 'BD.exe':
                    print(f'Скачиваем файл: {item["name"]}')
                    request = service.files().get_media(fileId=item['id'])
                    fh = io.BytesIO()
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print(f'Загружено {int(status.progress() * 100)}%.')
                    
                    # Сохраните файл
                    with open(item['name'], 'wb') as f:
                        f.write(fh.getbuffer())
        self.update_succeddful_but.clicked.connect(self.start_app)

    def start_app(self):
        global d
        os.chdir(d)
        subprocess.Popen('BD.exe')
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    d = str(os.getcwd()).replace('\\', '/')  # Запоминаем где были
    os.chdir(getattr(sys, '_MEIPASS', os.getcwd()))  # Сменяем рабочудеррикторию, чтобы подгрузить окошки и .env
    d2 = str(os.getcwd()).replace('\\', '/')  # Запоминаем где были
    main = MainWindow()
    main.show()
    sys.exit(app.exec())