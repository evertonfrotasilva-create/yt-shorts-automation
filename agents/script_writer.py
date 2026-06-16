"""
Script Writer Agent
Usa Claude API para gerar 21 roteiros/semana (3 por dia),
com horários de publicação otimizados pelo Performance Analyst.
"""

import os, json, sys
from pathlib import Path
from datetime import date, timedelta
from dotenv import load_dotenv
import anthropic

BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR  = Path(__file__).parent / "data"
QUEUE_DIR = BASE_DIR / "queue"

DAYS_EN = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAYS_PT = ["Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado", "Domingo"]
SLUGS   = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
SLOTS   = ["a", "b", "c"]


def _next_week_dates() -> list[dict]:
    """Retorna os 7 dias da próxima semana com metadados."""
    today   = date.today()
    # próxima segunda-feira
    days_until_monday = (7 - today.weekday()) % 7 or 7
    next_monday = today + timedelta(days=days_until_monday)

    days = []
    for i in range(7):
        d = next_monday + timedelta(days=i)
        days.append({
            "day":    DAYS_EN[i],
            "day_pt": DAYS_PT[i],
            "slug":   SLUGS[i],
            "date":   d.isoformat(),
            "mmdd":   d.strftime("%m%d"),
        })
    return days


def _load_performance_report() -> dict:
    report_file = DATA_DIR / "performance_report.json"
    if report_file.exists():
        return json.loads(report_file.read_text(encoding="utf-8"))
    return {"best_hours": [8, 14, 20], "top_videos": [], "avg_views": 0, "videos": []}


def _load_past_titles(weeks_back: int = 6) -> list[str]:
    """Retorna títulos das últimas N semanas para evitar repetição."""
    today = date.today()
    titles = []
    for i in range(weeks_back):
        check = today - timedelta(weeks=i)
        iso_year, iso_week, _ = check.isocalendar()
        qf = QUEUE_DIR / f"{iso_year}_W{iso_week:02d}.json"
        if not qf.exists():
            continue
        for e in json.loads(qf.read_text(encoding="utf-8")):
            t = e.get("title", "").strip()
            if t:
                titles.append(t)
    return titles


