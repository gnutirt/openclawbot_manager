import subprocess
import random
import sys
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

# --- PHẦN QUAN TRỌNG: FIX PATH ---
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from other_utils import read_config, get_vietnam_time
from telegram_utils import send_telegram_notification

# Đường dẫn file
CONFIG_PATH = str(ROOT / "config" / "config.cfg")
JSON_MODEL_PATH = str(ROOT / "config" / "ai_no_free.json")

def run_openclaw_command():
    cfg = read_config(CONFIG_PATH)
    ID_LOG_CHANNEL = cfg.get("API_KEYS", "TELEGRAM_CHAT_ID_CHANNEL_LOG", fallback=None)
    now = get_vietnam_time()

    # 1. Đọc danh sách model từ file JSON
    try:
        if not Path(JSON_MODEL_PATH).exists():
            print(f"❌ Lỗi: Không tìm thấy file {JSON_MODEL_PATH}.")
            return

        with open(JSON_MODEL_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        all_models = data.get("models", [])
        if not all_models:
            print("❌ Lỗi: Danh sách model trống.")
            return

        # 2. Lọc chỉ lấy models của service cliproxy
        cliproxy_models = [m for m in all_models if m.get("service") == "cliproxy"]
        
        if not cliproxy_models:
            print("❌ Lỗi: Không tìm thấy model nào của service cliproxy.")
            return
        
        # 3. Chọn ngẫu nhiên 1 model từ cliproxy
        selected_model = random.choice(cliproxy_models)
        model_ref = selected_model.get("full_path")
        model_name = model_ref.split("/")[-1] if model_ref else "Unknown"

        if not model_ref:
            print("❌ Lỗi: Không lấy được full_path từ dữ liệu.")
            return

        command = f"openclaw models set {model_ref}"
        print(f"[{now}] 🚀 Đang thực thi: {command}")
        print(f"📦 Service: cliproxy | Model: {model_name}")
        
        # 3. Chạy lệnh
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        output = result.stdout.strip() or "Success"
        
        msg = (
            f"────────────────────\n" 
            f"<b>🤖 OPENCLAW AI SWITCH</b>\n"
            f"────────────────────\n"             
            f"<b>Status:</b> 🎉 THÀNH CÔNG\n"
            f"<b>Time  :</b> <code>{now}</code>\n"
            f"<b>Name  :</b> <code>{model_name}</code>\n"
            f"<b>Ref   :</b> <code>{model_ref}</code>\n"
            f"<b>Log   :</b> <i>{output[:80]}...</i>\n"
            f"────────────────────\n"
        )
        
        print(f"✅ Đã chuyển sang: {model_ref}")
        # send_telegram_notification(msg, config_path=CONFIG_PATH, target_chat=ID_LOG_CHANNEL)

    except (json.JSONDecodeError, Exception) as e:
        error_msg = (
            f"────────────────────\n" 
            f"<b>🤖 OPENCLAW AI SWITCH</b>\n"
            f"────────────────────\n"
            f"<b>Status:</b> ❌ THẤT BẠI\n"
            f"<b>Time  :</b> <code>{now}</code> (VN)\n"
            f"<b>Error :</b> <code>{str(e)[:100]}</code>\n"
            f"────────────────────\n"
        )
        print(f"❌ Lỗi: {str(e)}")
        send_telegram_notification(error_msg, config_path=CONFIG_PATH, target_chat=ID_LOG_CHANNEL)

if __name__ == "__main__":
    run_openclaw_command()
