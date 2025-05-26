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
    and limit your response to about 100 characters or less.\n
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
