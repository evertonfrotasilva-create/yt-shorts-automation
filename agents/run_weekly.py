"""
Orquestrador semanal — controlado pelo Advisor Agent.
Roda todo domingo para gerar a fila da próxima semana com estratégia baseada em dados.

Uso:
  python agents/run_weekly.py               # fluxo completo via Advisor
  python agents/run_weekly.py --dry-run     # sem chamadas de API
  python agents/run_weekly.py --simple      # sem Advisor (Performance Analyst + Script Writer direto)
"""

import sys, argparse, json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))


def run_simple(dry_run: bool = False):
    """Fluxo direto sem Advisor — útil para debug ou primeiro uso."""
    from agents import performance_analyst, script_writer

    print("\n[1/2] Performance Analyst")
    report = performance_analyst.run() if not dry_run else {"best_hours": [8, 14, 20]}

    print("\n[2/2] Script Writer")
    queue_file = script_writer.run(dry_run=dry_run)
    return queue_file


def run_with_advisor():
    """Fluxo orquestrado pelo Advisor — usa dados e estratégia para gerar roteiros melhores."""
    from agents import advisor

    print("\n[Advisor] Iniciando orquestração semanal...")
    report = advisor.orchestrate_weekly()

    if report.get("strategy"):
        print("\n" + "─" * 60)
        print("ESTRATEGIA DA SEMANA:")
        print(report["strategy"])
        print("─" * 60)

    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--simple",  action="store_true",
                        help="Pula o Advisor, roda Performance Analyst + Script Writer diretamente")
    args = parser.parse_args()

    print("=" * 60)
    print("AGENTES SEMANAIS — The Reality of Money by Rufino")
    print("=" * 60)

    if args.dry_run:
        print("\nDRY-RUN: validando estrutura sem chamar APIs...")
        run_simple(dry_run=True)
        print("\nDRY-RUN CONCLUIDO — estrutura OK")
        return

    if args.simple:
        queue_file = run_simple()
        print(f"\nCONCLUIDO — Fila: {queue_file.name if queue_file else 'N/A'}")
    else:
        report = run_with_advisor()
        steps = report.get("steps", [])
        print(f"\nCONCLUIDO — Etapas executadas: {', '.join(steps) if steps else 'nenhuma'}")

    print("\nProximos passos:")
    print("  1. Revisar os roteiros no webapp (semana seguinte)")
    print("  2. Ajustar se necessario")
    print("  3. Os videos serao produzidos automaticamente pelo pipeline diario")
    print("=" * 60)


if __name__ == "__main__":
    main()
