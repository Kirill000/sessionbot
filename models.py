from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, MetaData
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)  # Уникальный идентификатор
    user_created = Column(DateTime, default=datetime.now)  # Дата и время создания
    subjects_allowed_to_read = Column(String, nullable=False, default='[]')
    is_banned = Column(Boolean, nullable=False, default=False)
    is_admin = Column(Boolean, nullable=False, default=False)

class SAU(Base):
    __tablename__ = 'sau'

    id = Column(Integer, primary_key=True, autoincrement=True)  # Уникальный идентификатор
    title = Column(String, nullable=False)
    answer_text = Column(String, nullable=True, default=None)
    answer_imgs = Column(String, nullable=True, default='[]')
    author = Column(Integer, nullable=False)
    is_empty = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)

class Schemotech(Base):
    __tablename__ = 'schemotech'

    id = Column(Integer, primary_key=True, autoincrement=True)  # Уникальный идентификатор
    title = Column(String, nullable=False)
    answer_text = Column(String, nullable=True)
    answer_imgs = Column(String, nullable=True, default='[]')
    author = Column(Integer, nullable=False)
    is_empty = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)