def _build_prompt(report: dict, past_titles: list[str], week_dates: list[dict]) -> str:
    best_hours = report.get("best_hours", [8, 14, 20])
    top_videos = report.get("top_videos", [])
    avg_views  = report.get("avg_views", 0)

    top_section = ""
    if top_videos:
        top_section = "\n\nTop performing videos (use as reference for tone and topics):\n"
        for v in top_videos[:5]:
            top_section += f'- "{v["title"]}" — {v["views"]} views\n'

    past_section = ""
    if past_titles:
        past_section = "\n\nTopics already covered (do NOT repeat these):\n"
        for t in past_titles[-30:]:
            past_section += f"- {t}\n"

    week_info = f"Week of {week_dates[0]['date']} to {week_dates[6]['date']}"

    return f"""You are a YouTube Shorts script writer for the channel "Daily Manna".

CHANNEL BRIEF:
- Niche: Bible verse of the day with brief explanation (NIV translation)
- Tone: Warm, reverent, accessible — like a wise friend sharing God's word
- Target audience: English-speaking Christians and faith-seekers looking for daily spiritual nourishment
- Style rules:
  * Open with a PSYCHOLOGICAL HOOK (first 10-15 words) — NOT the verse itself
  * Hook types (vary them): surprising context ("Paul wrote this from prison"), emotional recognition
    ("If you've ever felt..."), counterintuitive truth ("God didn't say what most people think"),
    pattern interrupt ("Most people skip past this verse. They shouldn't.")
  * Hooks must be ETHICAL — create curiosity and emotional connection, never fear, false urgency, or
    misleading claims
  * Every word counts — 30 seconds total, ~65-75 words maximum
  * After the hook, deliver the verse with its reference naturally
  * Explanation must be practical and relatable, not preachy
  * End with a personal question that invites comment + "Subscribe for a verse every day"
  * Never say "In this video" — go straight to the hook
  * Use NIV translation exclusively

VIDEO STRUCTURE (30 seconds, 3 takes of ~10s each):
- Take 1 (~10s): Hook (2-3s) + verse with reference clearly stated (~8s).
  Example: "The night before he was crucified, Jesus said this — John 14 verse 27: Peace I leave with you..."
- Take 2 (~15s): Brief explanation — context, what it meant then, what it means now. One key insight only.
- Take 3 (~5s): Personal application question + "Subscribe for a verse every day."

ALL THREE SLOTS are the same format and length (30 seconds, ~65-75 words).
Each slot should feature a DIFFERENT verse and theme — no two videos on the same day should feel similar.

PERFORMANCE DATA:
- Best posting hours (BRT, highest to lowest engagement): {best_hours}
- Channel average views: {avg_views}{top_section}{past_section}

YOUR TASK:
Generate 21 original Bible verse scripts for {week_info}.
3 videos per day, 7 days. Each video must use a DIFFERENT verse and cover a DIFFERENT theme.

Distribute publish hours across the day using the best performing slots: {best_hours}
Assign hour {best_hours[0]}h to slot "a" (morning), {best_hours[1] if len(best_hours) > 1 else 14}h to slot "b" (afternoon), {best_hours[2] if len(best_hours) > 2 else 20}h to slot "c" (evening).

Verse themes to explore across the week (vary these — don't cluster similar themes on the same day):
- Strength and courage (Joshua 1:9, Isaiah 40:31, Philippians 4:13...)
- God's love and grace (John 3:16, Romans 8:38-39, Ephesians 2:8-9...)
- Peace and anxiety (Philippians 4:6-7, Isaiah 26:3, John 14:27...)
- Hope and perseverance (Romans 5:3-4, Jeremiah 29:11, Lamentations 3:22-23...)
- Forgiveness and redemption (1 John 1:9, Psalm 103:12, Romans 8:1...)
- Purpose and calling (Jeremiah 29:11, Ephesians 2:10, Proverbs 3:5-6...)
- Wisdom and guidance (James 1:5, Proverbs 3:5-6, Psalm 119:105...)
- Gratitude and joy (Philippians 4:4, 1 Thessalonians 5:18, Psalm 118:24...)
- Faith and trust (Hebrews 11:1, Proverbs 3:5, Matthew 17:20...)
- Prayer (Matthew 7:7, Philippians 4:6, 1 Thessalonians 5:17...)

Call the generate_weekly_queue tool with all 21 scripts."""


def _load_strategic_brief() -> str:
    brief_file = Path(__file__).parent / "data" / "strategic_brief.txt"
    if brief_file.exists():
        brief = brief_file.read_text(encoding="utf-8").strip()
        brief_file.unlink()  # usa uma vez e descarta
        return brief
    return ""


