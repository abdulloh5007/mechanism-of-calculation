import json

def load_items():
    with open("items.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_items(items):
    with open("items.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
