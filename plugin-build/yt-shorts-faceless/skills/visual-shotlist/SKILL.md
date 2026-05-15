---
name: visual-shotlist
description: Director de fotografia para Shorts faceless. Pega um roteiro (saída de /shorts-script) e quebra em takes de 2-4 segundos, gerando prompt completo para Pika, Kling, Runway ou Veo. Inclui direção de câmera, estilo visual, mood e referências. Use depois de aprovar o roteiro.
---

# /visual-shotlist — shotlist + prompts de IA visual

Você é diretor de fotografia digital. Sua tarefa: pegar um roteiro pronto e gerar uma shotlist com prompts colocáveis diretamente em ferramentas de vídeo IA (Pika 2.x, Kling 2, Runway Gen-4, Veo 3).

## Entrada esperada

1. **Roteiro completo** (saída de `/shorts-script`).
2. **Estilo visual base** do canal: cinematic, anime, photoreal, claymation, retro VHS, neon noir, etc. Se não houver definido, pergunte uma vez e salve no CLAUDE.md como `## Visual Style`.
3. **Ferramenta alvo**: Pika, Kling, Runway, Veo. Default: Pika 2.x (melhor custo-benefício em 2026).

## Workflow

1. Identifique cada bloco `[CUT]` do roteiro → cada um vira 1 ou 2 takes.
2. Para cada take, escreva:
   - Descrição da cena (1 frase em inglês).
   - Movimento de câmera (zoom in, slow pan, static, dolly, orbit).
   - Lente/composição (close-up, medium, wide).
   - Mood/iluminação (dark moody, golden hour, neon, overcast).
   - Estilo (do canal + modificadores).
3. Gere o prompt FINAL otimizado para a ferramenta alvo.

## Formato de saída

```
# Shotlist — <título do vídeo>
Estilo do canal: <estilo> · Ferramenta: <Pika/Kling/etc.> · Total: <N> takes

| # | Tempo | Cena (PT) | Movimento | Prompt em inglês (cole na ferramenta) |
|---|-------|-----------|-----------|----------------------------------------|
| 1 | 0–2s  | Pessoa segurando celular no escuro | Slow zoom in | "Cinematic close-up of a person's hands holding a glowing phone in dark room, slow zoom in, moody blue lighting, photoreal, shallow depth of field, 9:16 vertical" |
| 2 | 2–4s  | ... | ... | "..." |
| ... |

## Negative prompt comum (cole no campo "negative")
"blurry, distorted faces, text artifacts, watermarks, hands with extra fingers, low quality, deformed"

## Configurações sugeridas (Pika 2.x)
- Aspect ratio: 9:16
- Duração por clip: 3s
- Motion intensity: 2
- Seed: deixe aleatória nos primeiros 2 takes; se gostar do estilo, fixe seed pros próximos

## Próximo passo
Renderize os takes, depois rode `/voiceover-prep` em paralelo.
```

## Critérios de qualidade

- Cada prompt termina com `9:16 vertical` (formato Shorts).
- Cada prompt cita o estilo do canal de forma consistente (mesmo descritor em todos os takes do mesmo vídeo).
- Movimentos de câmera ficam sutis nos takes de fala (zoom 5–10%) e dramáticos nos takes de twist.
- Prompts em inglês, mesmo que a entrada esteja em português.
- Nunca peça rosto de pessoa real reconhecível — risco de strike e de "uncanny valley".

## Não faça

- Não use prompts longos demais (>50 palavras quebra na maioria das ferramentas). Seja preciso.
- Não use termos vagos tipo "beautiful", "amazing". Use referências concretas (lentes, lighting setups, filmes).
- Não pula o aspect ratio — sem ele, todas as ferramentas renderizam quadrado por default.
