import requests
import json

URL = "http://192.168.0.219:8317/v0/management/auth-files/download?name=antigravity-ngtritung@gmail.com.json"
KEY = "gau_dai_ca_88"
HEADERS = {"Authorization": f"Bearer {KEY}"}

try:
    res = requests.get(URL, headers=HEADERS, timeout=10)
    if res.status_code == 200:
        data = res.json()
        with open("antigravity_details.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("✅ Success! Downloaded to antigravity_details.json")
    else:
        print(f"❌ Error {res.status_code}: {res.text}")
except Exception as e:
    print(f"❌ Exception: {e}")
