"""
Advisor Agent — Co-Fundador + Especialista em YouTube
Orquestra os demais agentes e responde perguntas estratégicas via chat.
"""

import os, json, sys
from pathlib import Path
from datetime import date, timedelta
from typing import Generator
from dotenv import load_dotenv
import anthropic

BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")

SYSTEM_PROMPT = """You are the strategic co-founder and YouTube growth expert for "The Reality of Money by Rufino" — a personal finance YouTube Shorts channel targeting English-speaking audiences aged 25-40.

## YOUR ROLE
You are a business co-founder who understands the P&L, growth trajectory, and strategic decisions, AND a deep YouTube expert who knows the algorithm, monetization requirements, and optimization techniques. You have access to real channel data through your tools — always use them before answering data-related questions.

## BUSINESS CONTEXT
- Channel: "The Reality of Money by Rufino"
- Format: YouTube Shorts (~75 seconds, 3 videos/day, daily posting)
- Niche: Personal finance education in English
- Pipeline: Fully automated (ElevenLabs TTS → Pexels B-roll → MoviePy → YouTube API)
- Goal: YouTube Partner Program monetization + revenue diversification
- Owner: Everton, building this as a real business

## YOUTUBE PARTNER PROGRAM (YPP) REQUIREMENTS
- **Tier 1** (Fan Funding — Super Thanks, memberships): 500 subs + 3M Shorts views in 90 days
- **Tier 2** (Ad Revenue): 1,000 subs + 10M Shorts views in 90 days
- Also required: no strikes, 2FA enabled, AdSense linked, comply with advertiser policies

## YOUTUBE SHORTS ALGORITHM (ranked by impact)
1. **Watch rate** — % of video watched. The #1 signal. Target >85%
2. **Rewatch rate** — Loop-friendly endings dramatically boost distribution
3. **Shares** — Strongest engagement signal after watch rate
4. **Likes & Comments** — Secondary signals; comments especially signal community
5. **Posting consistency** — Daily posting gets algorithmic preference over sporadic
6. **First-frame CTR** — The cover frame and title determine if viewer swipes or stays

## CONTENT OPTIMIZATION TECHNIQUES
- **Hook (0-2 sec)**: Must create a "pattern interrupt" — challenge a belief, state a surprising number, ask a provocative question. The viewer decides in 0.5 seconds.
- **No filler**: Every sentence must earn the next. Never say "In this video..."
- **Loop design**: End on a question or unresolved tension — encourages rewatch
- **Title formulas that convert**:
  - [Common belief] + "is wrong" / "is lying to you"
  - "The [number] [thing] nobody told you about [topic]"
  - "Why [surprising claim]"
  - "[Specific number] that [emotional outcome]"
- **Optimal posting hours**: Analyze YOUR data — general best: 7-9am, 12-2pm, 7-9pm audience timezone
- **Finance niche advantage**: High CPM ($15-40 long form), strong affiliate programs, purchase-intent audience

## REVENUE STREAMS (priority order)
1. **YouTube Ad Revenue** — Shorts revenue share (lower CPM but compounds with volume)
2. **Affiliate Marketing** — Finance apps (investment platforms, budgeting tools, credit cards). Finance affiliates pay $50-300/conversion. Start before monetization.
3. **Sponsorships** — Finance brands pay $500-5,000/video at 100K+ subs
4. **Digital Products** — Course or ebook aligned with channel message (highest margin)
5. **Channel Memberships** — Available at 1,000 subscribers

## GROWTH PLAYBOOK BY STAGE
- **0-1K subs**: Consistency + niche clarity. Post every day. Test hooks aggressively.
- **1K-10K**: Double down on top 20% performing topics. Optimize watch rate. Build email list.
- **10K-100K**: Add affiliate CTAs, test sponsorship outreach, introduce long-form to boost watch hours.
- **100K+**: Brand deals, premium sponsorships, launch digital product.

## YOUR TOOLS — MANDATORY USAGE RULES
**ALWAYS call `run_performance_analyst` first** when the user asks ANYTHING about: views, performance, metrics, how the channel is doing, which videos are working, watch rate, engagement, top videos, or channel progress. This fetches live data from YouTube API. Do not answer performance questions from memory or old cached data.
After `run_performance_analyst` completes, call `read_channel_data` to get the full queue + the fresh report together.
Use `get_monetization_progress` when asked about YPP timeline or how far we are from monetization.
Use `run_script_writer` (with strategic_brief) to generate next week's scripts — only when explicitly asked or during Sunday orchestration.

## COMMUNICATION STYLE
- Direct and honest — you're a co-founder, not a cheerleader
- Data-driven — reference real numbers, not generic advice
- Actionable — every insight ends with a concrete recommendation
- Strategic — think 4-8 weeks ahead
- Language: respond in the same language the user writes (Portuguese or English)
- Concise — no padding, no "Great question!"
"""

