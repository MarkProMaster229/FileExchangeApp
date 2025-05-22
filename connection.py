from minio import Minio
from minio.error import S3Error


class Backet:
    def __init__(self, host="127.0.0.1:9000", access_key="minioadmin", secret_key="minioadmin", secure=False):
        self.client = Minio(
            host,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
    def fileup(self,bucked_name,username,password,filename, file_size, file_data):
        objec = f"{username}/{password}/{filename}"
        self.client.put_object(bucked_name, objec, file_data, file_size)
        print(f"Файл {filename} загружен в бакет {bucked_name} в папку пользователя {username}")