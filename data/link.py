from datetime import datetime
import string
from random import choices
import sqlalchemy
from data.db_session import SqlAlchemyBase


class Link(SqlAlchemyBase):
    __tablename__ = 'link'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    original_url = sqlalchemy.Column(sqlalchemy.String(512))  # Исходный URL
    short_url = sqlalchemy.Column(sqlalchemy.String(3), unique=True)  # Новый URL
    visits = sqlalchemy.Column(sqlalchemy.Integer, default=0)  # Количество посещений
    date_created = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.short_url = self.generate_short_link()

    def generate_short_link(self):  # Генерация нового URL
        characters = string.digits + string.ascii_letters
        short_url = ''.join(choices(characters, k=3))  # Используем три знака

        return short_url
