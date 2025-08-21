#!/usr/bin/env python3
import argparse
import csv
import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

DATA_FILE = os.path.join(os.path.dirname(__file__), "drugs.json")

def load_db() -> List[Dict[str, Any]]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print("Warning: drugs.json is corrupted; starting with empty DB.", file=sys.stderr)
            return []

def save_db(data: List[Dict[str, Any]]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def parse_date(s: str) -> str:
    try:
        dt = datetime.strptime(s, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        print("Invalid date format; use YYYY-MM-DD.", file=sys.stderr)
        sys.exit(1)

def add_item(args):
    data = load_db()
    item = {
        "name": args.name.strip(),
        "strength": (args.strength or "").strip(),
        "form": (args.form or "").strip(),
        "batch": (args.batch or "").strip(),
        "expiry": parse_date(args.expiry),
        "location": (args.location or "").strip(),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    data.append(item)
    save_db(data)
    print(f"Added: {item['name']} {item.get('strength','')} {item.get('form','')} — expiry={item['expiry']}")

def list_items(args):
    data = load_db()
    if not data:
        print("No medicines yet. Use 'add' to add your first one.")
        return
    # Sort by expiry ascending
    data.sort(key=lambda x: x.get("expiry", "9999-12-31"))
    for it in data:
        print(format_item(it))

def soon_items(args):
    days = int(args.days)
    data = load_db()
    today = datetime.today().date()
    limit = today + timedelta(days=days)
    soon = []
    for it in data:
        try:
            exp = datetime.strptime(it.get("expiry","9999-12-31"), "%Y-%m-%d").date()
        except ValueError:
            continue
        if today <= exp <= limit:
            soon.append(it)
    if not soon:
        print(f"No items expiring in the next {days} days.")
        return
    print(f"Expiring in the next {days} days:")
    for it in sorted(soon, key=lambda x: x["expiry"]):
        print(format_item(it))

def expired_items(args):
    data = load_db()
    today = datetime.today().strftime("%Y-%m-%d")
    ex = [it for it in data if it.get("expiry") and it["expiry"] < today]
    if not ex:
        print("No expired items 🎉")
        return
    print("Expired items:")
    for it in sorted(ex, key=lambda x: x["expiry"]):
        print(format_item(it))

def find_items(args):
    q = args.query.strip().lower()
    data = load_db()
    res = [it for it in data if q in it.get("name","").lower()]
    if not res:
        print("No matches.")
        return
    for it in sorted(res, key=lambda x: x["name"].lower()):
        print(format_item(it))

def export_csv(args):
    data = load_db()
    path = args.csv
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["name","strength","form","batch","expiry","location","created_at"])
        w.writeheader()
        for it in data:
            w.writerow({k: it.get(k,"") for k in w.fieldnames})
    print(f"Exported {len(data)} items to {path}")

def format_item(it: Dict[str, Any]) -> str:
    core = it.get("name","")
    if it.get("strength"): core += f" ({it['strength']})"
    if it.get("form"): core += f" {it['form']}"
    extra = []
    if it.get("batch"): extra.append(f"batch={it['batch']}")
    if it.get("expiry"): extra.append(f"expiry={it['expiry']}")
    if it.get("location"): extra.append(f"loc={it['location']}")
    return f"- {core} — " + ", ".join(extra) if extra else f"- {core}"

def main():
    p = argparse.ArgumentParser(description="Drug Expiry Tracker (simple, JSON-backed).")
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("add", help="Add a medicine")
    pa.add_argument("--name", required=True)
    pa.add_argument("--strength", default="")
    pa.add_argument("--form", default="")
    pa.add_argument("--batch", default="")
    pa.add_argument("--expiry", required=True, help="YYYY-MM-DD")
    pa.add_argument("--location", default="")
    pa.set_defaults(func=add_item)

    pl = sub.add_parser("list", help="List all medicines (sorted by expiry)")
    pl.set_defaults(func=list_items)

    ps = sub.add_parser("soon", help="List items expiring within N days (default 30)")
    ps.add_argument("--days", type=int, default=30)
    ps.set_defaults(func=soon_items)

    pe = sub.add_parser("expired", help="List expired items")
    pe.set_defaults(func=expired_items)

    pf = sub.add_parser("find", help="Search by name")
    pf.add_argument("--query", required=True)
    pf.set_defaults(func=find_items)

    px = sub.add_parser("export", help="Export all to CSV")
    px.add_argument("--csv", required=True)
    px.set_defaults(func=export_csv)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
