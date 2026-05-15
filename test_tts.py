"""Teste real: gera um MP3 curto via ElevenLabs."""
from dotenv import load_dotenv
import os, json
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")

from elevenlabs.client import ElevenLabs

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
out = Path(os.getenv("OUTPUT_DIR", Path(__file__).parent / "outputs")) / "test_narration.mp3"
out.parent.mkdir(parents=True, exist_ok=True)

print("Gerando narração de teste...")
audio = client.text_to_speech.convert(
    voice_id=voice_id,
    text="Most people quit right before they succeed. Here's why that happens — and how to stop.",
    model_id="eleven_multilingual_v2",
    output_format="mp3_44100_128",
)

with open(out, "wb") as f:
    for chunk in audio:
        f.write(chunk)

size_kb = out.stat().st_size // 1024
print(f"OK! Arquivo gerado: {out}")
print(f"Tamanho: {size_kb} KB")
