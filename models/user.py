from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BigInteger, String, Column

from config import database

class User(database.Model):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
