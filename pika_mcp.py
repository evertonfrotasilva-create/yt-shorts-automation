"""MCP server — Vídeo stock via Pexels API (gratuito, sem créditos).
Busca clipes relevantes ao prompt, baixa e entrega prontos para edição.
Substitui o Pika AI na fase de testes gratuitos.
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(Path(__file__).parent / ".env")

mcp = FastMCP("pexels-video")

PEXELS_KEY = os.getenv("PEXELS_API_KEY", "")
PEXELS_BASE = "https://api.pexels.com/videos"
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", Path(__file__).parent / "outputs"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _headers() -> dict:
    return {"Authorization": PEXELS_KEY}


def _best_vertical_file(video_files: list) -> dict | None:
    """Prioriza arquivos verticais (9:16) ou de alta qualidade."""
    vertical = [f for f in video_files if f.get("width", 0) < f.get("height", 1)]
    if vertical:
        return max(vertical, key=lambda f: f.get("height", 0))
    return max(video_files, key=lambda f: f.get("height", 0)) if video_files else None


@mcp.tool()
def generate_video_clip(
    prompt: str,
    aspect_ratio: str = "9:16",
    duration: int = 4,
    filename: str = "",
) -> str:
    """
    Busca e baixa um clipe de vídeo stock via Pexels (gratuito).

    Args:
        prompt: Palavras-chave em inglês para buscar o clipe (ex: 'person thinking alone dark').
        aspect_ratio: Ignorado na busca mas registrado nos metadados.
        duration: Ignorado na busca (Pexels retorna o clipe mais relevante).
        filename: Nome base do arquivo MP4. Usa timestamp se omitido.

    Returns:
        JSON com caminho do arquivo baixado, URL original e metadados.
    """
    params = {"query": prompt, "per_page": 5, "orientation": "portrait"}
    r = requests.get(f"{PEXELS_BASE}/search", headers=_headers(), params=params, timeout=15)
    r.raise_for_status()
    videos = r.json().get("videos", [])

    if not videos:
        return json.dumps({"success": False, "error": f"Nenhum vídeo encontrado para: {prompt}"})

    video = videos[0]
    file_info = _best_vertical_file(video.get("video_files", []))
    if not file_info:
        return json.dumps({"success": False, "error": "Nenhum arquivo de vídeo disponível"})

    video_url = file_info["link"]
    fname = filename or f"clip_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_path = OUTPUT_DIR / f"{fname}.mp4"

    with requests.get(video_url, stream=True, timeout=60) as resp:
        resp.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 64):
                f.write(chunk)

    return json.dumps({
        "success": True,
        "file": str(out_path),
        "url": video_url,
        "pexels_id": video["id"],
        "duration_s": video.get("duration", 0),
        "width": file_info.get("width"),
        "height": file_info.get("height"),
        "search_query": prompt,
    })


@mcp.tool()
def generate_shotlist_videos(
    shots: list,
    filename_prefix: str = "shot",
) -> str:
    """
    Baixa múltiplos clipes stock para um shotlist completo.

    Args:
        shots: Lista de dicts com 'prompt' e opcionalmente 'duration'.
               Ex: [{"prompt": "person alone dark room"}, {"prompt": "brain neurons firing"}]
        filename_prefix: Prefixo dos arquivos baixados.

    Returns:
        JSON com lista de arquivos e status de cada clipe.
    """
    results = []
    for i, shot in enumerate(shots):
        prompt = shot.get("prompt", "")
        try:
            r = json.loads(generate_video_clip(
                prompt=prompt,
                filename=f"{filename_prefix}_{i+1:02d}",
            ))
            results.append({"shot": i + 1, **r})
        except Exception as e:
            results.append({"shot": i + 1, "success": False, "error": str(e)})

    return json.dumps({"clips": results, "total": len(results)})


if __name__ == "__main__":
    mcp.run(transport="stdio")
