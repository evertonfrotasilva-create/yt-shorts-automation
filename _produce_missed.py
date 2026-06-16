"""
Produz e sobe vídeos de datas passadas que ficaram como pending.
Os vídeos são agendados com publishAt = agora + 10 min (clamp automático).

Uso:
  python _produce_missed.py 2026-06-02 2026-06-03
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Importa a lógica de produção do daily_auto
from daily_auto import produce_entry, find_today_entries, QUEUE_DIR
import types

# Args falsos equivalentes a rodar sem flags
fake_args = types.SimpleNamespace(
    dry_run=False,
    skip_upload=False,
    force=False,
)

dates_to_produce = sys.argv[1:] if len(sys.argv) > 1 else []
if not dates_to_produce:
    print("Uso: python _produce_missed.py 2026-06-02 2026-06-03")
    sys.exit(1)

success = 0
total   = 0

for week_file in sorted(QUEUE_DIR.glob("*.json")):
    if "bak" in week_file.name:
        continue
    entries = json.loads(week_file.read_text(encoding="utf-8"))
    for entry in entries:
        if entry.get("date") not in dates_to_produce:
            continue
        if entry.get("status") not in ("pending", "error"):
            print(f"[SKIP] {entry['slug']} — status={entry['status']}")
            continue
        total += 1
        print(f"\n{'='*60}")
        print(f"Produzindo: {entry['slug']} ({entry['date']} slot={entry['slot']})")
        print(f"Titulo: {entry.get('title','')}")
        print('='*60)
        # Re-lê entries frescos antes de cada vídeo
        fresh_entries = json.loads(week_file.read_text(encoding="utf-8"))
        ok = produce_entry(week_file, fresh_entries, entry, fake_args)
        if ok:
            success += 1
            print(f"OK: {entry['slug']}")
        else:
            print(f"FALHOU: {entry['slug']}")

print(f"\nCONCLUIDO: {success}/{total} produzidos")
