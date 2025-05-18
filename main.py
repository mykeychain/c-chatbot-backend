# main.py

from fastapi import FastAPI, Depends, HTTPException
from schemas import (
    ConversationCreateRequest,
    ConversationCreateResponse,
    ConversationDeleteResponse,
    ConversationSchema,
    MessageRequest,
    MessageResponse,
)
from crud import (
    create_conversation,
    create_message,
    delete_conversation,
    get_conversation,
    list_user_conversations,
)
from dependencies import get_db
from helpers.ai import get_ai_response
from helpers.pinyin import get_pinyin_list
from sqlalchemy.orm import Session
from typing import List

app = FastAPI()

@app.post("/api/conversations", response_model=ConversationCreateResponse)
def api_create_conversation(request: ConversationCreateRequest, db: Session = Depends(get_db)):
    conv = create_conversation(db, request.user_id, request.bot_id)

    if request.initial_message:
        create_message(
            db=db,
            conversation_id=conv.id,
            sender='user',
            content=request.initial_message,
            pinyin=get_pinyin_list(request.initial_message)
        )

        ai_content = get_ai_response([], conv.bot, request.initial_message)
        create_message(
            db=db,
            conversation_id=conv.id,
            sender='ai',
            content=ai_content,
            pinyin=get_pinyin_list(ai_content)
        )

    return ConversationCreateResponse(conversation_id=conv.id)

@app.get("/api/conversations/{conversation_id}", response_model=ConversationSchema)
def api_get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conv = get_conversation(db, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv

@app.get("/api/users/{user_id}/conversations", response_model=List[ConversationSchema])
def api_list_conversations(user_id: str, db: Session = Depends(get_db)):
    return list_user_conversations(db, user_id)

@app.delete("/api/conversations/{conversation_id}", response_model=ConversationDeleteResponse)
def api_delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    success = delete_conversation(db, conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ConversationDeleteResponse(success=True)

@app.post("/api/message", response_model=MessageResponse)
def api_send_message(request: MessageRequest, db: Session = Depends(get_db)):
    conv = get_conversation(db, request.conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    recent_msgs = [{"sender": msg.sender, "content": msg.content} for msg in conv.messages[-20:]]

    create_message(
        db=db,
        conversation_id=conv.id,
        sender='user',
        content=request.content,
        pinyin=get_pinyin_list(request.content)
    )

    ai_content = get_ai_response(recent_msgs, conv.bot, conv.user, request.content)

    ai_msg = create_message(
        db=db,
        conversation_id=conv.id,
        sender='ai',
        content=ai_content,
        pinyin=get_pinyin_list(ai_content)
    )

    return MessageResponse(content=ai_content, pinyin=ai_msg.pinyin)
