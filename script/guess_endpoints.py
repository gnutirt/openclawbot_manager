import requests
import json

URL_BASE = "http://192.168.0.219:8317/v0/management"
KEY = "gau_dai_ca_88"
HEADERS = {"Authorization": f"Bearer {KEY}"}

endpoints = [
    "/auth-files/details?name=antigravity-ngtritung@gmail.com.json",
    "/auth-files/status?name=antigravity-ngtritung@gmail.com.json",
    "/balances",
    "/quota",
    "/quotas",
    "/limits",
    "/usage/details",
    "/providers",
    "/providers/antigravity/balances",
    "/account/balances"
]

if __name__ == "__main__":
    for ep in endpoints:
        print(f"Testing {ep}...", end=" ")
        try:
            res = requests.get(f"{URL_BASE}{ep}", headers=HEADERS, timeout=3)
            print(f"Status: {res.status_code}")
            if res.status_code == 200:
                print(f"Response: {res.text[:200]}...")
        except Exception as e:
            print(f"Error: {e}")
