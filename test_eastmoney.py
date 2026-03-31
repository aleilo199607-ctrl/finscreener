"""Test eastmoney API - no unicode"""
import sys, os
# Clear proxy settings
for k in ["HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy", "ALL_PROXY", "all_proxy"]:
    os.environ.pop(k, None)

sys.path.insert(0, "c:/Users/42337/WorkBuddy/20260330172538/FinScreener/backend")
from app_fc import fetch_eastmoney_all_stocks, parse_eastmoney_stock, fetch_eastmoney_indices

print("=" * 50)
print("Test: full A-share data")
stocks = fetch_eastmoney_all_stocks()
print(f"Total stocks: {len(stocks)}")

if stocks:
    s = parse_eastmoney_stock(stocks[0])
    print(f"Sample: {s['name']}({s['ts_code']}) price={s['close']} pct={s['pct_chg']}%")
else:
    print("NO DATA - might be proxy issue (OK on aliyun FC)")

print("\n" + "=" * 50)
print("Test: index data")
indices = fetch_eastmoney_indices()
print(f"Total indices: {len(indices)}")
for idx in indices:
    print(f"  {idx['name']}: {idx['close']} ({idx['pct_chg']}%)")

print("\nDone!")
