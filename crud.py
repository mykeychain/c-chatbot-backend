from models import Conversation, Message, Bot, Translation
import uuid
import datetime
from sqlalchemy import not_
from sqlalchemy.orm import Session
from helpers.text_processing import make_digest

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

def create_message(db, conversation_id: str, sender: str, content: str, pinyin: list[str], translation: str = ''):
    msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        sender=sender,
        content=content,
        pinyin=pinyin,
        translation=translation,
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

def get_translation(db, key: str): 
    hash = make_digest(key)
    print(f"key: {key}, hash: {hash}")
    return db.query(Translation).filter(Translation.key == hash).first()

def create_translation(db, key: str, value: str): 
    hash = make_digest(key)
    print(f"creating translation:key: {key}, hash: {hash}")
    translation = Translation(key=hash, value=value)
    db.add(translation)
    db.commit()
    db.refresh(translation)
    return translation
