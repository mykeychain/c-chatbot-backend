from pypinyin import pinyin, lazy_pinyin, Style

def get_pinyin_list(text: str) -> list[str]:
    pinyin_conversion = pinyin(text, strict=False)
    return [item for sublist in pinyin_conversion for item in sublist]

def get_lazy_pinyin(text: str) -> list[str]:
    return lazy_pinyin(text)
