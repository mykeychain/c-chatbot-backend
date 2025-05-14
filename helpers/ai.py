from models import Conversation, Message, User
from schemas import ConversationCreateRequest, MessageRequest, MessageResponse
import uuid
import datetime
from pypinyin import lazy_pinyin, pinyin
from gemini import generate_response

def get_ai_response(recent_msgs: list[dict], user_content: str) -> str:
    prompt = "你是一個中文老師，使用繁體中文回答。Limit your response to about 140 characters.\n"
    for msg in recent_msgs:
        role = "User" if msg["sender"] == "user" else "AI"
        prompt += f"{role}: {msg['content']}\n"

    prompt += f"User: {user_content}\nAI:"
    return generate_response(prompt)


def create_conversation(db, request: ConversationCreateRequest):
    new_conv = Conversation(
        id=str(uuid.uuid4()),
        user_id=request.user_id,
        created_at=datetime.datetime.utcnow()
    )
    db.add(new_conv)
    db.commit()

    # Handle optional initial user message
    if request.initial_message:
        user_msg = Message(
            id=str(uuid.uuid4()),
            conversation_id=new_conv.id,
            sender='user',
            content=request.initial_message,
            pinyin=lazy_pinyin(request.initial_message),
            created_at=datetime.datetime.utcnow()
        )
        db.add(user_msg)

        # Initial AI response
        ai_content = generate_response(f"你是一個中文老師，使用繁體中文回答。\nUser: {request.initial_message}\nAI:")
        ai_msg = Message(
            id=str(uuid.uuid4()),
            conversation_id=new_conv.id,
            sender='ai',
            content=ai_content,
            pinyin=lazy_pinyin(ai_content),
            created_at=datetime.datetime.utcnow()
        )
        db.add(ai_msg)
        db.commit()

    return new_conv

def process_message(db, request: MessageRequest):
    conv = db.query(Conversation).filter_by(id=request.conversation_id).first()
    if not conv:
        raise ValueError("Conversation not found")

    # Get last 20 messages for context
    recent_msgs = db.query(Message).filter_by(conversation_id=conv.id)\
                    .order_by(Message.created_at.asc()).limit(20).all()
    
    prompt = "你是一個中文老師，使用繁體中文回答。\n"
    for msg in recent_msgs:
        role = "User" if msg.sender == "user" else "AI"
        prompt += f"{role}: {msg.content}\n"

    prompt += f"User: {request.content}\nAI:"

    # Generate AI response using Gemini
    ai_response_text = generate_response(prompt)

    # Create and store the user's message
    user_msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=conv.id,
        sender='user',
        content=request.content,
        pinyin=pinyin(request.content),
        created_at=datetime.datetime.utcnow()
    )

    # Create and store AI's response message
    pinyin_conversion = pinyin(ai_response_text, strict=False)
    pinyin_list = [item for clause in pinyin_conversion for item in clause]
    ai_msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=conv.id,
        sender='ai',
        content=ai_response_text,
        pinyin=pinyin_list,
        created_at=datetime.datetime.utcnow()
    )

    db.add(user_msg)
    db.add(ai_msg)
    db.commit()

    return MessageResponse(content=ai_response_text, pinyin=ai_msg.pinyin)
