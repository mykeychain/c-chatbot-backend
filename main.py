import os

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import (
    ConversationCreateRequest,
    ConversationCreateResponse,
    ConversationDeleteResponse,
    ConversationSchema,
    MessageRequest,
    MessageResponse,
    MessageSchema,
    BotSchema,
    TranslationRequest,
    TranslationResponse,
)
from crud import (
    create_conversation,
    create_message,
    delete_conversation,
    get_conversation,
    list_user_conversations,
    get_conversation_messages,
    get_available_bots,
    get_translation,
    create_translation,
)
from dependencies import get_db
from helpers.text_processing import remove_emojis
from helpers.translator import ensure_zh_en_installed, translate_chinese_to_english
from helpers.ai import get_ai_response
from helpers.pinyin import get_pinyin_list
from sqlalchemy.orm import Session
from typing import List


@asynccontextmanager
async def lifespan(app: FastAPI): 
    ensure_zh_en_installed()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
  CORSMiddleware,
  allow_origins=os.environ.get('CORS_URLS'),
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"], 
)

@app.post("/api/conversations", response_model=ConversationSchema)
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

        ai_content, ai_pinyin, ai_translation = get_ai_response([], conv.bot, conv.user, request.initial_message, db)
        create_message(
            db=db,
            conversation_id=conv.id,
            sender='ai',
            content=ai_content,
            pinyin=ai_pinyin,
            translation=ai_translation
        )

    return conv

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

@app.get("/api/conversations/{conversation_id}/messages", response_model=List[MessageSchema])
def api_get_conversation_messages(conversation_id: str, db: Session = Depends(get_db)):
    conv = get_conversation(db, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    msgs = get_conversation_messages(db, conversation_id)
    return msgs

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

    ai_content, ai_pinyin, ai_translation = get_ai_response(recent_msgs, conv.bot, conv.user, request.content, db)

    ai_msg = create_message(
        db=db,
        conversation_id=conv.id,
        sender='ai',
        content=ai_content,
        pinyin=ai_pinyin,
        translation=ai_translation
    )

    return MessageSchema(
        id=ai_msg.id, 
        sender=ai_msg.sender, 
        content=ai_msg.content, 
        pinyin=ai_msg.pinyin, 
        translation=ai_msg.translation,
        created_at=ai_msg.created_at
    )

@app.get("/api/users/{user_id}/available-bots", response_model=List[BotSchema])
def api_get_available_bots(user_id: str, db: Session = Depends(get_db)):
    return get_available_bots(db, user_id)

@app.post("/api/translate", response_model=TranslationResponse)
def api_translate_chinese_to_english(request: TranslationRequest, db: Session = Depends(get_db)):
    if not request.is_chinese:
        raise HTTPException(status_code=400, detail="Text must contain Chinese characters")
    
    formatted_text = remove_emojis(request.text)

    translation = get_translation(db, formatted_text)
    if translation:
        return TranslationResponse(
            original_text=request.text,
            translated_text=translation.value
        )
    
    translated = translate_chinese_to_english(formatted_text)
    create_translation(db, formatted_text, translated)
    
    return TranslationResponse(
        original_text=request.text,
        translated_text=translated
    )
