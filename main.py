from flask import Flask, render_template, request, redirect, url_for, session ,send_file
from UserRegistration import UserRegistration
from connection import Backet

app = Flask(__name__)
store = UserRegistration()
from flask import Flask, render_template, request, redirect, url_for, session

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
        else:
            store.add_user(name, password)
            print("Пользователь добавлен")

        return render_template('index.html', name=name, password=password)

    return render_template('index.html')


@app.route('/filerecipient', methods=['GET', 'POST'])
def file():
    baket = Backet()
    baketName = "mybucket"

    file = None

    if request.method == 'POST':
        file = request.files.get('file')

        name = session.get('name')
        password = session.get('password')

        print(f"name: {name}, password: {password}, file: {file.filename if file else 'нет файла'}")

        baket.fileup(
            bucked_name=baketName,
            username=name,
            password=password,
            filename=file.filename,
            file_data=file.stream,
            file_size=file.content_length
        )


        name_file = file.filename
        fileget = baket.downloadFile(baketName, name, password, file.filename)
        fileget.seek(0)
        data = fileget.read()
        print(f"Размер данных для отдачи: {len(data)}")
        fileget.seek(0)

        return send_file(
            fileget,
            download_name=name_file,
            as_attachment=True
        )

    return render_template('filerecipient.html')


if __name__ == '__main__':
    app.run(debug=True)
