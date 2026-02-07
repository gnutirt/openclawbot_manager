# utils/telegram_utils.py
import os
import time
import logging
import configparser
import codecs
import requests
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Không còn phụ thuộc vào vnstock.botbuilder nữa để tránh lỗi version
Messenger = None 

def sanitize(value: Optional[str]) -> Optional[str]:
    if value is None: return None
    v = str(value).split("#")[0].strip()
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        v = v[1:-1].strip()
    return v or None

def read_config(path: str = "config.cfg") -> configparser.ConfigParser:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    cfg = configparser.ConfigParser()
    try:
        with codecs.open(path, "r", "utf-8") as f:
            cfg.read_file(f)
    except UnicodeDecodeError:
        with codecs.open(path, "r", "cp1252") as f:
            cfg.read_file(f)
    return cfg

def parse_bool(value: Optional[str]) -> bool:
    if value is None: return False
    v = str(value).strip().lower()
    return v in ("1", "true", "yes", "on")

def telegram_api_send_message_raw(bot_token: str, chat_id: str, text: str) -> Dict[str, Any]:
    """Gửi tin nhắn qua Telegram API bằng requests - Cực kỳ ổn định"""
    bot_token = sanitize(bot_token)
    if not bot_token:
        raise ValueError("Empty bot_token")
    base = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        resp = requests.post(base, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"Telegram send error: {e}")
        return {"ok": False, "error": str(e)}

def telegram_api_edit_message_text(bot_token: str, chat_id: str, message_id: int, text: str) -> Dict[str, Any]:
    """Chỉnh sửa tin nhắn đã gửi (Progress bar)"""
    bot_token = sanitize(bot_token)
    base = f"https://api.telegram.org/bot{bot_token}/editMessageText"
    try:
        resp = requests.post(base, json={
            "chat_id": chat_id, 
            "message_id": message_id, 
            "text": text, 
            "parse_mode": "HTML"
        }, timeout=20)
        return resp.json()
    except Exception:
        return {}

class VnstockSender:
    """Phiên bản mới: Tự gửi tin nhắn không cần vnstock.botbuilder"""
    def __init__(self, token_key: str, channel: Optional[str] = None, platform: str = "telegram"):
        self.token_key = token_key
        self.channel = channel

    def send_message(self, message: str, **kwargs) -> Dict[str, Any]:
        return telegram_api_send_message_raw(self.token_key, self.channel, message)

class TelegramReporter:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send_message(self, text: str):
        return telegram_api_send_message_raw(self.bot_token, self.chat_id, text)

# Hàm kiểm tra tự động
def run_self_test(config_path: str = "config.cfg"):
    print(f"--- Running Telegram Test ({config_path}) ---")
    try:
        cfg = read_config(config_path)
        token = cfg.get("API_KEYS", "TELEGRAM_TOKEN", fallback=None)
        chat_id = cfg.get("API_KEYS", "TELEGRAM_CHAT_ID", fallback=None)
        
        if not token or not chat_id:
            print("Lỗi: Thiếu TOKEN hoặc CHAT_ID trong config.cfg")
            return

        res = telegram_api_send_message_raw(token, chat_id, "<b>Vnstock Bot Test</b>: Kết nối thành công!")
        if res.get("ok"):
            print("[OK] Tin nhắn đã gửi thành công!")
        else:
            print(f"[FAIL] Lỗi: {res.get('error')}")
    except Exception as e:
        print(f"[ERROR] {e}")

def send_telegram_notification(message: str, config_path: str = "config/config.cfg", target_chat: str = None, token_key: str = "TELEGRAM_TOKEN"):
    """
    Hàm tổng quát để gửi thông báo qua Telegram.
    :param token_key: Khóa của Token trong config (ví dụ: 'TELEGRAM_TOKEN' hoặc 'TELEGRAM_TOKEN_BOT_GAU_CK').
    """
    try:
        cfg = read_config(config_path)
        token = cfg.get("API_KEYS", token_key, fallback=None)
        
        # Fallback nếu không tìm thấy token đặc thù, quay về dùng token chính
        if not token:
            token = cfg.get("API_KEYS", "TELEGRAM_TOKEN", fallback=None)
        
        # Nếu target_chat được truyền vào thì dùng nó, nếu không thì mới lấy từ config
        chat_id = target_chat if target_chat else cfg.get("API_KEYS", "TELEGRAM_CHAT_ID", fallback=None)
        
        if not token or not chat_id:
            print(f"❌ Lỗi: Thiếu TOKEN hoặc CHAT_ID (Target: {chat_id})")
            return False

        res = telegram_api_send_message_raw(token, chat_id, message)
        
        if res.get("ok"):
            print(f"[OK] Đã gửi thông báo tới Telegram ID: {chat_id}")
            return True
        else:
            error_info = res.get('description') or res.get('error')
            print(f"[FAIL] Telegram Error ({chat_id}): {error_info}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Không thể gửi Telegram: {e}")
        return False

if __name__ == "__main__":
    run_self_test()