TOOLS = [
    {
        "name": "read_channel_data",
        "description": "Read all channel data: queue history, published videos, performance metrics, and current week status.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_monetization_progress",
        "description": "Calculate current progress toward YouTube Partner Program (YPP) monetization tiers.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "run_performance_analyst",
        "description": "Fetch live YouTube metrics (views, likes, comments) for all published videos via the YouTube API. Call this FIRST whenever the user asks about performance, views, which videos are working, channel progress, or anything data-related. Do not skip this to save time — stale data leads to wrong recommendations.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "run_script_writer",
        "description": "Execute the Script Writer agent to generate 21 scripts for next week.",
        "input_schema": {
            "type": "object",
            "properties": {
                "strategic_brief": {
                    "type": "string",
                    "description": "Strategic direction for the scripts: which topics to focus on, hooks to use, topics to avoid, format recommendations.",
                }
            },
            "required": ["strategic_brief"],
        },
    },
]


# ── Tool implementations ───────────────────────────────────────────────────────

def _tool_read_channel_data() -> str:
    queue_dir = BASE_DIR / "queue"
    today = date.today()
    result = {"weeks": [], "totals": {"done": 0, "pending": 0, "error": 0, "total_videos": 0}}

    for i in range(6):
        check = today - timedelta(weeks=i)
        iso_year, iso_week, _ = check.isocalendar()
        qf = queue_dir / f"{iso_year}_W{iso_week:02d}.json"
        if not qf.exists():
            continue
        entries = json.loads(qf.read_text(encoding="utf-8"))
        week_data = {
            "week": iso_week, "year": iso_year, "file": qf.name,
            "entries": []
        }
        for e in entries:
            status = e.get("status", "pending")
            result["totals"][status] = result["totals"].get(status, 0) + 1
            result["totals"]["total_videos"] += 1
            week_data["entries"].append({
                "slug":             e.get("slug"),
                "date":             e.get("date"),
                "slot":             e.get("slot", "-"),
                "title":            e.get("title", ""),
                "status":           status,
                "publish_hour_brt": e.get("publish_hour_brt"),
                "views":            e.get("metrics", {}).get("views", 0) if e.get("metrics") else 0,
                "likes":            e.get("metrics", {}).get("likes", 0) if e.get("metrics") else 0,
                "youtube_url":      e.get("youtube_url", ""),
            })
        result["weeks"].append(week_data)

    # Performance report
    report_file = Path(__file__).parent / "data" / "performance_report.json"
    if report_file.exists():
        report = json.loads(report_file.read_text(encoding="utf-8"))
        result["performance_report"] = {
            "best_hours":      report.get("best_hours", []),
            "avg_views":       report.get("avg_views", 0),
            "videos_analyzed": report.get("videos_analyzed", 0),
            "top_videos":      report.get("top_videos", [])[:3],
            "generated_at":    report.get("generated_at"),
        }

    return json.dumps(result, ensure_ascii=False, indent=2)


