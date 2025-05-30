import os
import dotenv
from pathlib import Path
from helpers.text_processing import remove_emojis

dotenv.load_dotenv()
project_data = Path(os.getenv("XDG_DATA_HOME", "./argos_data"))
pkg_dir      = Path(os.getenv("ARGOS_TRANSLATE_PACKAGE_DIR", project_data / "packages"))
project_data.mkdir(exist_ok=True)
pkg_dir.mkdir(parents=True, exist_ok=True)

os.environ.setdefault("XDG_DATA_HOME", str(project_data))
os.environ.setdefault("ARGOS_TRANSLATE_PACKAGE_DIR", str(pkg_dir))

import argostranslate.package
import argostranslate.translate

def ensure_zh_en_installed():
    installed = argostranslate.package.get_installed_packages()
    has_zh_en = any(
        pkg.from_code == "zh" and pkg.to_code == "en"
        for pkg in installed
    )
    if not has_zh_en:
        argostranslate.package.update_package_index()
        available = argostranslate.package.get_available_packages()
        zh_en_pkg = next(
            p for p in available
            if p.from_code == "zh" and p.to_code == "en"
        )
        argostranslate.package.install_from_path(zh_en_pkg.download())

def translate_chinese_to_english(text: str) -> str:
    res = google_translate(text)
    if not res: 
        res = argos_translate(text)

    return res if res else ""

def google_translate(text: str) -> str: 
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()
    if isinstance(text, bytes):
        text = text.decode("utf-8")

    result = translate_client.translate(text, target_language='en', format_='text')
    return result["translatedText"]

def argos_translate(text: str) -> str: 
    clean_text = remove_emojis(text)
    if not clean_text:
        return ""
    return argostranslate.translate.translate(clean_text, "zh", "en")