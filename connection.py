from minio import Minio
from minio.error import S3Error
from io import BytesIO

class Backet:

    def __init__(self, host="127.0.0.1:9000", access_key="minioadmin", secret_key="minioadmin", secure=False):#временное решение миниио работает локально в контейнере
        self.client = Minio(
            host,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
    def fileup(self, bucked_name, username, password, filename, file_size, file_data):
        object_name = f"{username}/{password}/{filename}"
        data = file_data.read()
        bytes_io = BytesIO(data)
        self.client.put_object(bucked_name, object_name, bytes_io, len(data))
        print(f"Файл {filename} загружен в бакет {bucked_name} в папку пользователя {username} размер {len(data)}")#избыточнотест

    def downloadFile(self, bucket_name, username, password, filename):
        object_name = f"{username}/{password}/{filename}"
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