def _tool_get_monetization_progress() -> str:
    """Calcula progresso em direção ao YPP via dados locais."""
    queue_dir = BASE_DIR / "queue"
    today = date.today()

    done_videos = []
    for i in range(13):  # últimas 13 semanas (~90 dias)
        check = today - timedelta(weeks=i)
        iso_year, iso_week, _ = check.isocalendar()
        qf = queue_dir / f"{iso_year}_W{iso_week:02d}.json"
        if not qf.exists():
            continue
        for e in json.loads(qf.read_text(encoding="utf-8")):
            if e.get("status") == "done":
                views = e.get("metrics", {}).get("views", 0) if e.get("metrics") else 0
                done_videos.append({
                    "date": e.get("date"), "title": e.get("title"), "views": views
                })

    total_views_90d = sum(v["views"] for v in done_videos)
    total_published = len(done_videos)

    # Projeção: média de views por vídeo × vídeos restantes para atingir 10M
    avg_views = total_views_90d / total_published if total_published else 0
    videos_at_3_per_day = 3 * 90  # 270 vídeos em 90 dias
    projected_90d = avg_views * videos_at_3_per_day if avg_views else 0

    result = {
        "current": {
            "videos_published":       total_published,
            "total_views_in_data":    total_views_90d,
            "avg_views_per_video":    round(avg_views, 1),
            "note":                   "Views may be 0 if metrics haven't been refreshed yet",
        },
        "ypp_targets": {
            "tier1_shorts_views":  3_000_000,
            "tier2_shorts_views":  10_000_000,
            "tier1_subscribers":   500,
            "tier2_subscribers":   1_000,
            "window_days":         90,
        },
        "projection_at_3_videos_per_day": {
            "estimated_views_90d": round(projected_90d),
            "tier1_achievable":    projected_90d >= 3_000_000,
            "tier2_achievable":    projected_90d >= 10_000_000,
            "note":                "Based on current avg views. Will improve as channel grows.",
        },
        "recommendation": (
            "Refresh metrics via webapp (Metricas button) to get real view counts from YouTube API."
            if total_views_90d == 0
            else f"On track projection: {round(projected_90d):,} views in 90 days at current avg."
        )
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def _tool_run_performance_analyst() -> str:
    sys.path.insert(0, str(BASE_DIR))
    from agents import performance_analyst
    try:
        report = performance_analyst.run()
        return json.dumps({
            "status":      "success",
            "best_hours":  report.get("best_hours"),
            "avg_views":   report.get("avg_views"),
            "top_videos":  report.get("top_videos", [])[:3],
            "analyzed":    report.get("videos_analyzed"),
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


def _tool_run_script_writer(strategic_brief: str) -> str:
    sys.path.insert(0, str(BASE_DIR))
    from agents import script_writer
    try:
        # Salva o brief para o script_writer usar
        brief_file = Path(__file__).parent / "data" / "strategic_brief.txt"
        brief_file.parent.mkdir(exist_ok=True)
        brief_file.write_text(strategic_brief, encoding="utf-8")

        queue_file = script_writer.run()
        return json.dumps({
            "status": "success",
            "queue_file": queue_file.name if queue_file else None,
            "message": "21 scripts generated and saved to queue.",
        })
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


def _execute_tool(name: str, inputs: dict) -> str:
    if name == "read_channel_data":
        return _tool_read_channel_data()
    if name == "get_monetization_progress":
        return _tool_get_monetization_progress()
    if name == "run_performance_analyst":
        return _tool_run_performance_analyst()
    if name == "run_script_writer":
        return _tool_run_script_writer(inputs.get("strategic_brief", ""))
    return json.dumps({"error": f"Unknown tool: {name}"})


# ── Chat (streaming) ───────────────────────────────────────────────────────────

def chat_stream(message: str, history: list) -> Generator[str, None, None]:
    """
    Gerador que faz streaming da resposta do Advisor.
    Yields texto incrementalmente para SSE.
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

    messages = []
    for h in history:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": message})

    # Agentic loop: Claude pode chamar ferramentas antes de responder
    while True:
        with client.messages.stream(
            model="claude-opus-4-7",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        ) as stream:
            full_text   = ""
            tool_uses   = []
            stop_reason = None

            for event in stream:
                if hasattr(event, "type"):
                    if event.type == "content_block_delta":
                        delta = event.delta
                        if hasattr(delta, "text"):
                            full_text += delta.text
                            yield delta.text
                    elif event.type == "message_delta":
                        if hasattr(event.delta, "stop_reason"):
                            stop_reason = event.delta.stop_reason

            # Captura tool_use blocks
            final_msg = stream.get_final_message()
            for block in final_msg.content:
                if block.type == "tool_use":
                    tool_uses.append(block)

        if not tool_uses:
            break  # Resposta final — sem ferramentas

        # Executa as ferramentas e continua o loop
        messages.append({"role": "assistant", "content": final_msg.content})
        tool_results = []
        for tu in tool_uses:
            yield f"\n\n*[Consultando {tu.name}...]*\n\n"
            result = _execute_tool(tu.name, tu.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tu.id,
                "content": result,
            })
        messages.append({"role": "user", "content": tool_results})


# ── Orchestration (autônoma, semanal) ─────────────────────────────────────────

def orchestrate_weekly() -> dict:
    """
    Orquestração autônoma semanal:
    1. Lê dados do canal
    2. Roda Performance Analyst
    3. Define estratégia
    4. Instrui Script Writer
    5. Retorna relatório
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

    prompt = """It's Sunday — time to generate next week's content strategy and scripts.

Follow this sequence:
1. Call read_channel_data to understand current performance
2. Call run_performance_analyst to get fresh metrics
3. Analyze what's working: best topics, best hours, watch rate patterns
4. Call run_script_writer with a strategic_brief that includes:
   - Which topics to focus on this week and why
   - Which topics to avoid (overused, low performance)
   - Hook style recommendations based on what's converting
   - Any specific angles or formats to test
5. After all tools complete, give a concise weekly strategy report

Be specific and data-driven. Reference actual video titles and metrics."""

    messages = [{"role": "user", "content": prompt}]
    report   = {"steps": [], "strategy": ""}

    while True:
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=8192,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        text_blocks = [b.text for b in response.content if hasattr(b, "text") and b.text]
        tool_uses   = [b for b in response.content if b.type == "tool_use"]

        if text_blocks:
            report["strategy"] = "\n".join(text_blocks)

        if not tool_uses:
            break

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for tu in tool_uses:
            print(f"  [Advisor] Executando: {tu.name}")
            report["steps"].append(tu.name)
            result = _execute_tool(tu.name, tu.input)
            tool_results.append({
                "type":        "tool_result",
                "tool_use_id": tu.id,
                "content":     result,
            })
        messages.append({"role": "user", "content": tool_results})

    return report


if __name__ == "__main__":
    # Teste rápido de chat
    print("Advisor Agent — teste de chat")
    print("=" * 40)
    for chunk in chat_stream("Como estamos indo? Qual é nossa situação atual?", []):
        print(chunk, end="", flush=True)
    print()
