"""Test alternative eastmoney API"""
import sys, os, requests
for k in ["HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy", "ALL_PROXY", "all_proxy"]:
    os.environ.pop(k, None)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://quote.eastmoney.com/",
}

# Test 1: clist with smaller page
print("Test 1: clist API (pz=100)")
try:
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": 1, "pz": 100, "po": 1, "np": 1,
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": 2, "invt": 2, "fid": "f3",
        "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
        "fields": "f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23",
    }
    resp = requests.get(url, params=params, headers=headers, timeout=15)
    print(f"  Status: {resp.status_code}")
    data = resp.json()
    if data.get("data") and data["data"].get("diff"):
        items = data["data"]["diff"]
        print(f"  Got {len(items)} stocks")
        for item in items[:3]:
            print(f"    {item.get('f14')}({item.get('f12')}): price={item.get('f2')} pct={item.get('f3')}%")
    else:
        print(f"  No data: {str(data)[:200]}")
except Exception as e:
    print(f"  Error: {e}")

# Test 2: another endpoint
print("\nTest 2: stocklist API")
try:
    url2 = "https://push2.eastmoney.com/api/qt/slist/get"
    params2 = {
        "pn": 1, "pz": 20, "po": 1, "np": 1,
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": 2, "invt": 2,
        "fid": "f3",
        "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
        "fields": "f12,f14,f2,f3",
    }
    resp2 = requests.get(url2, params=params2, headers=headers, timeout=15)
    print(f"  Status: {resp2.status_code}")
    data2 = resp2.json()
    if data2.get("data") and data2["data"].get("diff"):
        items2 = data2["data"]["diff"]
        print(f"  Got {len(items2)} stocks")
        for item in items2[:3]:
            print(f"    {item.get('f14')}({item.get('f12')}): price={item.get('f2')} pct={item.get('f3')}%")
    else:
        print(f"  No data: {str(data2)[:200]}")
except Exception as e:
    print(f"  Error: {e}")

print("\nDone!")