def run(dry_run: bool = False) -> Path:
    print("[Script Writer] Iniciando geração de roteiros...")

    report      = _load_performance_report()
    past_titles = _load_past_titles()
    week_dates  = _next_week_dates()
    best_hours  = report.get("best_hours", [8, 14, 20])

    print(f"  Semana alvo: {week_dates[0]['date']} a {week_dates[6]['date']}")
    print(f"  Horários de publicação: {best_hours}")
    print(f"  {len(past_titles)} títulos anteriores carregados para evitar repetição")

    if dry_run:
        print("  DRY-RUN: prompt montado, sem chamar a API")
        return None

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

    tool_def = {
        "name": "generate_weekly_queue",
        "description": "Output the complete 21-script weekly queue",
        "input_schema": {
            "type": "object",
            "properties": {
                "entries": {
                    "type": "array",
                    "description": "21 video entries, 3 per day for 7 days",
                    "items": {
                        "type": "object",
                        "properties": {
                            "day":              {"type": "string", "description": "e.g. monday"},
                            "slot":             {"type": "string", "enum": ["a", "b", "c"]},
                            "title":            {"type": "string", "description": "Compelling title, max 80 chars"},
                            "narration":        {"type": "string", "description": "Script text. All slots: 65-75 words (~30 seconds). Structure: verse + reference → brief explanation → personal question + CTA."},
                            "description":      {"type": "string", "description": "YouTube description, max 400 chars + hashtags"},
                            "tags":             {"type": "array", "items": {"type": "string"}, "description": "8-10 tags"},
                            "publish_hour_brt": {"type": "integer", "description": "Publishing hour in BRT timezone"},
                        },
                        "required": ["day", "slot", "title", "narration", "description", "tags", "publish_hour_brt"],
                    },
                    "minItems": 21,
                    "maxItems": 21,
                }
            },
            "required": ["entries"],
        },
    }

    strategic_brief = _load_strategic_brief()
    if strategic_brief:
        print(f"  Brief estrategico do Advisor carregado ({len(strategic_brief)} chars)")

    prompt = _build_prompt(report, past_titles, week_dates)
    if strategic_brief:
        prompt += f"\n\n## STRATEGIC DIRECTION FROM ADVISOR\n{strategic_brief}"

    print("  Chamando Claude API (pode levar 1-2 minutos)...")
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=16000,
        tools=[tool_def],
        tool_choice={"type": "tool", "name": "generate_weekly_queue"},
        messages=[{"role": "user", "content": prompt}],
    )

    # Extrai o tool_use block
    tool_block = next((b for b in response.content if b.type == "tool_use"), None)
    if not tool_block:
        raise RuntimeError("Claude não retornou tool_use — resposta inesperada")

    raw_entries = tool_block.input["entries"]
    print(f"  {len(raw_entries)} roteiros gerados")

    # Monta o JSON final da fila
    iso_year, iso_week, _ = (date.fromisoformat(week_dates[0]["date"])).isocalendar()
    queue_entries = []

    day_map = {d["day"]: d for d in week_dates}
    hour_by_slot = {"a": best_hours[0], "b": best_hours[1] if len(best_hours) > 1 else 14,
                    "c": best_hours[2] if len(best_hours) > 2 else 20}

    for e in raw_entries:
        day_info = day_map.get(e["day"])
        if not day_info:
            continue
        slot = e["slot"]
        slot_cfg = {"a": (30, 3), "b": (30, 3), "c": (30, 3)}.get(slot, (30, 3))
        queue_entries.append({
            "day":              e["day"],
            "day_pt":           day_info["day_pt"],
            "date":             day_info["date"],
            "slot":             slot,
            "slug":             f"video_{day_info['slug']}_{day_info['mmdd']}_{slot}",
            "narration":        e["narration"],
            "num_takes":        slot_cfg[1],
            "duration":         slot_cfg[0],
            "voice":            "rachel",
            "title":            e["title"],
            "description":      e["description"],
            "tags":             e.get("tags", []),
            "publish_hour_brt": e.get("publish_hour_brt", hour_by_slot.get(slot, 18)),
            "status":           "pending",
            "error_msg":        "",
        })

    # Ordena: segunda a domingo, slot a→b→c
    slot_order = {"a": 0, "b": 1, "c": 2}
    queue_entries.sort(key=lambda e: (DAYS_EN.index(e["day"]), slot_order.get(e["slot"], 0)))

    queue_file = QUEUE_DIR / f"{iso_year}_W{iso_week:02d}.json"
    if queue_file.exists():
        backup = queue_file.with_suffix(f".bak.json")
        backup.write_text(queue_file.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"  Backup criado: {backup.name}")

    queue_file.write_text(json.dumps(queue_entries, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Fila salva: {queue_file.name} ({len(queue_entries)} entradas)")

    return queue_file


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    run(dry_run=dry)
