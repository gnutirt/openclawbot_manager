
import requests
import json
import sys
from pathlib import Path

# Add script dir to path to import utils
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.append(str(SCRIPT_DIR))

from other_utils import read_config

ROOT = SCRIPT_DIR.parent
CONFIG_PATH = str(ROOT / "config" / "config.cfg")
config = read_config(CONFIG_PATH)

URL_BASE = config.get("API_KEYS", "CLIPROXY_MANAGEMENT_URL", fallback="http://127.0.0.1:8317/v0/management")
KEY = config.get("API_KEYS", "CLIPROXY_MANAGEMENT_KEY", fallback="")
HEADERS = {"Authorization": f"Bearer {KEY}"}

def dump_endpoint(endpoint):
    print(f"\n--- Dumping {endpoint} ---")
    try:
        res = requests.get(f"{URL_BASE}{endpoint}", headers=HEADERS, timeout=5)
        if res.status_code == 200:
            data = res.json()
            filename = f"dump_{endpoint.replace('/', '_').replace('?', '_')}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved to {filename}")
        else:
            print(f"❌ Error {res.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    endpoints = [
        "/auth-files",
        "/usage",
        "/config",
        "/latest-version",
        "/request-log"
    ]
    for ep in endpoints:
        dump_endpoint(ep)
