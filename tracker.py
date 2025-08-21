#!/usr/bin/env python3
import argparse, os, json, sys, csv
from datetime import datetime, timedelta

DATA_FILE = os.path.join(os.path.dirname(__file__), "drugs.json")

def load_db():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_db(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def parse_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except Exception:
        print("Invalid date format, use YYYY-MM-DD", file=sys.stderr)
        sys.exit(1)

def add_item(args):
    data = load_db()
    name = args.name.strip()
    expiry = parse_date(args.expiry).strftime("%Y-%m-%d")
    for d in data:
        if d["name"].lower() == name.lower():
            print("Item already exists.")
            sys.exit(1)
    data.append({"name": name, "expiry": expiry})
    save_db(data)
    print(f"Added: {name} (expiry {expiry})")

def list_items(args):
    data = load_db()
    if not data:
        print("No drugs recorded.")
        return
    for d in sorted(data, key=lambda x: x["expiry"]):
        print(f"- {d['name']} (expiry {d['expiry']})")

def expiring(args):
    data = load_db()
    if not data:
        print("No drugs recorded.")
        return
    today = datetime.today()
    limit = today + timedelta(days=30)
    soon = [d for d in data if parse_date(d["expiry"]) <= limit]
    if not soon:
        print("No drugs expiring within 30 days.")
        return
    print("Drugs expiring within 30 days:")
    for d in sorted(soon, key=lambda x: x["expiry"]):
        print(f"- {d['name']} (expiry {d['expiry']})")

def remove_item(args):
    data = load_db()
    name = args.name.strip().lower()
    newdata = [d for d in data if d["name"].lower() != name]
    if len(newdata) == len(data):
        print("Item not found.")
        return
    save_db(newdata)
    print(f"Removed {args.name}")

def export_csv(args):
    data = load_db()
    if not data:
        print("No data.")
        return
    path = args.csv
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["name","expiry"])
        w.writeheader()
        for d in data:
            w.writerow(d)
    print(f"Exported {len(data)} drugs to {path}")

def main():
    p = argparse.ArgumentParser(description="Drug Expiry Tracker")
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("add", help="Add a drug with expiry")
    pa.add_argument("--name", required=True)
    pa.add_argument("--expiry", required=True, help="YYYY-MM-DD")
    pa.set_defaults(func=add_item)

    pl = sub.add_parser("list", help="List all drugs")
    pl.set_defaults(func=list_items)

    pe = sub.add_parser("expiring", help="List drugs expiring within 30 days")
    pe.set_defaults(func=expiring)

    pr = sub.add_parser("remove", help="Remove a drug")
    pr.add_argument("--name", required=True)
    pr.set_defaults(func=remove_item)

    px = sub.add_parser("export", help="Export to CSV")
    px.add_argument("--csv", required=True)
    px.set_defaults(func=export_csv)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
