from flask import Flask, render_template, request, redirect, url_for
from SVTask.DataBase.UserDB import create_users_table, add_user


app = Flask(__name__)


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/registor', methods=['GET', 'POST'])
def registor():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        try:
            add_user(username, email, password)
            return redirect(url_for('main'))
        except Exception as e:
            return f"Ошибка при регистрации: {e}"
    
    return render_template('registor.html')


@app.route('/user/<username>')
def show_user_profile(username):
    # показать профиль данного пользователя
    return 'User %s' % username


if __name__ == '__main__':
    app.run(debug=True)