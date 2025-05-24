from models import Conversation, Message, Bot
import uuid
import datetime
from sqlalchemy import not_
from sqlalchemy.orm import Session

def create_conversation(db, user_id: str, bot_id: str):
    conv = Conversation(
        id=str(uuid.uuid4()),
        user_id=user_id,
        bot_id=bot_id,
        created_at=datetime.datetime.utcnow()
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv

def create_message(db, conversation_id: str, sender: str, content: str, pinyin: list[str]):
    msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        sender=sender,
        content=content,
        pinyin=pinyin,
        created_at=datetime.datetime.utcnow()
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def get_conversation(db, conversation_id: str):
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()

def list_user_conversations(db, user_id: str):
    return db.query(Conversation).filter(Conversation.user_id == user_id).order_by(Conversation.created_at.desc()).all()

def delete_conversation(db, conversation_id: str):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conv:
        db.query(Message).filter(Message.conversation_id == conversation_id).delete()
        db.delete(conv)
        db.commit()
        return True
    return False

def get_conversation_messages(db, conversation_id: str):
    return db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()

def get_available_bots(db: Session, user_id: str):
    # Get all bots that don't have a conversation with this user
    existing_bot_ids = db.query(Conversation.bot_id).filter(Conversation.user_id == user_id).subquery()
    available_bots = db.query(Bot).filter(not_(Bot.id.in_(existing_bot_ids))).all()
    return available_bots
