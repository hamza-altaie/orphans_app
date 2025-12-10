# app_settings.py
import json
import os

SETTINGS_FILE = "app_settings.json"

_default_settings = {
    "currency_symbol": "د.ع",   # تقدر تغير الافتراضي إذا تريد
    "default_export_dir": "",
}

_settings = _default_settings.copy()


def load_settings():
    """تحميل الإعدادات من ملف JSON إن وجد، وإلا استخدام الافتراضي."""
    global _settings
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            _settings.update({
                "currency_symbol": data.get("currency_symbol", _default_settings["currency_symbol"]),
                "default_export_dir": data.get("default_export_dir", _default_settings["default_export_dir"]),
            })
        except Exception:
            _settings = _default_settings.copy()
    else:
        _settings = _default_settings.copy()


def save_settings():
    """حفظ الإعدادات الحالية في ملف JSON."""
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(_settings, f, ensure_ascii=False, indent=2)


# تحميل الإعدادات أول ما ينستورد الملف
load_settings()


def get_currency_symbol() -> str:
    return _settings.get("currency_symbol", "")


def set_currency_symbol(symbol: str):
    _settings["currency_symbol"] = symbol.strip()
    save_settings()


def get_default_export_dir() -> str:
    return _settings.get("default_export_dir", "")


def set_default_export_dir(path: str):
    _settings["default_export_dir"] = path.strip()
    save_settings()
