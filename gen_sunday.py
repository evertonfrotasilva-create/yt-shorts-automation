"""Gera 3 roteiros para domingo 2026-05-24 e adiciona à fila W21."""
import os, json
from pathlib import Path
from dotenv import load_dotenv
import anthropic

load_dotenv(Path(__file__).parent / ".env")
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

past_titles = [
    "The 50/30/20 rule is lying to you",
    "Why rich people don't save money",
    "The one number that predicts your wealth",
    "Stop waiting for a raise — do this instead",
    "The $9,000 Tax Refund Lie Nobody Talks About",
    "The $127,000 Mistake of Paying Off Your Mortgage Early",
    "Why 'Buy the Dip' Is Killing Your Portfolio",
    "Why your budget fails (and what works instead)",
    "The $62,000 Car Lease Trap That Looks Affordable",
    "The 3-Account System That Replaced My Budget",
    "Why Your 'Safe' Savings Account Lost You $4,300 Last Year",
    "The $5/day rule that builds wealth quietly",
    "The $250,000 Roth IRA Trick Most People Skip",
    "Why 'Following Your Passion' Made You Broke",
    "The 4% Rule Is Wrong: Here's the Real Number",
    "You don't have a money problem. You have a decision problem.",
]

tool_def = {
    "name": "generate_sunday_scripts",
    "description": "Output 3 scripts for Sunday",
    "input_schema": {
        "type": "object",
        "properties": {
            "entries": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "slot":             {"type": "string", "enum": ["a", "b", "c"]},
                        "title":            {"type": "string", "description": "Compelling title max 80 chars"},
                        "narration":        {"type": "string", "description": "180-210 words exactly"},
                        "description":      {"type": "string", "description": "YouTube description max 400 chars + hashtags"},
                        "tags":             {"type": "array", "items": {"type": "string"}},
                        "publish_hour_brt": {"type": "integer"},
                    },
                    "required": ["slot", "title", "narration", "description", "tags", "publish_hour_brt"],
                },
                "minItems": 3,
                "maxItems": 3,
            }
        },
        "required": ["entries"],
    },
}

past_block = "\n".join(f"- {t}" for t in past_titles)

prompt = f"""You are a YouTube Shorts script writer for "The Reality of Money by Rufino".

CHANNEL BRIEF:
- Niche: Personal finance education in English
- Format: YouTube Shorts (~75 seconds, conversational)
- Tone: Calm, insightful, slightly provocative — like a trusted mentor
- Target audience: 25-40 year olds who feel stuck financially
- Style rules:
  * Open with a hook that challenges a common belief (first 3 seconds are critical)
  * No fluff — every sentence must earn its place
  * Use specific numbers and data when possible
  * End with: "If this changed how you see money — subscribe. New video every day."
  * Never say "In this video" — start in medias res
  * Avoid complex financial jargon
  * Narration length: 180-210 words exactly

PERFORMANCE DATA:
- Best posting hours (BRT): [11, 18, 21]
- Assign hour 11 to slot "a", 18 to slot "b", 21 to slot "c"

TOPICS ALREADY COVERED THIS WEEK — DO NOT REPEAT:
{past_block}

Generate 3 completely different YouTube Shorts scripts for Sunday 2026-05-24.
Each must be a fresh personal finance angle not covered above.
Call generate_sunday_scripts with all 3 scripts."""

print("Chamando Claude API (pode levar 1-2 min)...")
response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=8000,
    tools=[tool_def],
    tool_choice={"type": "tool", "name": "generate_sunday_scripts"},
    messages=[{"role": "user", "content": prompt}],
)

tool_block = next(b for b in response.content if b.type == "tool_use")
entries = tool_block.input["entries"]
print(f"Gerados {len(entries)} roteiros")

q_path = Path(__file__).parent / "queue" / "2026_W21.json"
queue = json.loads(q_path.read_text(encoding="utf-8"))

for e in entries:
    wc = len(e["narration"].split())
    print(f"  Slot {e['slot']}: {e['title'][:65]} ({wc} palavras, {e['publish_hour_brt']}h BRT)")
    queue.append({
        "day":              "sunday",
        "day_pt":           "Domingo",
        "date":             "2026-05-24",
        "slot":             e["slot"],
        "slug":             f"video_sun_0524_{e['slot']}",
        "narration":        e["narration"],
        "num_takes":        12,
        "duration":         75,
        "voice":            "rachel",
        "title":            e["title"],
        "description":      e["description"],
        "tags":             e.get("tags", []),
        "publish_hour_brt": e["publish_hour_brt"],
        "status":           "pending",
        "error_msg":        "",
    })

q_path.write_text(json.dumps(queue, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Fila atualizada: {q_path.name} ({len(queue)} entradas)")
