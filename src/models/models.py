from datetime import datetime
from sqlalchemy import (
    Boolean, CheckConstraint, Column, DateTime, Integer, ForeignKey, String,
    UniqueConstraint
)
from sqlalchemy.orm import relationship

from .base import Base


class Url(Base):
    '''Таблица для url.'''

    __tablename__ = 'url'

    id = Column(Integer, primary_key=True)
    original_url = Column(String, nullable=False)
    short_url = Column(String, unique=True)
    created = Column(DateTime, default=datetime.utcnow, index=True)
    connections = relationship(
        'ClientConnection',
        back_populates='url',
        lazy='selectin'
    )
    deleted = Column(Boolean, default=False)
    url_type = Column(
        String,
        default='public',
        nullable=False
    )

    user_id = Column(ForeignKey('user.id'), nullable=True)
    user = relationship('User', back_populates='urls')

    __table_args__ = (
        UniqueConstraint(
            'original_url', 'user_id', name='original_url_user_id_constraint'
        ),
        CheckConstraint(
            r'url_type in ("private", "public")',
            name='url_type_constraint',
        ),
    )


class ClientConnection(Base):
    '''Таблица для соединений.'''

    __tablename__ = 'client_connection'

    id = Column(Integer, primary_key=True)
    time = Column(DateTime, default=datetime.utcnow)
    client_info = Column(String)
    url_id = Column(ForeignKey('url.id'))
    url = relationship('Url', back_populates='connections')


class User(Base):
    '''Таблица для пользователей.'''
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String, nullable=False)
    urls = relationship('Url', back_populates='user', lazy='selectin')
