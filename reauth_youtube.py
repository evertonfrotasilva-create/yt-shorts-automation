"""
Re-autoriza o YouTube OAuth2.
Inicia um servidor local na porta 8080 para capturar o redirect do Google.

Uso:
  python reauth_youtube.py
"""
import os, json, pickle, sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

SCOPES        = ["https://www.googleapis.com/auth/youtube.upload"]
token_file    = BASE_DIR / "youtube_token.pkl"
client_secrets = BASE_DIR / "youtube_client_secrets.json"

client_id     = os.getenv("YOUTUBE_CLIENT_ID", "")
client_secret = os.getenv("YOUTUBE_CLIENT_SECRET", "")

if not client_id or not client_secret:
    print("ERRO: YOUTUBE_CLIENT_ID ou YOUTUBE_CLIENT_SECRET nao encontrados no .env")
    sys.exit(1)

# Desktop app com redirect para localhost
client_secrets.write_text(json.dumps({"installed": {
    "client_id":     client_id,
    "client_secret": client_secret,
    "redirect_uris": ["http://localhost"],
    "auth_uri":      "https://accounts.google.com/o/oauth2/auth",
    "token_uri":     "https://oauth2.googleapis.com/token",
}}))

if token_file.exists():
    token_file.unlink()
    print("Token antigo removido.")

from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets), SCOPES)

# Abre servidor local na porta 8080 e imprime a URL sem abrir o browser automaticamente
print("\nIniciando servidor local na porta 8080...")
print("Abrindo browser para autorizacao...\n")

creds = flow.run_local_server(
    port=8090,
    open_browser=True,
    authorization_prompt_message="Se o browser nao abrir automaticamente, acesse:\n{url}\n",
    success_message="Autorizacao concluida! Pode fechar esta aba.",
)

with open(token_file, "wb") as f:
    pickle.dump(creds, f)

print("\n" + "=" * 60)
print("SUCESSO! Novo refresh token salvo localmente.")
print()
print("Atualize o GitHub Secret YOUTUBE_REFRESH_TOKEN com:")
print("=" * 60)
print(creds.refresh_token)
print("=" * 60)
