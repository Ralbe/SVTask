from flask import Flask, render_template
import psycopg2


app = Flask(__name__)


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/registor', methods=['GET', 'POST'])
def registor():
    return render_template('registor.html')


@app.route('/user/<username>')
def show_user_profile(username):
    # показать профиль данного пользователя
    return 'User %s' % username


if __name__ == '__main__':
    app.run(debug=True)