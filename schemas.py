from pydantic import BaseModel
from typing import List, Optional
import datetime

class ConversationCreateRequest(BaseModel):
    user_id: str
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

class ConversationSchema(BaseModel):
    id: str
    user_id: str
    created_at: datetime.datetime
    messages: List[MessageSchema] = []

    class Config:
        orm_mode = True
