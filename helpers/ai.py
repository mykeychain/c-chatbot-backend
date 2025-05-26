import json
import re

from crud import create_translation, get_translation
from gemini import generate_response
from models import Bot, User
from sqlalchemy.orm import Session

from helpers.text_processing import remove_emojis

BASIC_PROMPT = '''You are a conversational Mandarin-speaking chatbot.
    You must respond in a specific JSON format with three fields:
    - "response": Your response in Traditional Chinese characters (limit to about 100 characters)
    - "pinyin": The pinyin for your response with accents on the characters (excluding any emojis)
    - "translation": English translation of your response (excluding any emojis)
    
    Keep your responses natural, like texting a friend.
    You may use emojis very sparingly in the "response" field only.
    
    Example response format:
    {
        "response": "哈囉！很高興認識你呀！💪",
        "pinyin": "hā luō！ hěn gāo xìng rèn shí nǐ ya ！",
        "translation": "Hello! Nice to meet you!"
    }
\n'''

DIFFICULTY_PROMPTS = {
    'easy': "The user is at an easy difficulty so respond with the vocabulary that a 5th grader may understand.\n",
    'medium': "The user is at a medium difficulty so respond with the vocabulary that a 9th grader may understand.\n",
    'hard': "The user is at a hard difficulty so respond with the vocabulary that an undergraduate may understand.\n",
    'native': "The user is at a native difficulty so respond with the vocabulary that a native speaker may understand.\n",
}

_JSON_BLOCK = re.compile(
    r'''(?sx)            # allow dot to match newline, and ignore whitespace/comments
    ```json\s*           # optional opening fence with "json" tag
    (?P<payload>\{.*?\}) # capture the {...} JSON payload
    \s*```               # optional closing fence
    |
    (?P<object>\{.*?\})  # or just a raw {...} object
    '''
)

def parse_ai_response(response: str) -> tuple[str, list[str], str]:
    """
    Parse the AI response JSON into its components.
    Note, the response we get from Gemini is fenced with backticks and a json label.
    """
    m = _JSON_BLOCK.search(response)
    if not m:
        raise ValueError(f"No JSON object found in model output:\n{response!r}")
    payload = m.group("payload") or m.group("object")
    data = json.loads(payload)
    return (
        data["response"],
        data["pinyin"].split(),
        data["translation"]
    )

def get_ai_response(recent_msgs: list[dict], bot: Bot, user: User, user_content: str, db: Session) -> tuple[str, list[str], str]:
    prompt = BASIC_PROMPT + bot.character_notes + DIFFICULTY_PROMPTS[user.difficulty]
    for msg in recent_msgs:
        role = "User" if msg["sender"] == "user" else "AI"
        prompt += f"{role}: {msg['content']}\n"

    prompt += f"User: {user_content}\nAI:"
    
    raw_response = generate_response(prompt)
    content, pinyin, translation = parse_ai_response(raw_response)
    
    clean_content = remove_emojis(content)
    existing_translation = get_translation(db, clean_content)
    if not existing_translation and clean_content:
        create_translation(db, clean_content, translation)
    
    return content, pinyin, translation
