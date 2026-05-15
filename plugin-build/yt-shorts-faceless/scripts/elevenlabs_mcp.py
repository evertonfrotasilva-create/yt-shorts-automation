"""MCP server — TTS gratuito via edge-tts (Microsoft Edge).
Gera narrações em inglês sem precisar de API key.
Quando fizer upgrade pro ElevenLabs pago, basta trocar as funções abaixo.
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import edge_tts

load_dotenv(Path(__file__).parent / ".env")

mcp = FastMCP("tts-voiceover")

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", Path(__file__).parent / "outputs"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Vozes recomendadas para Shorts em inglês
VOICES = {
    "aria":   "en-US-AriaNeural",       # feminino EUA — natural, caloroso
    "guy":    "en-US-GuyNeural",        # masculino EUA — direto
    "jenny":  "en-US-JennyNeural",      # feminino EUA — amigável
    "sonia":  "en-GB-SoniaNeural",      # feminino britânico — autoridade
    "ryan":   "en-GB-RyanNeural",       # masculino britânico — premium
    "default": "en-US-AriaNeural",
}


async def _synthesize(text: str, voice: str, out_path: Path) -> None:
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(out_path))


@mcp.tool()
def generate_voiceover(
    text: str,
    voice: str = "aria",
    filename: str = "",
) -> str:
    """
    Gera narração em MP3 via Microsoft Edge TTS (gratuito, sem API key).

    Args:
        text: Texto a narrar em inglês (máx ~2000 chars por chamada).
        voice: Voz a usar. Opções: aria, guy, jenny, sonia, ryan.
               'aria' é o padrão — feminino EUA, natural para Shorts educativos.
        filename: Nome do arquivo sem extensão. Usa timestamp se omitido.

    Returns:
        JSON com caminho do arquivo MP3 gerado e duração estimada.
    """
    voice_id = VOICES.get(voice.lower(), VOICES["default"])
    fname = filename or f"voiceover_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_path = OUTPUT_DIR / f"{fname}.mp3"

    asyncio.run(_synthesize(text, voice_id, out_path))

    words = len(text.split())
    estimated_s = round(words / 2.8)

    return json.dumps({
        "success": True,
        "file": str(out_path),
        "estimated_duration_s": estimated_s,
        "voice": voice_id,
        "words": words,
    })


@mcp.tool()
def list_voices() -> str:
    """Lista as vozes disponíveis para narrações em inglês."""
    return json.dumps([
        {"key": "aria",  "name": "Aria (en-US)",  "style": "Natural, warm — best for educational content"},
        {"key": "guy",   "name": "Guy (en-US)",   "style": "Direct, confident — good for motivational"},
        {"key": "jenny", "name": "Jenny (en-US)", "style": "Friendly, conversational"},
        {"key": "sonia", "name": "Sonia (en-GB)", "style": "Authoritative, premium feel"},
        {"key": "ryan",  "name": "Ryan (en-GB)",  "style": "Warm British accent"},
    ])


if __name__ == "__main__":
    mcp.run(transport="stdio")
