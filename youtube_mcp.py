"""MCP server — YouTube Data API v3 para upload e agendamento de Shorts."""

import os
import json
import pickle
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

load_dotenv(Path(__file__).parent / ".env")

mcp = FastMCP("youtube-upload")

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly"]
TOKEN_FILE = Path(__file__).parent / "youtube_token.pkl"
CLIENT_SECRETS = Path(__file__).parent / "youtube_client_secrets.json"

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", Path(__file__).parent / "outputs"))


def _get_youtube_client():
    creds = None
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRETS.exists():
                _write_client_secrets()
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)


def _write_client_secrets():
    """Escreve youtube_client_secrets.json a partir das variáveis de ambiente."""
    secrets = {
        "installed": {
            "client_id": os.getenv("YOUTUBE_CLIENT_ID", ""),
            "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET", ""),
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    CLIENT_SECRETS.write_text(json.dumps(secrets))


@mcp.tool()
def upload_short(
    video_path: str,
    title: str,
    description: str,
    tags: list,
    thumbnail_path: str = "",
    publish_at: str = "",
) -> str:
    """
    Faz upload de um Short para o YouTube.

    Args:
        video_path: Caminho absoluto do arquivo MP4 final.
        title: Título do vídeo (max 100 chars).
        description: Descrição com hashtags (max 5000 chars).
        tags: Lista de tags (max 500 chars total).
        thumbnail_path: Caminho da thumbnail JPG/PNG (opcional).
        publish_at: ISO 8601 com timezone para agendar. Ex: '2026-05-14T08:00:00+00:00'.
                    Vazio = publica imediatamente.

    Returns:
        JSON com video_id e URL do vídeo publicado.
    """
    yt = _get_youtube_client()

    status = "private" if publish_at else "public"
    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags,
            "categoryId": "22",
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": status,
            "selfDeclaredMadeForKids": False,
        },
    }
    if publish_at:
        body["status"]["publishAt"] = publish_at

    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True, chunksize=1024 * 1024)
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        _, response = request.next_chunk()

    video_id = response["id"]

    if thumbnail_path and Path(thumbnail_path).exists():
        yt.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(thumbnail_path)).execute()

    return json.dumps({
        "success": True,
        "video_id": video_id,
        "url": f"https://www.youtube.com/shorts/{video_id}",
        "status": status,
        "publish_at": publish_at or "immediate",
    })


@mcp.tool()
def get_channel_stats() -> str:
    """Retorna estatísticas básicas do canal: inscritos, views, vídeos."""
    yt = _get_youtube_client()
    resp = yt.channels().list(part="statistics", mine=True).execute()
    stats = resp["items"][0]["statistics"]
    return json.dumps({
        "subscribers": int(stats.get("subscriberCount", 0)),
        "total_views": int(stats.get("viewCount", 0)),
        "video_count": int(stats.get("videoCount", 0)),
    })


@mcp.tool()
def list_recent_shorts(max_results: int = 10) -> str:
    """Lista os Shorts mais recentes do canal com views e likes."""
    yt = _get_youtube_client()
    search_resp = yt.search().list(
        part="snippet", forMine=True, type="video",
        order="date", maxResults=max_results,
    ).execute()

    ids = [item["id"]["videoId"] for item in search_resp.get("items", [])]
    if not ids:
        return json.dumps([])

    stats_resp = yt.videos().list(part="snippet,statistics", id=",".join(ids)).execute()
    result = []
    for item in stats_resp.get("items", []):
        s = item["statistics"]
        result.append({
            "title": item["snippet"]["title"],
            "video_id": item["id"],
            "url": f"https://www.youtube.com/shorts/{item['id']}",
            "views": int(s.get("viewCount", 0)),
            "likes": int(s.get("likeCount", 0)),
            "published": item["snippet"]["publishedAt"],
        })
    return json.dumps(result)


if __name__ == "__main__":
    mcp.run(transport="stdio")
