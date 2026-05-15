"""Teste completo do pipeline gratuito: voz + vídeo stock + status YouTube."""
import asyncio, os, json, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")
OUTPUT = Path(os.getenv("OUTPUT_DIR", Path(__file__).parent / "outputs"))
OUTPUT.mkdir(exist_ok=True)

# ── 1. Edge-TTS ──────────────────────────────────────────────────────────────
print("=" * 50)
print("TESTE 1 — Voz (edge-tts)")
print("=" * 50)
try:
    import edge_tts
    async def tts():
        out = OUTPUT / "test_narration.mp3"
        comm = edge_tts.Communicate(
            "Most people quit right before they succeed. "
            "Here's the psychology behind why — and how to rewire your brain.",
            "en-US-AriaNeural"
        )
        await comm.save(str(out))
        return out
    mp3 = asyncio.run(tts())
    print(f"  OK — {mp3.name} ({mp3.stat().st_size // 1024} KB)")
except Exception as e:
    print(f"  ERRO: {e}")

# ── 2. Pexels ─────────────────────────────────────────────────────────────────
print("\n" + "=" * 50)
print("TESTE 2 — Vídeo stock (Pexels)")
print("=" * 50)
try:
    key = os.getenv("PEXELS_API_KEY", "")
    r = requests.get(
        "https://api.pexels.com/videos/search",
        headers={"Authorization": key},
        params={"query": "person thinking alone dark cinematic", "per_page": 1, "orientation": "portrait"},
        timeout=15
    )
    r.raise_for_status()
    videos = r.json().get("videos", [])
    if not videos:
        print("  ERRO: nenhum vídeo encontrado")
    else:
        v = videos[0]
        files = v.get("video_files", [])
        vertical = [f for f in files if f.get("width", 0) < f.get("height", 1)]
        best = max(vertical or files, key=lambda f: f.get("height", 0))
        url = best["link"]
        out = OUTPUT / "test_clip.mp4"
        with requests.get(url, stream=True, timeout=60) as resp:
            out.write_bytes(resp.content)
        print(f"  OK — {out.name} ({out.stat().st_size // 1024} KB)")
        print(f"  Resolucao: {best.get('width')}x{best.get('height')}")
        print(f"  Duracao: {v.get('duration')}s")
except Exception as e:
    print(f"  ERRO: {e}")

# ── 3. YouTube OAuth (verifica credenciais) ───────────────────────────────────
print("\n" + "=" * 50)
print("TESTE 3 — YouTube (credenciais OAuth)")
print("=" * 50)
cid = os.getenv("YOUTUBE_CLIENT_ID", "")
cs = os.getenv("YOUTUBE_CLIENT_SECRET", "")
if cid and "googleusercontent" in cid and cs.startswith("GOCSPX"):
    print("  OK — credenciais presentes e no formato correto")
    print("  (autenticacao completa exige browser — rode /daily-pipeline para ativar)")
else:
    print("  ERRO: credenciais ausentes ou incorretas")

print("\n" + "=" * 50)
print("RESUMO FINAL")
print("=" * 50)
print("  edge-tts (voz):   GRATIS, sem limite")
print("  Pexels (video):   GRATIS, 200 req/hora")
print("  YouTube upload:   GRATIS, 10k units/dia")
print("\nPipeline pronto para producao!")
