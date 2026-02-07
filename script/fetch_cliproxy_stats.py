
import requests
import json
import socket
import sys
from pathlib import Path

# Add script dir to path to import utils
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.append(str(SCRIPT_DIR))

from other_utils import read_config

ROOT = SCRIPT_DIR.parent
CONFIG_PATH = str(ROOT / "config" / "config.cfg")
config = read_config(CONFIG_PATH)

# --- CONFIGURATION ---
def get_base_url():
    # Try fetching from config first
    url = config.get("API_KEYS", "CLIPROXY_MANAGEMENT_URL", fallback="")
    if url: return url

    # Fallback to auto-detection if not in config
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        if s.connect_ex(('127.0.0.1', 8317)) == 0:
            return "http://127.0.0.1:8317/v0/management"
        else:
            return "http://192.168.0.219:8317/v0/management"

MANAGEMENT_URL = get_base_url()
MANAGEMENT_KEY = config.get("API_KEYS", "CLIPROXY_MANAGEMENT_KEY", fallback="")

if not MANAGEMENT_KEY:
    print("⚠️ Warning: CLIPROXY_MANAGEMENT_KEY not found in config. Using empty key.")

headers = {
    "Authorization": f"Bearer {MANAGEMENT_KEY}",
    "Content-Type": "application/json"
}

def format_tokens(n):
    if n >= 1000000:
        return f"{n/1000000:.2f} triệu"
    if n >= 1000:
        return f"{n/1000:.1f}k"
    return str(n)

def fetch_stats():
    print(f"📡 Đang kết nối tới: {MANAGEMENT_URL}...")
    
    # 1. Lấy Usage Statistics
    try:
        print("\n📊 --- THỐNG KÊ SỬ DỤNG ---")
        response = requests.get(f"{MANAGEMENT_URL}/usage", headers=headers)
        if response.status_code == 200:
            data = response.json().get("usage", {})
            total_req = data.get("total_requests", 0)
            total_tokens = data.get("total_tokens", 0)
            
            print(f"✅ Tổng số yêu cầu: {total_req}")
            print(f"✅ Tổng số token: {format_tokens(total_tokens)}")
            
            # Liệt kê theo model
            print("\n📈 Chi tiết theo Model:")
            apis = data.get("apis", {})
            for api_name, api_info in apis.items():
                models = api_info.get("models", {})
                for model_name, model_info in models.items():
                    m_req = model_info.get("total_requests", 0)
                    m_tokens = model_info.get("total_tokens", 0)
                    print(f"  - {model_name}: {m_req} reqs | {format_tokens(m_tokens)} tokens")
        else:
            print(f"❌ Lỗi {response.status_code}: Không có quyền truy cập Usage Statistics.")
            print("👉 Vui lòng kiểm tra lại MANAGEMENT_KEY (Mật khẩu admin) trong config.cfg.")
    except Exception as e:
        print(f"❌ Lỗi kết nối: {e}")

    # 2. Lấy Auth Files (Hạn ngạch)
    try:
        print("\n🛡️ --- QUẢN LÝ HẠN NGẠCH ---")
        response = requests.get(f"{MANAGEMENT_URL}/auth-files", headers=headers)
        if response.status_code == 200:
            files = response.json().get("files", [])
            if not files:
                print("⚠️ Không có file auth nào.")
            for f in files:
                provider = f.get("provider", "N/A").upper()
                name = f.get("name", "Unknown")
                status = f.get("status", "unknown")
                size = f.get("size", 0)
                
                status_icon = "🟢" if status == "ready" else "🔴"
                print(f"{status_icon} [{provider}] {name}")
                print(f"   └─ Trạng thái: {status} | Size: {size} bytes")
        else:
            print(f"❌ Lỗi {response.status_code}: Không có quyền truy cập Auth Files.")
    except Exception as e:
        print(f"❌ Lỗi kết nối: {e}")

if __name__ == "__main__":
    fetch_stats()
