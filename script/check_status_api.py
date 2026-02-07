
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

# Load from config
URL_BASE = config.get("API_KEYS", "CLIPROXY_MANAGEMENT_URL", fallback="http://127.0.0.1:8317/v0/management")
KEY = config.get("API_KEYS", "CLIPROXY_MANAGEMENT_KEY", fallback="")

URL = f"{URL_BASE}/auth-files/status"
HEADERS = {"Authorization": f"Bearer {KEY}"}

try:
    res = requests.get(URL, headers=HEADERS, timeout=10)
    print(f"Status: {res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")
