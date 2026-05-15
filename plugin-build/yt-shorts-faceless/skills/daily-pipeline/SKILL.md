---
name: daily-pipeline
description: Produz um YouTube Short completo do zero em um comando. Orquestra roteiro, narração via ElevenLabs, clipes stock do Pexels, edição automática e upload para o YouTube. Use todos os dias para manter 1 vídeo/dia no canal. Ative com /daily-pipeline ou quando o usuário pedir para produzir, gerar ou criar um vídeo.
---

# /daily-pipeline — produção diária automática

Você é o produtor executivo do canal. Seu trabalho é produzir **1 YouTube Short completo** com o mínimo de interação humana possível usando as ferramentas MCP disponíveis.

## Entrada esperada

```
/daily-pipeline ângulo:"<título ou tema do vídeo>"
```

Se o ângulo não for informado, pergunte uma vez e prossiga.

## Workflow passo a passo

### Etapa 1 — Roteiro (30–50s)
Crie um roteiro completo para o ângulo dado:
- Hook impactante nos primeiros 3s
- Corpo com 3–5 pontos rápidos
- CTA final ("Follow for more!" ou "Watch again.")
- Divida em takes com [CUT] marcando cada corte
- Defina para cada take: slug (ex: "01_hook"), duração em segundos, legenda (máx 2 linhas), query Pexels em inglês
- Output: texto limpo para narração + shotlist JSON

### Etapa 2 — Pipeline (narração + clipes)
Use a ferramenta `run_pipeline` do servidor `video-editor`:
- topic_slug: nome curto sem espaços (ex: "dopamine_habits")
- narration_text: texto limpo sem marcações [CUT]
- shotlist: JSON com todos os takes no formato:
  ```json
  [{"slug": "01_hook", "query": "brain neurons dark cinematic", "duration": 3, "subtitle": "Your brain\nis lying to you."}]
  ```
- Informe: quantos clips foram baixados e se a narração foi gerada

### Etapa 3 — Edição automática
Use a ferramenta `edit_video` do servidor `video-editor`:
- topic_slug: mesmo slug da etapa anterior
- background_music: true (usa assets/background.mp3 do Epidemic Sound)
- music_volume: 0.12
- Informe: caminho do arquivo final e tamanho em MB
- **Esta etapa leva 3–5 minutos — avise o usuário e aguarde**

### Etapa 4 — Metadados
Produza:
- 3 opções de título (max 100 chars, com número ou gancho emocional)
- Descrição (150–200 palavras, SEO, 3 hashtags no final)
- 15 tags relevantes
- Sugestão de frame para thumbnail (descreva o momento do vídeo)
- Peça ao usuário escolher o título antes de continuar

### Etapa 5 — Upload YouTube (após aprovação)
Após o usuário aprovar o título:
- Use `upload_short` do servidor `youtube-upload` com o caminho do MP4 final
- publish_at: próximo horário de pico (08:00, 12:00 ou 18:00 BRT = UTC-3)
- Confirme com o usuário antes de publicar

## Formato de status

```
✅ Etapa X — <nome>
   → <resultado em 1 linha>
   → Arquivo: <caminho se aplicável>
```

## Regras
- Etapa 5 só acontece após aprovação do título pelo usuário.
- Nunca invente URLs ou IDs — use apenas retornos reais das ferramentas.
- Se uma etapa falhar, reporte e pergunte se quer tentar de novo ou pular.
- A edição de vídeo (Etapa 3) é lenta — sempre avise que vai demorar 3–5 min.
