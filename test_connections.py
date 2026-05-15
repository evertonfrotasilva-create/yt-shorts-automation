from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

keys = {
    "ElevenLabs API Key": os.getenv("ELEVENLABS_API_KEY", ""),
    "Pika/Fal.ai Key": os.getenv("PIKA_API_KEY", ""),
    "YouTube Client ID": os.getenv("YOUTUBE_CLIENT_ID", ""),
    "YouTube Client Secret": os.getenv("YOUTUBE_CLIENT_SECRET", ""),
}

print("=== Status das chaves ===")
for name, val in keys.items():
    ok = val and "your_" not in val and len(val) > 10
    status = "OK" if ok else "FALTANDO"
    print(f"  {name}: {status}")

print("\n=== Teste ElevenLabs ===")
try:
    from elevenlabs.client import ElevenLabs
    c = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
    voices = c.voices.get_all()
    print(f"  Conexao: OK ({len(voices.voices)} vozes encontradas)")
    sub = c.user.get_subscription()
    remaining = sub.character_limit - sub.character_count
    print(f"  Caracteres restantes este mes: {remaining:,}")
except Exception as e:
    print(f"  ERRO: {e}")

print("\n=== Teste Fal.ai/Pika ===")
try:
    import fal_client
    os.environ["FAL_KEY"] = os.getenv("PIKA_API_KEY", "")
    print("  fal-client importado: OK")
    print("  Chave configurada: OK")
except Exception as e:
    print(f"  ERRO: {e}")

print("\nTudo pronto para uso!")
