import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# --- FIX PATH ĐỂ NHẬN UTILS ---
# .parent.parent vì file đang nằm trong python_plugins/openclaw_tools/
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from utils.other_utils import read_config
from utils.telegram_utils import send_telegram_notification

# Đường dẫn file trong thư mục config
CONFIG_PATH = str(ROOT / "config" / "config.cfg")
CONTEXT_PATH = str(ROOT / "config" / "context.json")

def get_vietnam_time():
    """Lấy thời gian hiện tại múi giờ VN (UTC+7)"""
    tz_vn = timezone(timedelta(hours=7))
    return datetime.now(tz_vn).strftime("%H:%M - %d/%m/%Y")

def send_ai_command_reply():
    # 1. Đọc config để lấy ID Channel Log
    cfg = read_config(CONFIG_PATH)
    ID_LOG_CHANNEL = cfg.get("API_KEYS", "TELEGRAM_CHAT_ID", fallback=None)
    now = get_vietnam_time()

    # 2. Đọc nội dung từ context.json
    try:
        context_file = Path(CONTEXT_PATH)
        if not context_file.exists():
            print(f"❌ Không tìm thấy file: {CONTEXT_PATH}")
            return
        with open(CONTEXT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Trích xuất dữ liệu
        cmd = data.get("command", "N/A")
        bot_reply = data.get("bot_reply", "N/A")

        # Kiểm tra nếu đúng là lệnh điều khiển thì mới gửi format đẹp
        if cmd == "aicommand":
            # Chỉ gửi nội dung bot_reply (vì trong bot_reply bạn đã để format danh sách lệnh rất đẹp rồi)
            # Thêm một dòng nhỏ phía dưới về thời gian để theo dõi log
            final_msg = (
                f"{bot_reply} "
                f"──────────────────── "
                f"🕒 <i>Cập nhật lúc: {now}</i>"
            )
        else:
            # Format mặc định cho các loại log khác
            final_msg = (
                f"<b>🤖 AI SYSTEM REPLY</b> "
                f"──────────────────── "
                f"📝 <b>Command:</b> <code>{cmd}</code> "
                f"💬 <b>Reply:</b> {bot_reply} "
                f"⏰ <b>Time:</b> <code>{now}</code>"
            )
        
        # 3. Gửi tin nhắn
        print(f"[{now}] 📤 Đang phản hồi lệnh: {cmd}")
        success = send_telegram_notification(final_msg, config_path=CONFIG_PATH, target_chat=ID_LOG_CHANNEL)
        if success:
            print(f"✅ Gửi phản hồi thành công!")
        else:
            print(f"❌ Gửi Telegram thất bại (Vui lòng kiểm tra Token/ID).")

    except json.JSONDecodeError:
        print(f"❌ Lỗi: File context.json sai định dạng JSON.")
    except Exception as e:
        print(f"❌ Lỗi hệ thống: {e}")

if __name__ == "__main__":
    send_ai_command_reply()