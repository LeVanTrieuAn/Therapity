import json

with open("/app/database/thapsang_db.json", "r", encoding="utf-8") as f:
    db = json.load(f)

accounts = db.get("_accounts", {})
profiles = db.get("_profiles", {})

print("REGISTERED ACCOUNTS:")
for u, p in accounts.items():
    prof = profiles.get(u, {})
    print(f"- {u}: {prof.get('displayName', u)}")
