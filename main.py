from flask import Flask, render_template,request

app = Flask(__name__)

@app.route('/', methods = ['GET','POST'])
def start():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        print(name)
        print(password)
        return render_template('index.html', name = name, password = password)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)