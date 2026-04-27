"""
Straicoで利用可能なモデル一覧を取得して表示するスクリプト
使い方: python scripts/list_straico_models.py
"""

import os
import sys
import json
import requests

API_KEY = os.environ.get("STRAICO_API_KEY")
if not API_KEY:
    print("❌ 環境変数 STRAICO_API_KEY を設定してください")
    print("   例: export STRAICO_API_KEY=your_key_here")
    sys.exit(1)

resp = requests.get(
    "https://api.straico.com/v1/models",
    headers={"Authorization": f"Bearer {API_KEY}"},
    timeout=15,
)
resp.raise_for_status()
data = resp.json()

models = data.get("data", data) if isinstance(data, dict) else data

print(f"\n{'='*60}")
print(f"  Straico 利用可能モデル一覧（{len(models)}件）")
print(f"{'='*60}\n")

for m in models:
    mid   = m.get("id") or m.get("model") or m.get("name", "")
    mname = m.get("name") or mid
    print(f"  識別子: {mid}")
    print(f"  名前  : {mname}")
    print()

print("STRAICO_MODEL に設定する値は「識別子」の列の文字列です。")
