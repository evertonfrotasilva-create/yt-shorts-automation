# Security Policy

## Segredos utilizados

| Secret | Onde fica | Validade |
|--------|-----------|----------|
| `ELEVENLABS_API_KEY` | GitHub Secrets + `.env` local | Sem expiração (revogar manualmente) |
| `PEXELS_API_KEY` | GitHub Secrets + `.env` local | Sem expiração |
| `YOUTUBE_CLIENT_ID` | GitHub Secrets + `.env` local | Sem expiração |
| `YOUTUBE_CLIENT_SECRET` | GitHub Secrets + `.env` local | Sem expiração |
| `YOUTUBE_REFRESH_TOKEN` | GitHub Secrets | Expira após ~6 meses sem uso (modo Testing) |

## Como renovar o YOUTUBE_REFRESH_TOKEN

O token expira se o app Google Cloud estiver em modo **Testing** e não for usado por 7 dias,
ou após ~6 meses em produção.

```bash
# 1. Deleta o token antigo localmente
rm youtube_token.pkl

# 2. Abre o fluxo OAuth (abrirá o browser)
python -c "from webapp import _load_youtube_creds; _load_youtube_creds()"

# 3. Reconfigura o secret no GitHub
python setup_github_secrets.py
```

## O que fazer se uma chave vazar

1. **Revogar imediatamente** no console do provedor (ElevenLabs, Google, Pexels)
2. **Remover do GitHub Secrets**: Settings → Secrets → Actions → deletar
3. Gerar nova chave e rodar `python setup_github_secrets.py`
4. Verificar histórico de uso nos dashboards dos provedores

## Arquivos que NUNCA devem ser commitados

Já protegidos pelo `.gitignore`:
- `.env` — todas as API keys
- `*.pkl` — tokens OAuth localizados
- `youtube_client_secrets.json` — credenciais OAuth do Google
- `outputs/` — vídeos gerados (dados de produção)

## Proteção de branch recomendada

No GitHub → Settings → Branches → Branch protection rules para `master`:
- [x] Require a pull request before merging
- [x] Require status checks to pass (selecionar: `validate`)
- [x] Do not allow bypassing the above settings

## Vulnerabilidades

Para reportar uma vulnerabilidade de segurança neste projeto,
abra uma issue privada ou contate: evertonfrota.silva@gmail.com
