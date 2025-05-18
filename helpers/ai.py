from models import Conversation, Message, User, Sender, Bot
from schemas import ConversationCreateRequest, MessageRequest, MessageResponse
import uuid
import datetime
from pypinyin import lazy_pinyin, pinyin
from gemini import generate_response

BASIC_PROMPT = '''You are a conversational Mandarin-speaking chatbot.
    Respond only in Traditional Chinese characters,
    respond like you are texting a friend or acquaintance with a focus on sounding natural,
    use emojis very sparingly,
    and limit your response to about 30 characters or less.\n
'''

DIFFICULTY_PROMPTS = {
    'easy': "The user is at an easy difficulty so respond with the vocabulary that a 5th grader may understand.\n",
    'medium': "The user is at a medium difficulty so respond with the vocabulary that a 9th grader may understand.\n",
    'hard': "The user is at a hard difficulty so respond with the vocabulary that an undergraduate may understand.\n",
    'native': "The user is at a native difficulty so respond with the vocabulary that a native speaker may understand.\n",
}


def get_ai_response(recent_msgs: list[dict], bot: Bot, user: User, user_content: str) -> str:
    prompt = BASIC_PROMPT + bot.character_notes + DIFFICULTY_PROMPTS[user.difficulty]
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

    if request.initial_message:
        user_msg = Message(
            id=str(uuid.uuid4()),
            conversation_id=new_conv.id,
            sender=Sender.USER,
            content=request.initial_message,
            pinyin=lazy_pinyin(request.initial_message),
            created_at=datetime.datetime.utcnow()
        )
        db.add(user_msg)

        ai_content = generate_response(f"{BASIC_PROMPT}User: {request.initial_message}\nAI:")
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
    
    prompt = BASIC_PROMPT
    for msg in recent_msgs:
        role = "user" if msg.sender == Sender.USER else "ai"
        prompt += f"{role}: {msg.content}\n"

    prompt += f"User: {request.content}\nAI:"

    ai_response_text = generate_response(prompt)

    user_msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=conv.id,
        sender=Sender.USER,
        content=request.content,
        pinyin=pinyin(request.content),
        created_at=datetime.datetime.utcnow()
    )

    pinyin_conversion = pinyin(ai_response_text, strict=False)
    pinyin_list = [item for clause in pinyin_conversion for item in clause]
    ai_msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=conv.id,
        sender=Sender.AI,
        content=ai_response_text,
        pinyin=pinyin_list,
        created_at=datetime.datetime.utcnow()
    )

    db.add(user_msg)
    db.add(ai_msg)
    db.commit()

    return MessageResponse(content=ai_response_text, pinyin=ai_msg.pinyin)
