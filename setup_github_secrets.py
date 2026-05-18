"""
Configura todos os secrets necessários no GitHub Actions.
Uso: python setup_github_secrets.py
"""
import os, pickle, base64, requests
from pathlib import Path
from nacl import encoding, public
from dotenv import load_dotenv

REPO  = "evertonfrotasilva-create/yt-shorts-automation"
BASE  = Path(__file__).parent
load_dotenv(BASE / ".env")

# ── Coleta os valores ──────────────────────────────────────────────────────────

def get_refresh_token() -> str:
    pkl = BASE / "youtube_token.pkl"
    if not pkl.exists():
        raise FileNotFoundError("youtube_token.pkl não encontrado — faça o login OAuth primeiro")
    with open(pkl, "rb") as f:
        creds = pickle.load(f)
    if not creds.refresh_token:
        raise ValueError("Refresh token vazio no pickle — refaça o login OAuth")
    return creds.refresh_token

SECRETS = {
    "ELEVENLABS_API_KEY":    os.getenv("ELEVENLABS_API_KEY", ""),
    "PEXELS_API_KEY":        os.getenv("PEXELS_API_KEY", ""),
    "YOUTUBE_CLIENT_ID":     os.getenv("YOUTUBE_CLIENT_ID", ""),
    "YOUTUBE_CLIENT_SECRET": os.getenv("YOUTUBE_CLIENT_SECRET", ""),
    "YOUTUBE_REFRESH_TOKEN": "",  # preenchido abaixo
}

try:
    SECRETS["YOUTUBE_REFRESH_TOKEN"] = get_refresh_token()
except Exception as e:
    print(f"AVISO: {e}")


# ── Funções GitHub API ─────────────────────────────────────────────────────────

def encrypt_secret(public_key_b64: str, value: str) -> str:
    key = public.PublicKey(public_key_b64.encode(), encoding.Base64Encoder())
    box = public.SealedBox(key)
    encrypted = box.encrypt(value.encode())
    return base64.b64encode(encrypted).decode()


def set_secret(token: str, name: str, value: str, key_id: str, public_key: str):
    encrypted = encrypt_secret(public_key, value)
    url = f"https://api.github.com/repos/{REPO}/actions/secrets/{name}"
    r = requests.put(url,
        headers={"Authorization": f"token {token}", "Accept": "application/vnd.github+json"},
        json={"encrypted_value": encrypted, "key_id": key_id},
        timeout=15,
    )
    return r.status_code in (201, 204)


def get_repo_public_key(token: str) -> tuple:
    url = f"https://api.github.com/repos/{REPO}/actions/secrets/public-key"
    r = requests.get(url,
        headers={"Authorization": f"token {token}", "Accept": "application/vnd.github+json"},
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    return data["key_id"], data["key"]


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  Configuração de Secrets — GitHub Actions")
    print(f"  Repo: {REPO}")
    print("=" * 55)

    # Verifica se algum valor está vazio
    missing = [k for k, v in SECRETS.items() if not v]
    if missing:
        print(f"\nERRO: Valores ausentes no .env ou token.pkl: {missing}")
        return

    print("\nSecrets a configurar:")
    for k in SECRETS:
        print(f"  [ok] {k}")

    print("\nGere um token em: https://github.com/settings/tokens")
    print("Permissao necessaria: repo (escopo completo)")
    token = input("\nCole seu GitHub Personal Access Token: ").strip()
    if not token:
        print("Token vazio — abortando.")
        return

    print("\nObtendo chave pública do repositório...")
    try:
        key_id, public_key = get_repo_public_key(token)
    except Exception as e:
        print(f"ERRO ao autenticar: {e}")
        print("Verifique se o token tem permissão 'repo' e se o repositório existe.")
        return

    print("Configurando secrets...")
    ok = 0
    for name, value in SECRETS.items():
        try:
            success = set_secret(token, name, value, key_id, public_key)
            status = "OK" if success else "ERRO"
            print(f"  [{status}] {name}")
            if success:
                ok += 1
        except Exception as e:
            print(f"  [ERRO] {name}: {e}")

    print(f"\n{'=' * 55}")
    print(f"Concluído: {ok}/{len(SECRETS)} secrets configurados")
    if ok == len(SECRETS):
        print("\nPróximos passos:")
        print("  1. Vá em Actions no GitHub e rode manualmente o workflow")
        print("     (botão 'Run workflow' na aba Actions → Daily YT Short)")
        print("  2. A partir de amanhã rodará automaticamente às 06:00 BRT")
    print("=" * 55)


if __name__ == "__main__":
    main()
