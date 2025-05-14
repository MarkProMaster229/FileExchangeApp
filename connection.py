from minio import Minio

# Подключаемся
client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False  # потому что http, не https
)

# Проверим, есть ли бакет (и создадим, если нужно)
bucket_name = "mybucket"
if not client.bucket_exists(bucket_name):
    client.make_bucket(bucket_name)

# Загружаем файл
client.fput_object(
    "mybucket",
    "images/cat.jpg",
    "/home/chelovek/Рабочий стол/deleteMe/Снимок экрана_20250501_153723.png"
)
# выгружаем файл
client.fget_object(
    "mybucket",
    "images/cat.jpg",
    "/home/chelovek/Рабочий стол/моя работа описание и скриншоты/cat.jpg "
)


print("Загрузка завершена!")
