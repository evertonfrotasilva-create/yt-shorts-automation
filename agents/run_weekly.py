"""
Orquestrador semanal de agentes.
Roda todo domingo para gerar a fila da próxima semana.

Uso:
  python agents/run_weekly.py               # fluxo completo
  python agents/run_weekly.py --dry-run     # sem chamadas de API
  python agents/run_weekly.py --skip-analyst  # pula coleta de métricas
"""

import sys, argparse
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from agents import performance_analyst, script_writer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run",       action="store_true")
    parser.add_argument("--skip-analyst",  action="store_true",
                        help="Usa performance_report.json existente sem buscar novas métricas")
    args = parser.parse_args()

    print("=" * 60)
    print("AGENTES SEMANAIS — The Reality of Money by Rufino")
    print("=" * 60)

    # Passo 1: Performance Analyst
    if not args.skip_analyst and not args.dry_run:
        print("\n[1/2] Performance Analyst")
        report = performance_analyst.run()
    else:
        print("\n[1/2] Performance Analyst — pulado")
        data_file = Path(__file__).parent / "data" / "performance_report.json"
        if data_file.exists():
            import json
            report = json.loads(data_file.read_text(encoding="utf-8"))
            print(f"  Usando relatório existente: {data_file.name}")
        else:
            report = {"best_hours": [8, 14, 20], "top_videos": [], "avg_views": 0, "videos": []}
            print("  Sem relatório existente — usando horários padrão")

    # Passo 2: Script Writer
    print("\n[2/2] Script Writer")
    queue_file = script_writer.run(dry_run=args.dry_run)

    print("\n" + "=" * 60)
    if args.dry_run:
        print("DRY-RUN CONCLUÍDO — nenhum arquivo modificado")
    else:
        print(f"CONCLUÍDO — Fila gerada: {queue_file.name if queue_file else 'N/A'}")
        print("Próximos passos:")
        print("  1. Revisar os roteiros no webapp")
        print("  2. Ajustar títulos/horários se necessário")
        print("  3. Clicar 'Produzir' nos cards")
    print("=" * 60)


if __name__ == "__main__":
    main()
