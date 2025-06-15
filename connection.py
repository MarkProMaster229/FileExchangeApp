import threading
import uuid
from minio import Minio
from minio.error import S3Error
from io import BytesIO
import time
import schedule
import time
from datetime import datetime, timedelta
# def __init__(self, host="minio:9000", access_key="minioadmin", secret_key="minioadmin", secure=False):
# self.client = Minio(
# host,
# access_key=access_key,
# secret_key=secret_key,
# secure=secure
# )

class Backet:

    def __init__(self, host="127.0.0.1:9000", access_key="minioadmin", secret_key="minioadmin", secure=False):#временное решение миниио работает локально в контейнере
        #в докер компасе есть часть для работы с мимниио предоставлю - выше там предусмотрена локально работа меж контейнерами
        self.client = Minio(
            host,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

    def fileup(self, bucked_name, username, password, filename, file_size, file_data):
        object_name = f"{username}/{password}/{filename}"
        if file_size is None or file_size == 0:
            pos = file_data.tell()
            file_data.seek(0, 2)  # в конец
            file_size = file_data.tell()
            file_data.seek(pos)
        file_data.seek(0)
        print(f"Загружаем файл {filename} размером {file_size} байт")
        current_size = self.police(bucked_name, username, password)  # размер уже загруженных файлов
        limit = 10_737_418_240  # 10 гигабайт в байтах
        if current_size + file_size > limit:
            print("Превышен общий лимит на пользователя")
            return 1
        self.client.put_object(bucked_name, object_name, file_data, file_size)
        print(f"Файл {filename} загружен в бакет {bucked_name} в папку пользователя {username} размер {file_size}")
        return 0

    def downloadFile(self, bucket_name, username, password, filename):
        object_name = f"{username}/{password}/{filename}"#наверно, лучше бы быть ему глобальным
        response = self.client.get_object(bucket_name, object_name)
        file_data = BytesIO(response.read())
        response.close()
        response.release_conn()
        file_data.seek(0)
        return file_data

    def scannerFiles(self, bucket_name, prefix=None):
        files = []
        try:
            objects = self.client.list_objects(bucket_name, prefix=prefix, recursive=True)
            for obj in objects:
                files.append({
                    "name": obj.object_name,
                    "size": obj.size
                })
        except S3Error as e:
            print(f"Ошибка при получении списка объектов: {e}")
        return files
    #после последнего обновления, мне стало страшно, раньше пользователя
    #физчески держало кол-во озу сервера, теперь юзер может загрузить очень большие данные
    #для этого нужно разработать меры ограничения 10гигабайт я думаю как верхний лимит на пользователя
    def police(self, bucket_name, username, password):
        size = 0
        breakPointFile = 0
        folder_name = f"{username}/{password}/"
        rider = self.client.list_objects(bucket_name,prefix=folder_name,recursive=True)
        for obj in rider:
            size += obj.size

        if size > 10_737_418_240:
            breakPointFile = 1
            print("отладка-предел-стоп")

        return breakPointFile

    def deletedFiles(self, bucket_name, username, password, filename):
        object_name = f"{username}/{password}/{filename}"
        try:
            self.client.remove_object(bucket_name, object_name)
            print(f"Файл {object_name} удалён.")
            return True
        except S3Error as e:
            print(f"Ошибка при удалении файла: {e}")
            return False

    def deletedAll(self, bucket_name):
        print(f"[{datetime.now()}]полное удаление всех файлов в бакете {bucket_name}")
        objectDell = self.client.list_objects(bucket_name, recursive=True)
        for obj in objectDell:
            self.client.remove_object(bucket_name, obj.object_name)
            print(f"Удалён файл {obj.object_name}")
        print("Полное удаление завершено.")

    def clean(self, bucket_name):
        schedule.every().day.at("01:00").do(self.deletedAll, bucket_name=bucket_name)
        print(f"[{datetime.now()}] Планировщик запущен. Удаление каждый день в 01:00.")
        while True:
            schedule.run_pending()
            time.sleep(30)

    def start_cleaning_thread(self, bucket_name):
        thread = threading.Thread(target=self.clean, args=(bucket_name,), daemon=True)
        thread.start()

    #было принято решение для того что бы пользователь смог делится своими файлами
    #решение было принято по причине комфорта пользователя, у пользователя будут как личные так и
    #общевственные файлы в разных бакетах соответственно

    def generalFiles(self, bucked_name, username, filename, file_size, file_data, token):
        object_name = f"{username}/{token}/{filename}"
        if file_size is None or file_size == 0:
            pos = file_data.tell()
            file_data.seek(0, 2)  # в конец
            file_size = file_data.tell()
            file_data.seek(pos)
        file_data.seek(0)
        print(f"Загружаем файл {filename} размером {file_size} байт")
        self.client.put_object(bucked_name, object_name, file_data, file_size)
        print(f"Файл {filename} загружен в бакет {bucked_name} в папку пользователя {username} размер {file_size}")
        return 0

    def downloadFilePublic(self, bucket_name, username, filename,token):
        object_name = f"{username}/{token}/{filename}"
        response = self.client.get_object(bucket_name, object_name)
        file_data = BytesIO(response.read())
        response.close()
        response.release_conn()
        file_data.seek(0)
        return file_data

    def generate_token(self):
        return uuid.uuid4().hex