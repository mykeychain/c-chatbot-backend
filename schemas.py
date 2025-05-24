from pydantic import BaseModel
from typing import List, Optional
import datetime

class ConversationCreateRequest(BaseModel):
    user_id: str
    bot_id: str
    initial_message: Optional[str] = None

class ConversationCreateResponse(BaseModel):
    conversation_id: str

class ConversationDeleteResponse(BaseModel):
    success: bool

class MessageRequest(BaseModel):
    conversation_id: str
    content: str

class MessageResponse(BaseModel):
    content: str
    pinyin: List[str]

class MessageSchema(BaseModel):
    id: str
    sender: str
    content: str
    pinyin: List[str]
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class Bot(BaseModel): 
    id: str
    name: str

class ConversationSchema(BaseModel):
    id: str
    user_id: str
    bot: Bot
    created_at: datetime.datetime
    last_message: Optional[MessageSchema] = None

    class Config:
        orm_mode = True

class BotSchema(BaseModel):
    id: str
    name: str
    picture_url: Optional[str]

    class Config:
        orm_mode = True

class TranslationRequest(BaseModel):
    text: str

    @property
    def is_chinese(self) -> bool:
        return any('\u4e00' <= char <= '\u9fff' for char in self.text)

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
