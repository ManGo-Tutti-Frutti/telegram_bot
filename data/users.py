import sqlalchemy
from data.db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True)
    completed_colours = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    failed_colours = sqlalchemy.Column(sqlalchemy.Integer, default=0)
