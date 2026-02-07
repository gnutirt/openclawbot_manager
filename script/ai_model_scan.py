import subprocess
import sys
import json
from pathlib import Path

# --- SETUP PATH ---
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from utils.other_utils import read_config, get_vietnam_time
from utils.telegram_utils import send_telegram_notification

# Đường dẫn file
CONFIG_PATH = str(ROOT / "config" / "config.cfg")
JSON_OUTPUT_PATH = str(ROOT / "config" / "ai_free_model_list.json")

def run_model_scan():
    """Chạy scan với flag --json, lưu vào file và gửi tóm tắt qua Telegram."""
    cfg = read_config(CONFIG_PATH)
    ID_LOG_CHANNEL = cfg.get("API_KEYS", "TELEGRAM_CHAT_ID_CHANNEL_LOG", fallback=None)
    
    now = get_vietnam_time()
    # Thêm flag --json để nhận output sạch từ openclaw
    command = "openclaw models scan --no-probe --json"
    
    print(f"[{now}] 🔍 Đang quét danh sách model (JSON mode)...")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        stdout_output = result.stdout.strip()
        stderr_output = result.stderr.strip()
        
        if result.returncode == 0:
            try:
                # 1. Parse trực tiếp từ JSON output
                models_list = json.loads(stdout_output)
                
                # 2. Lưu file JSON
                with open(JSON_OUTPUT_PATH, "w", encoding="utf-8") as f:
                    json.dump(models_list, f, indent=4, ensure_ascii=False)
                
                count = len(models_list)
                print(f"✅ Đã lưu {count} model vào {JSON_OUTPUT_PATH}")
                
                # 3. Gửi thông báo rút gọn
                msg = (
                    f"────────────────────\n"
                    f"<b>🤖 AI MODEL SCAN COMPLETE</b>\n"
                    f"────────────────────\n"
                    f"<b>Status:</b> 🎉 THÀNH CÔNG\n"
                    f"<b>Models Found:</b> <code>{count}</code>\n"
                    f"<b>Time:</b> <code>{now}</code>\n"
                    f"<b>File:</b> <code>ai_free_model_list.json</code>\n"
                    f"────────────────────"
                )
            except json.JSONDecodeError as je:
                print(f"❌ Lỗi parse JSON từ output: {je}")
                msg = f"<b>🤖 AI MODEL SCAN ERROR</b>\nLỗi parse JSON output: <code>{str(je)}</code>"
        else:
            msg = (
                f"────────────────────\n"
                f"<b>🤖 AI MODEL SCAN FAILED</b>\n"
                f"────────────────────\n"
                f"<b>Status:</b> ❌ THẤT BẠI\n"
                f"<b>Error:</b> <code>{stderr_output[:100]}</code>\n"
                f"<b>Time:</b> <code>{now}</code>\n"
                f"────────────────────"
            )
            
        send_telegram_notification(msg, config_path=CONFIG_PATH, target_chat=ID_LOG_CHANNEL)

    except Exception as e:
        print(f"❌ Lỗi: {e}")
        err_msg = f"<b>🤖 SYSTEM ERROR</b>\nScan failed with error: <code>{str(e)}</code>"
        send_telegram_notification(err_msg, config_path=CONFIG_PATH, target_chat=ID_LOG_CHANNEL)

if __name__ == "__main__":
    run_model_scan()
 