import regex
import unicodedata
import hashlib

_EMOJI_CLEANER = regex.compile(
    r'(?:'
      r'\p{Emoji_Presentation}'
      r'|[\p{Variation_Selector}\p{Join_Control}\U000020E3]'  
    r')+',
    flags=regex.VERSION1
)

def remove_emojis(text: str) -> str:
    """
    Remove emojis (Emoji), Extended_Pictographic pictographs,
    plus Variation_Selector and Join_Control characters—all in one pass.
    """
    return _EMOJI_CLEANER.sub('', text).strip()

def normalize_for_hash(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)

    return text

def make_digest(text: str) -> str:
    norm = normalize_for_hash(text)
    b = norm.encode("utf-8")
    return hashlib.sha256(b).hexdigest()
