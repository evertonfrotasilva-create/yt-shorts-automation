"""MCP server — TTS via ElevenLabs (plano Starter $5/mês).
Fallback automático para edge-tts se a API key não estiver configurada.
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(Path(__file__).parent / ".env")

mcp = FastMCP("tts-voiceover")

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", Path(__file__).parent / "outputs"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# Vozes ElevenLabs pré-selecionadas para Shorts educativos em inglês
ELEVENLABS_VOICES = {
    "rachel":  "21m00Tcm4TlvDq8ikWAM",  # feminino EUA — warm, natural (padrão)
    "adam":    "pNInz6obpgDQGcFmaJgB",  # masculino EUA — deep, authoritative
    "domi":    "AZnzlk1XvdvUeBnXmlld",  # feminino EUA — strong, confident
    "elli":    "MF3mGyEYCl7XYWbV9V6O",  # feminino EUA — emotional
    "josh":    "TxGEqnHWrfWFTfGW9XjX",  # masculino EUA — deep, conversational
    "arnold":  "VR6AewLTigWG4xSOukaG",  # masculino EUA — crisp, authoritative
    "default": "21m00Tcm4TlvDq8ikWAM",  # rachel
}

# Fallback edge-tts (grátis)
EDGE_VOICES = {
    "aria":    "en-US-AriaNeural",
    "guy":     "en-US-GuyNeural",
    "jenny":   "en-US-JennyNeural",
    "sonia":   "en-GB-SoniaNeural",
    "ryan":    "en-GB-RyanNeural",
    "default": "en-US-AriaNeural",
}


def _generate_elevenlabs(text: str, voice_id: str, out_path: Path) -> dict:
    from elevenlabs.client import ElevenLabs
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id="eleven_turbo_v2",
        output_format="mp3_44100_128",
    )
    with open(out_path, "wb") as f:
        for chunk in audio:
            f.write(chunk)
    return {"engine": "elevenlabs", "voice_id": voice_id}


async def _generate_edge(text: str, voice: str, out_path: Path) -> dict:
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(out_path))
    return {"engine": "edge-tts", "voice": voice}


@mcp.tool()
def generate_voiceover(
    text: str,
    voice: str = "rachel",
    filename: str = "",
) -> str:
    """
    Gera narração em MP3. Usa ElevenLabs se a API key estiver configurada,
    senão usa edge-tts (Microsoft, gratuito) como fallback.

    Args:
        text: Texto a narrar em inglês (máx ~2000 chars).
        voice: ElevenLabs: rachel, adam, domi, elli, josh, arnold
               edge-tts fallback: aria, guy, jenny, sonia, ryan
        filename: Nome do arquivo sem extensão. Usa timestamp se omitido.

    Returns:
        JSON com caminho do arquivo MP3, engine usada e duração estimada.
    """
    fname = filename or f"voiceover_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_path = OUTPUT_DIR / f"{fname}.mp3"

    words = len(text.split())
    estimated_s = round(words / 2.8)

    if ELEVENLABS_API_KEY and ELEVENLABS_API_KEY.startswith("sk_"):
        voice_id = ELEVENLABS_VOICES.get(voice.lower(), ELEVENLABS_VOICES["default"])
        meta = _generate_elevenlabs(text, voice_id, out_path)
    else:
        edge_voice = EDGE_VOICES.get(voice.lower(), EDGE_VOICES["default"])
        meta = asyncio.run(_generate_edge(text, edge_voice, out_path))

    return json.dumps({
        "success": True,
        "file": str(out_path),
        "estimated_duration_s": estimated_s,
        "words": words,
        **meta,
    })


@mcp.tool()
def list_voices() -> str:
    """Lista vozes disponíveis — ElevenLabs (pago) e edge-tts (gratuito)."""
    using_elevenlabs = bool(ELEVENLABS_API_KEY and ELEVENLABS_API_KEY.startswith("sk_"))
    return json.dumps({
        "active_engine": "elevenlabs" if using_elevenlabs else "edge-tts (fallback)",
        "elevenlabs_voices": [
            {"key": "rachel", "style": "Warm, natural — melhor para educativo"},
            {"key": "adam",   "style": "Deep, authoritative — bom para finanças"},
            {"key": "domi",   "style": "Strong, confident"},
            {"key": "elli",   "style": "Emotional, engaging"},
            {"key": "josh",   "style": "Deep, conversational"},
            {"key": "arnold", "style": "Crisp, authoritative"},
        ],
        "edge_tts_voices": [
            {"key": "aria",  "style": "Natural, warm (padrão)"},
            {"key": "guy",   "style": "Direct, confident"},
            {"key": "jenny", "style": "Friendly"},
            {"key": "sonia", "style": "British, premium"},
            {"key": "ryan",  "style": "British, warm"},
        ],
    })


if __name__ == "__main__":
    mcp.run(transport="stdio")
