import re

def remove_emojis(text: str) -> str:
    pattern = re.compile("["
        # Basic emoji ranges
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F900-\U0001F9FF"  # supplemental symbols
        u"\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        # Additional symbol ranges
        u"\U00002600-\U000026FF"  # miscellaneous symbols
        u"\U00002700-\U000027BF"  # dingbats
        u"\U0000FE00-\U0000FE0F"  # variation selectors
        u"\U0001F000-\U0001F02F"  # mahjong tiles
        u"\U0001F0A0-\U0001F0FF"  # playing cards
        u"\U0001F200-\U0001F2FF"  # enclosed ideographic supplement
        u"\U0001F700-\U0001F77F"  # alchemical symbols
        # Special Chinese-related ranges
        # u"\U00003100-\U0000312F"  # bopomofo
        # u"\U00003190-\U000319F"  # kanbun
        # u"\U0000FE30-\U0000FE4F"  # cjk compatibility forms
        # Combining characters and variation selectors
        u"\U0000200D"             # zero width joiner
        u"\U0000FE0F"             # variation selector-16
        u"\U000020E3"             # combining enclosing keycap
        u"\U000020D0-\U000020FF"  # combining diacritical marks
        u"\U0000FE20-\U0000FE2F"  # combining half marks
        "]+", flags=re.UNICODE)
    
    # Remove emojis and special characters
    text = pattern.sub('', text)
    
    # Remove any remaining variation selectors and zero-width characters
    text = re.sub(r'[\uFE00-\uFE0F\u200B-\u200F\u2060-\u2064]', '', text)
    
    # Handle VS16-keycap sequences and other remnant emoji sequences
    text = re.sub(r'[\u00A9\u00AE][\uFE00-\uFE0F]?', '', text)
    
    return text.strip() 