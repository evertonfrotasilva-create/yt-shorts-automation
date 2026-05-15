"""
Pipeline completo — "Why Your Brain Is Wired To Quit On Money"
Etapa 1: narração edge-tts
Etapa 2: 16 clipes stock Pexels
"""
import asyncio, os, json, requests, time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

OUTPUT = Path(os.getenv("OUTPUT_DIR", Path(__file__).parent / "outputs")) / "wired_to_quit"
OUTPUT.mkdir(parents=True, exist_ok=True)

PEXELS_KEY = os.getenv("PEXELS_API_KEY", "")

# ── NARRAÇÃO ──────────────────────────────────────────────────────────────────

NARRATION = """Your brain is wired to make you broke. And willpower won't fix it.

Here's the neuroscience of why you quit on money — and how to beat it.

Your brain runs on two systems. One screams for the reward right now. The other plans for later. The loud one almost always wins.

That's why saving feels like pain. Scientists call it present bias — your brain literally discounts the future. Brain scans show it treats future you like a total stranger.

So every payday becomes a negotiation. And the stranger — future you — keeps losing.

The fix isn't more discipline. It's removing the decision. Automate the transfer the second you get paid. No willpower. No debate.

Here's the twist: people who build wealth aren't stronger. They just built a system their lazy brain can't argue with.

Still running on willpower? Watch again — then go automate it."""

# ── SHOTLIST (16 takes) ───────────────────────────────────────────────────────

SHOTS = [
    ("01_hook_brain",          "glowing brain technology dark cinematic"),
    ("02_promise_money",       "brain mri scan money dollar signs dark"),
    ("03_two_systems",         "two sides split light dark abstract brain"),
    ("04_reward_now",          "shopping impulsive spending money coins explosion"),
    ("05_plans_later",         "money tree growing savings dark background"),
    ("06_saving_pain",         "hand holding coin hesitant saving jar dark"),
    ("07_present_bias",        "timeline future past abstract neon dark"),
    ("08_future_stranger",     "two silhouettes glass separation dark cinematic"),
    ("09_payday_negotiation",  "paycheck money tug of war conflict dark"),
    ("10_stranger_losing",     "empty piggy bank broken dark sad cinematic"),
    ("11_not_discipline",      "thread breaking willpower fragile dark"),
    ("12_remove_decision",     "switch turning on gears mechanism dark gold"),
    ("13_automate_transfer",   "smartphone banking transfer money automatic dark"),
    ("14_twist_wealth",        "confident silhouette money growing success dark"),
    ("15_system_brain",        "gears machine coins compounding dark gold"),
    ("16_cta_loop",            "organized brain technology calm dark loop"),
]


def download_pexels_clip(query: str, filename: str) -> dict:
    out_path = OUTPUT / f"{filename}.mp4"
    if out_path.exists():
        return {"file": str(out_path), "cached": True}

    r = requests.get(
        "https://api.pexels.com/videos/search",
        headers={"Authorization": PEXELS_KEY},
        params={"query": query, "per_page": 5, "orientation": "portrait"},
        timeout=15,
    )
    r.raise_for_status()
    videos = r.json().get("videos", [])
    if not videos:
        return {"file": None, "error": f"Sem resultado: {query}"}

    video = videos[0]
    files = video.get("video_files", [])
    vertical = [f for f in files if f.get("width", 0) < f.get("height", 1)]
    best = max(vertical or files, key=lambda f: f.get("height", 0))

    with requests.get(best["link"], stream=True, timeout=60) as resp:
        resp.raise_for_status()
        out_path.write_bytes(resp.content)

    return {
        "file": str(out_path),
        "resolution": f"{best.get('width')}x{best.get('height')}",
        "duration": video.get("duration"),
    }


async def generate_narration():
    out = OUTPUT / "narration.mp3"
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY", "")

    if elevenlabs_key and elevenlabs_key.startswith("sk_"):
        # ElevenLabs — voz humana (plano Starter+)
        from elevenlabs.client import ElevenLabs
        voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        client = ElevenLabs(api_key=elevenlabs_key)
        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            text=NARRATION,
            model_id="eleven_turbo_v2",
            output_format="mp3_44100_128",
        )
        with open(out, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        print("  Engine: ElevenLabs (voz humana)")
    else:
        # edge-tts — fallback gratuito
        import edge_tts
        comm = edge_tts.Communicate(NARRATION, "en-US-AriaNeural")
        await comm.save(str(out))
        print("  Engine: edge-tts (fallback gratuito)")

    return out


# ── EXECUÇÃO ──────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("PIPELINE — Why Your Brain Is Wired To Quit On Money")
    print("=" * 55)

    # Etapa 1 — narração
    print("\n[1/2] Gerando narração (edge-tts)...")
    mp3 = asyncio.run(generate_narration())
    size_kb = mp3.stat().st_size // 1024
    words = len(NARRATION.split())
    print(f"  OK — {mp3.name} ({size_kb} KB | ~{round(words/2.8)}s estimado)")

    # Etapa 2 — clipes
    print(f"\n[2/2] Baixando {len(SHOTS)} clipes do Pexels...")
    results = []
    for i, (fname, query) in enumerate(SHOTS, 1):
        try:
            r = download_pexels_clip(query, fname)
            cached = " [cache]" if r.get("cached") else ""
            res = r.get("resolution", "?")
            dur = r.get("duration", "?")
            print(f"  [{i:02d}/{len(SHOTS)}] {fname}{cached} — {res} {dur}s")
            results.append({"take": i, "file": r["file"], "ok": True})
        except Exception as e:
            print(f"  [{i:02d}/{len(SHOTS)}] ERRO {fname}: {e}")
            results.append({"take": i, "ok": False, "error": str(e)})
        time.sleep(0.3)  # respeita rate limit Pexels

    # Salva manifesto
    manifest = {
        "video": "Why Your Brain Is Wired To Quit On Money",
        "narration": str(mp3),
        "clips": results,
        "output_dir": str(OUTPUT),
    }
    manifest_path = OUTPUT / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    # Resumo
    ok = sum(1 for r in results if r["ok"])
    print(f"\n{'=' * 55}")
    print(f"CONCLUÍDO")
    print(f"  Narração : {mp3.name}")
    print(f"  Clipes   : {ok}/{len(SHOTS)} baixados")
    print(f"  Pasta    : {OUTPUT}")
    print(f"  Manifesto: {manifest_path.name}")
    print(f"{'=' * 55}")
    print("\nPROXIMO PASSO:")
    print("  Abra a pasta outputs/wired_to_quit/ no Explorer")
    print("  Importe narration.mp3 + os 16 clipes no CapCut")
    print("  Monte seguindo o roteiro e o shotlist gerado")


if __name__ == "__main__":
    main()
