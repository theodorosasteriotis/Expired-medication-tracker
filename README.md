# Drug Expiry Tracker (Python CLI)

A tiny, dependency‑free **command‑line tool** to track medicine expiry dates. Add items once; list all, see what's **expired** or **expiring soon**, and export to CSV.

## Features
- Add medicines with name, strength, form, batch, expiry date, and location
- Show **expired** items and those **expiring soon** (configurable window, default 30 days)
- Search by name
- Export to CSV for Excel/Sheets
- Pure Python (standard library only)

## Quick start
```bash
python expiry.py add --name "Ibuprofen" --strength "400 mg" --form "tablet" --batch "B123" --expiry 2026-12-31 --location "Shelf B"
python expiry.py list
python expiry.py soon              # expiring in <= 30 days
python expiry.py soon --days 60    # expiring in <= 60 days
python expiry.py expired
python expiry.py find --query "ibu"
python expiry.py export --csv "expiry_export.csv"
```

> Data is saved to `drugs.json` in the same folder. Dates use `YYYY-MM-DD`.

## Fields
- **name**: e.g., "Ibuprofen"
- **strength**: e.g., "400 mg"
- **form**: e.g., "tablet", "capsule", "syrup"
- **batch** (optional): batch/lot number
- **expiry**: `YYYY-MM-DD`
- **location** (optional): where it is stored (e.g., "Shelf B")

## License
MIT
