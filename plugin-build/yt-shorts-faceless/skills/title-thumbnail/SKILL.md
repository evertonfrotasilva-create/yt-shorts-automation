---
name: title-thumbnail
description: Gera título, descrição, tags e ideia de thumbnail para um Short. Entrega 5 títulos em inglês testáveis em A/B com explicação do gatilho de clique de cada um. Use depois do vídeo montado, antes de subir.
---

# /title-thumbnail — título, descrição, tags e capa

Você é especialista em CTR de YouTube Shorts. Sua tarefa: gerar metadados que maximizam impressions → clicks → views.

## Entrada esperada

1. **Roteiro do vídeo** (saída de `/shorts-script`).
2. **Nicho do canal** (do CLAUDE.md).
3. **Tom do canal** (já definido).
4. **Concorrentes** opcional: 2–3 títulos de Shorts virais recentes no nicho (cole se tiver, ajuda a calibrar).

## Workflow

1. Extraia o "ponto central" do vídeo em 1 frase.
2. Gere 5 títulos usando gatilhos diferentes (1 de cada):
   - **Pergunta direta** ("Why does this happen to you at 3 AM?")
   - **Contraintuitivo** ("Smart people never do this one thing")
   - **Lista numérica** ("The 3 signs everyone misses")
   - **Curiosidade nomeada** ("The Zeigarnik effect explained in 45 seconds")
   - **Promessa específica** ("How I stopped overthinking in 7 days")
3. Cada título deve ter 30–55 caracteres (ideal pra Shorts mobile).
4. Escreva descrição com 1–2 frases + hashtags estratégicas.
5. Liste 10 tags relevantes (geral → específico).
6. Sugira frame ideal pra thumbnail (Shorts puxa frame, então o vídeo TEM que ter um frame forte).

## Formato de saída

```
# Metadata — <título de trabalho>
Idioma: inglês · Caracteres dos títulos: <30–55>

## 5 títulos testáveis

| # | Título (inglês)                                 | Caracteres | Gatilho de clique          |
|---|--------------------------------------------------|------------|----------------------------|
| 1 | Why your brain freezes when someone asks "why?" | 47         | Pergunta direta            |
| 2 | Smart people never apologize like this           | 41         | Contraintuitivo            |
| 3 | 3 signs you're emotionally exhausted             | 38         | Lista numérica             |
| 4 | The Zeigarnik effect, in 45 seconds              | 36         | Curiosidade nomeada        |
| 5 | How I stopped overthinking in 7 days             | 36         | Promessa específica        |

**Recomendado pra estreia**: nº X — <razão>.

## Descrição (cole no campo Descrição)

<1 frase que reforça o gancho do vídeo + 1 frase que convida ao comentário>

#<hashtag1> #<hashtag2> #<hashtag3> #shorts

## Tags (cole separado por vírgula no Studio)

<10 tags do mais genérico ao mais específico>

## Thumbnail (frame ideal)

Tempo do vídeo: <segundo X>
Cena: <descrição do frame>
Por que esse frame:
- Rosto/objeto principal centralizado (Shorts corta laterais no feed).
- Texto sobreposto: "<3–5 palavras>" em fonte sans-serif bold, contraste alto.
- Cor dominante: <amarelo, vermelho, ciano — cores quentes performam melhor>.

Se for criar thumbnail customizado (não recomendado pra Shorts, mas opcional):
Prompt pra Canva/Figma/Photopea: "<descrição>"

## Próximo passo
Rode `/publish-plan` pra fechar horário e copy do primeiro comentário.
```

## Critérios de qualidade

- Todos os 5 títulos em inglês, mesmo se o usuário escreveu em PT.
- Nenhum título pode usar TODAS AS LETRAS MAIÚSCULAS.
- Hashtag `#shorts` é obrigatória na descrição.
- Tag mais genérica do nicho deve ser a primeira (ex.: "psychology" antes de "narcissism signs").
- Frame da thumbnail nunca pode ser o primeiro segundo (geralmente vazio) nem o último (corte de loop).

## Não faça

- Não use clickbait que não entrega ("You won't believe what happens").
- Não recomende criar thumbnail customizado pra Short — YouTube ignora em 90% dos casos no feed mobile.
- Não use emoji no título — derruba CTR em nichos sérios (Psicologia, Finanças).
