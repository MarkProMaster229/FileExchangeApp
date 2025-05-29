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
        else:
            store.add_user(name, password)
            print("Пользователь добавлен")

        return render_template('index.html', name=name, password=password)

    return render_template('index.html')

baket = Backet()
baketName = "mybucket"

@app.route('/filerecipient', methods=['GET', 'POST'])
def file():
    global baket
    global baketName

    name = session.get('name')
    password = session.get('password')
    file = None

    if request.method == 'POST':
        file = request.files.get('file')



        print(f"name: {name}, password: {password}, file: {file.filename if file else 'нет файла'}")#избыточнотест

        baket.fileup(
            bucked_name=baketName,
            username=name,
            password=password,
            filename=file.filename,
            file_data=file.stream,
            file_size=file.content_length
        )


        name_file = file.filename


    people = f"{name}/{password}/"

    info = baket.scannerFiles(baketName, prefix=people)
    size = info[0]['size']#плохое значение в байтах(
    megabytes = size / (1024 * 1024)#хорошее значениев мегабайтах)
    print(round(megabytes, 1))#избыточнотест
    print(size)#избыточнотест
    print("INFO:", info)#избыточнотест

    prefix_length = len(people)
    files = [
        {
            'name': f['name'][prefix_length:],
            'size': round(f['size'] / (1024 * 1024), 1)
        }
        for f in info if f['name'].startswith(people)
    ]

    return render_template('filerecipient.html', files=files)

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


if __name__ == '__main__':
    app.run(debug=True)

