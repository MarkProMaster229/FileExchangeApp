from flask import Flask, render_template, request, redirect, url_for, session ,send_file
from UserRegistration import UserRegistration
from connection import Backet


store = UserRegistration()


app = Flask(__name__)
app.secret_key = 'секретный_ключ'


@app.route('/', methods=['GET', 'POST'])
def start():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')


        session['name'] = name
        session['password'] = password

        userdata = store.get_user(name)

        if userdata:
            if userdata.get("password") == password:
                print("Пользователь уже существует, пароль совпадает — вход разрешен")
                return redirect(url_for('file'))
            else:
                print("Пользователь существует, но пароль не совпадает")
                return render_template('index.html', error="Пользователь или пароль не верны")
        else:
            print("Пользователь не найден — перенаправляем на регистрацию")
            return render_template('index.html', error="Пользователь или пароль не верны")


        return render_template('index.html', name=name, password=password)

    return render_template('index.html')

@app.route('/registration', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')

        if not name or not password:
            return render_template('registration.html', error="Пожалуйста, заполните все поля")

        if not store.get_user(name):
            success = store.add_user(name, password)
            if success:
                print("Новый пользователь зарегистрирован")
                session['name'] = name
                session['password'] = password
                return redirect(url_for('file'))
            else:
                return render_template('registration.html', error="Ошибка регистрации")
        else:
            return render_template('registration.html', error="Пользователь уже существует")

    return render_template('registration.html')

baket = Backet()
baketName = "mybucket"
PubluckBaket = "publicbaket"
@app.route('/filerecipient', methods=['GET', 'POST'])
def file():
    global baket
    global baketName
    global PubluckBaket

    name = session.get('name')
    password = session.get('password')
    file = None
    show_alert = False

    if request.method == 'POST':
        if 'public_upload' in request.form:
            file = request.files.get('public_file')
            if not file or file.filename == '':
                return render_template('filerecipient.html', files=[],
                                       error="Пожалуйста, выберите файл для загрузки в публичные")

            baket.generalFiles(            bucked_name=PubluckBaket,
            username=name,
            filename=file.filename,
            file_data=file.stream,
            file_size=file.content_length)

        else:

            file = request.files.get('file')
            if not file or file.filename == '':
                return render_template('filerecipient.html', files=[], error="Пожалуйста, выберите файл")
            result = baket.fileup(
                bucked_name=baketName,
                username=name,
                password=password,
                filename=file.filename,
                file_data=file.stream,
                file_size=file.content_length
            )

        print(f"name: {name}, password: {password}, file: {file.filename if file else 'нет файла'}")#избыточнотест

    public_info = baket.scannerFiles(PubluckBaket, prefix=f"{name}/")
    publicFiles = [
        {
            'name': f['name'][len(name) + 1:],
            'size': round(f['size'] / (1024 * 1024), 1)
        }
        for f in public_info
    ]

    people = f"{name}/{password}/"
    info = baket.scannerFiles(baketName, prefix=people)
    if not info:
        files = []
    else:
        prefix_length = len(people)
        files = [
            {
                'name': f['name'][prefix_length:],
                'size': round(f['size'] / (1024 * 1024), 1)
            }
            for f in info if f['name'].startswith(people)
        ]
    polise = baket.police(baketName,name, password)

    return render_template('filerecipient.html', files=files, publicFiles=publicFiles, polise=polise, show_alert=show_alert)

@app.route('/download/<path:filename>')
def download_file(filename):
    global baket
    global baketName
    name = session.get('name')
    password = session.get('password')

    if not name or not password:
        return "Пользователь не авторизован", 401

    file_data = baket.downloadFile(baketName, name, password, filename)
    file_data.seek(0)
    return send_file(
        file_data,
        download_name=filename,
        as_attachment=True
    )
@app.route('/download/pub/<path:filename>')
def dowload_public(filename):
    global baket
    global PubluckBaket
    name = session.get('name')
    publickRealise = baket.downloadFilePublic(PubluckBaket,name,filename)
    publickRealise.seek(0)
    return send_file(publickRealise, download_name=filename, as_attachment=True)


@app.route('/delete/<path:filename>', methods=['POST'])
def delete_file(filename):
    global baket
    global baketName

    name = session.get('name')
    password = session.get('password')

    if not name or not password:
        return "Не авторизован", 401

    success = baket.deletedFiles(baketName, name, password, filename)
    if success:
        print(f"Файл {filename} удалён")
    else:
        print(f"Не удалось удалить файл {filename}")

    return redirect(url_for('file'))


if __name__ == '__main__':
    baket.start_cleaning_thread(baketName)
    app.run(debug=True)

