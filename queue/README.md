# Fila Semanal de Vídeos

Cada semana tem um arquivo `YYYY_WNN.json` com 7 vídeos (seg–dom).

## Como preencher (toda segunda-feira, 15 min)

1. No Cowork: `/weekly-trends` → pega 7 ângulos
2. No Cowork: `/daily-pipeline ângulo:"..."` × 7 → pega 7 narações
3. Copia os dados para o arquivo da semana
4. A automação faz o resto sozinha

## Status de cada vídeo
- `pending`   → aguardando produção
- `producing` → sendo produzido agora
- `done`      → produzido e enviado
- `error`     → falhou (ver campo error_msg)
