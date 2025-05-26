from pypinyin import pinyin, lazy_pinyin, Style
from helpers.text_processing import remove_emojis

def get_pinyin_list(text: str) -> list[str]:
    clean_text = remove_emojis(text)
    if not clean_text:
        return []
    pinyin_conversion = pinyin(clean_text, strict=False)
    return [item for sublist in pinyin_conversion for item in sublist]

def get_lazy_pinyin(text: str) -> list[str]:
    return lazy_pinyin(text)
