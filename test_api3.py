"""Test eastmoney without proxy - direct session"""
import sys, os
for k in ["HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy", "ALL_PROXY", "all_proxy"]:
    os.environ.pop(k, None)

import requests

# Create session with no proxy
session = requests.Session()
session.trust_env = False  # Ignore env proxy settings

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://quote.eastmoney.com/",
}

print("Test: clist API with trust_env=False")
try:
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": 1, "pz": 100, "po": 1, "np": 1,
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": 2, "invt": 2, "fid": "f3",
        "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
        "fields": "f12,f14,f2,f3,f4,f5,f6",
    }
    resp = session.get(url, params=params, headers=headers, timeout=15)
    print(f"  Status: {resp.status_code}")
    data = resp.json()
    if data.get("data") and data["data"].get("diff"):
        items = data["data"]["diff"]
        print(f"  Got {len(items)} stocks")
        for item in items[:5]:
            print(f"    {item.get('f14')}({item.get('f12')}): price={item.get('f2')} pct={item.get('f3')}%")
    else:
        print(f"  No data")
except Exception as e:
    print(f"  Error: {e}")

print("\nDone!")
