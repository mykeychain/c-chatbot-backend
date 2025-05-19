from sqlalchemy import Column, String, DateTime, Enum, Text, JSON, ForeignKey, desc
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List
import enum
import uuid, datetime

from database import Base

class Difficulty(str, enum.Enum): 
    EASY = 'easy'
    MED = 'medium'
    HARD = 'hard'
    NATIVE = 'native'

class Sender(str, enum.Enum): 
    USER = 'user'
    AI = 'ai'

class User(Base):
    __tablename__ = 'users'
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now(datetime.timezone.utc))
    conversations: Mapped[List['Conversation']] = relationship('Conversation', back_populates='user')
    difficulty: Mapped[Difficulty] = mapped_column(String(30), default=Difficulty.MED, nullable=False)

class Bot(Base): 
    __tablename__ = 'bots'
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now(datetime.timezone.utc))
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    character_notes: Mapped[str] = mapped_column(Text)
    conversations: Mapped[List['Conversation']] = relationship('Conversation', back_populates='bot')

class Conversation(Base):
    __tablename__ = 'conversations'
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship('User', back_populates='conversations')
    bot_id: Mapped[str] = mapped_column(ForeignKey('bots.id'))
    bot: Mapped['Bot'] = relationship('Bot', back_populates='conversations')
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now(datetime.timezone.utc))
    messages: Mapped[List['Message']] = relationship('Message', back_populates='conversation', order_by=lambda: Message.created_at)
    last_message: Mapped["Message"] = relationship(
        viewonly=True,
        uselist=False,
        primaryjoin=lambda: Conversation.id == Message.conversation_id,
        order_by=lambda: desc(Message.created_at)
    )

class Message(Base):
    __tablename__ = 'messages'
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id: Mapped[str] = mapped_column(ForeignKey('conversations.id'))
    conversation: Mapped['Conversation'] = relationship('Conversation', back_populates='messages')
    sender: Mapped[Sender] = mapped_column(String(30), default=Sender.USER, nullable=False)
    content: Mapped[str] = mapped_column(Text)
    pinyin: Mapped[list[any]] = mapped_column(JSON)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now(datetime.timezone.utc))
