import os
import dotenv
from pathlib import Path

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
    return argostranslate.translate.translate(text, "zh", "en")