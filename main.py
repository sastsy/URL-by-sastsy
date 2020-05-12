from flask import Flask, render_template, request
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

from data import db_session
from data.users import User
from data.link import Link


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():  # Главная функция
    db_session.global_init("db/blogs.sqlite")
    app.run(debug=True)


login_manager = LoginManager()
login_manager.init_app(app)


@app.route("/")  # Функция для главной страницы
def index():
    return render_template("index.html")


@app.route('/<short_url>')  # Функция для отслеживания кол-ва визитов и переадресации
def redirect_to_url(short_url):
    session = db_session.create_session()
    link = session.query(Link).filter_by(short_url=short_url).first()

    link.visits = link.visits + 1
    session.commit()

    return redirect(link.original_url)


@app.route('/create_url')  # Функция для создания нового URL
@login_required
def create_url():
    return render_template('create_url.html', title='Создать новое URL', head='Создать URL')


@app.route('/add_link', methods=['POST'])
@login_required
def add_link():  # Функция обработки ссылки
    session = db_session.create_session()
    original_url = request.form['original_url']
    user_id = current_user.id  # Запоминаем id текущего пользователя, чтобы передать его ссылке

    link = Link(original_url=original_url, user_id=user_id)
    session.add(link)
    session.commit()

    return render_template('link_added.html', new_link=link.short_url, original_url=link.original_url, head='Новое URL',
                           title='Новое URL')


@app.route('/stats')
@login_required
def stats():
    session = db_session.create_session()
    links = session.query(Link).filter(current_user.id == Link.user_id)  # Оставляем только ссылки текущего пользователя

    return render_template('stats.html', links=links, title='Архив', head='Архив')


class RegisterForm(FlaskForm):  # Форма регистрации
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Войти')


@app.route('/register', methods=['GET', 'POST'])  # Функция регистрации
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        if session.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким именем уже есть")
        user = User(name=form.name.data, email=form.email.data, about=form.about.data)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()

        return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form, head='Регистрация')


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()

    return session.query(User).get(user_id)


class LoginForm(FlaskForm):  # Форма авторизации
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/login', methods=['GET', 'POST'])  # Форма авторизации
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)

            return redirect("/")

        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)

    return render_template('login.html', title='Авторизация', form=form, head='Вход')


@app.route('/logout')  # Функция выхода из приложения
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    main()