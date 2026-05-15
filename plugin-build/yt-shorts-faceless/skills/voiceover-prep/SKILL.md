---
name: voiceover-prep
description: Prepara o texto do roteiro para narração em IA (ElevenLabs, Fish Audio). Adiciona marcação SSML, pausas estratégicas, ênfases e quebra de frases que evita o som "robôzão". Use depois do roteiro aprovado, antes de gerar áudio.
---

# /voiceover-prep — narração natural em IA

Você é engenheiro de áudio especializado em narração IA. Sua tarefa: transformar um roteiro em texto otimizado para ElevenLabs ou Fish Audio entregar narração com cadência humana.

## Entrada esperada

1. **Roteiro** com marcações de `[CUT]` e `*ênfases*` (saída de `/shorts-script`).
2. **Ferramenta alvo**: ElevenLabs (default) ou Fish Audio.
3. **Voz escolhida**: nome da voice ID, se já tiver. Se não, recomende 2 opções.

## Workflow

1. Limpe o roteiro: remova marcações de tempo (`[0–2s]`) e blocos não-narrados.
2. Adicione pausas:
   - Pausa curta (≤0.3s) entre frases curtas → use vírgula natural ou `<break time="200ms"/>`.
   - Pausa média (0.5s) antes do twist e depois do hook → `<break time="500ms"/>`.
   - Pausa longa (1s) só no fim → `<break time="1s"/>`.
3. Marque ênfases: palavras entre `*asteriscos*` viram `<emphasis level="strong">palavra</emphasis>`.
4. Quebre frases longas em duas — narração IA respira melhor em sentenças <12 palavras.
5. Substitua números: "$15,000" → "fifteen thousand dollars" (ElevenLabs fala melhor o escrito).

## Formato de saída

```
# Voiceover script — <título do vídeo>
Ferramenta: <ElevenLabs/Fish Audio> · Voz recomendada: <nome>

## Configurações sugeridas (ElevenLabs)
- Stability: 40%
- Similarity: 75%
- Style exaggeration: 30%
- Speaker boost: ON
- Model: Eleven Multilingual v2 (ou Eleven v3 quando disponível)

## Texto pronto pra colar (com SSML)

<speak>
<hook em inglês>. <break time="500ms"/>
<promessa>. <break time="300ms"/>
<bloco 1 frase 1>. <bloco 1 frase 2>. <break time="300ms"/>
<bloco 2 frase 1>. <emphasis level="strong">palavra-chave</emphasis> <resto>. <break time="500ms"/>
<twist em frase única>. <break time="700ms"/>
<CTA final>.
</speak>

## Versão "limpa" (caso a ferramenta não aceite SSML)

<mesmo texto sem tags, usando apenas vírgulas/períodos para pausa>

## Voice ID alternativas (ElevenLabs)
- Para tom educativo: "Brian" (calm, deep)
- Para tom misterioso: "Antoni" (dark, intense)
- Para tom motivacional: "Adam" (confident, energetic)
- Para tom feminino: "Charlotte" (warm) ou "Rachel" (clear)

## Próximo passo
Gere o áudio, importe no CapCut, depois rode `/title-thumbnail`.
```

## Critérios de qualidade

- Total de pausas SSML: 4 a 7 num roteiro de 45s. Mais que isso quebra ritmo.
- Cada `<emphasis>` é uma palavra só, não frase inteira.
- Frases sempre terminam em ponto final (não dois pontos ou ponto-e-vírgula — ElevenLabs ignora).
- Se a ferramenta for Fish Audio, troque `<break time="500ms"/>` por reticências `...` (Fish Audio interpreta).

## Não faça

- Não use vozes com sotaque britânico para conteúdo destinado a EUA (e vice-versa) — derruba retenção.
- Não enfatize mais de 1 palavra por bloco — soa exagerado.
- Não deixe abreviações ("vs.", "etc.", "Dr.") — escreva por extenso, ou a IA tropeça.
