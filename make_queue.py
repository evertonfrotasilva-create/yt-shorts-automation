"""
Cria o arquivo de fila da semana especificada (ou da semana atual).

Uso:
  python make_queue.py            # cria fila da semana atual
  python make_queue.py --next     # cria fila da proxima semana
  python make_queue.py --week 21  # cria fila da semana 21 do ano atual
"""

import json, argparse
from pathlib import Path
from datetime import date, timedelta

QUEUE_DIR = Path(__file__).parent / "queue"
QUEUE_DIR.mkdir(exist_ok=True)

DAY_NAMES = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
DAY_PT    = ["Segunda","Terca","Quarta","Quinta","Sexta","Sabado","Domingo"]
DAY_SLUGS = ["mon","tue","wed","thu","fri","sat","sun"]


def monday_of_week(year: int, week: int) -> date:
    """Retorna a segunda-feira da semana ISO especificada."""
    jan4 = date(year, 1, 4)
    monday = jan4 - timedelta(days=jan4.weekday())
    return monday + timedelta(weeks=week - 1)


def create_queue(year: int, week: int, overwrite: bool = False) -> Path:
    out_file = QUEUE_DIR / f"{year}_W{week:02d}.json"

    if out_file.exists() and not overwrite:
        print(f"Arquivo ja existe: {out_file}")
        print("Use --overwrite para substituir.")
        return out_file

    mon = monday_of_week(year, week)
    entries = []
    for i in range(7):
        day_date = mon + timedelta(days=i)
        entries.append({
            "day":              DAY_NAMES[i],
            "day_pt":           DAY_PT[i],
            "date":             day_date.isoformat(),
            "slug":             f"video_{DAY_SLUGS[i]}_{day_date.strftime('%m%d')}",
            "narration":        "",
            "num_takes":        12,
            "duration":         75,
            "voice":            "rachel",
            "title":            "",
            "description":      "",
            "tags":             [],
            "publish_hour_brt": 18,
            "status":           "pending",
            "error_msg":        "",
        })

    out_file.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Criado: {out_file}  ({len(entries)} entradas, {mon} a {mon + timedelta(days=6)})")
    print()
    print("Proximos passos:")
    print("  1. No Cowork: /weekly-trends -> pega 7 angulos")
    print("  2. No Cowork: /daily-pipeline angulo:\"...\" x 7 -> pega 7 narracoes")
    print("  3. Cole cada narracao no campo 'narration' do JSON")
    print("  4. Preencha title, description e tags para cada dia")
    print("  5. A automacao diaria faz o resto")
    return out_file


def main():
    parser = argparse.ArgumentParser(description="Cria arquivo de fila semanal")
    parser.add_argument("--next",      action="store_true", help="Cria fila da proxima semana")
    parser.add_argument("--week",      type=int,            help="Numero da semana ISO (1-53)")
    parser.add_argument("--year",      type=int,            help="Ano (padrao: ano atual)")
    parser.add_argument("--overwrite", action="store_true", help="Sobrescreve se ja existir")
    args = parser.parse_args()

    today = date.today()
    iso_year, iso_week, _ = today.isocalendar()

    if args.next:
        target = today + timedelta(weeks=1)
        iso_year, iso_week, _ = target.isocalendar()
    elif args.week:
        iso_week = args.week
        iso_year = args.year or iso_year

    create_queue(iso_year, iso_week, overwrite=args.overwrite)


if __name__ == "__main__":
    main()
