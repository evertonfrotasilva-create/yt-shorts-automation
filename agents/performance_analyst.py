"""
Performance Analyst Agent
Lê métricas do YouTube das últimas semanas e gera performance_report.json
com os melhores horários de publicação e tópicos de maior engajamento.
"""

import os, json, sys
from pathlib import Path
from datetime import date, timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def _youtube_client():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN", "")
    if not refresh_token:
        raise RuntimeError("YOUTUBE_REFRESH_TOKEN não configurado")

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("YOUTUBE_CLIENT_ID", ""),
        client_secret=os.getenv("YOUTUBE_CLIENT_SECRET", ""),
        scopes=["https://www.googleapis.com/auth/youtube.readonly"],
    )
    creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)


def collect_done_entries(weeks_back: int = 4) -> list:
    """Lê entradas 'done' das últimas N semanas das filas locais."""
    queue_dir = BASE_DIR / "queue"
    today = date.today()
    entries = []
    seen_slugs = set()

    for i in range(weeks_back):
        check = today - timedelta(weeks=i)
        iso_year, iso_week, _ = check.isocalendar()
        qf = queue_dir / f"{iso_year}_W{iso_week:02d}.json"
        if not qf.exists():
            continue
        for e in json.loads(qf.read_text(encoding="utf-8")):
            if e.get("status") == "done" and e.get("video_id") and e["slug"] not in seen_slugs:
                entries.append(e)
                seen_slugs.add(e["slug"])

    return entries


def fetch_channel_videos(yt, max_results: int = 50) -> list:
    """Busca todos os vídeos do canal direto do YouTube (ignora fila local)."""
    # Pega o channel id do próprio token
    channel_resp = yt.channels().list(part="id,contentDetails", mine=True).execute()
    items = channel_resp.get("items", [])
    if not items:
        return []

    uploads_playlist = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    videos = []
    page_token = None
    while len(videos) < max_results:
        resp = yt.playlistItems().list(
            part="contentDetails,snippet",
            playlistId=uploads_playlist,
            maxResults=min(50, max_results - len(videos)),
            pageToken=page_token,
        ).execute()
        for item in resp.get("items", []):
            videos.append({
                "video_id":    item["contentDetails"]["videoId"],
                "title":       item["snippet"]["title"],
                "published_at": item["snippet"]["publishedAt"],
            })
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return videos


def fetch_stats(yt, entries: list) -> dict:
    """Busca estatísticas do YouTube para os vídeos."""
    ids = [e["video_id"] for e in entries if e.get("video_id")]
    stats = {}
    for chunk in [ids[i:i+50] for i in range(0, len(ids), 50)]:
        resp = yt.videos().list(part="statistics", id=",".join(chunk)).execute()
        for item in resp.get("items", []):
            s = item["statistics"]
            stats[item["id"]] = {
                "views":    int(s.get("viewCount",    0)),
                "likes":    int(s.get("likeCount",    0)),
                "comments": int(s.get("commentCount", 0)),
            }
    return stats


def fetch_all_channel_stats(yt) -> tuple[list, dict]:
    """Busca todos os vídeos do canal + estatísticas em uma só chamada."""
    channel_videos = fetch_channel_videos(yt, max_results=200)
    if not channel_videos:
        return [], {}

    ids = [v["video_id"] for v in channel_videos]
    stats = {}
    for chunk in [ids[i:i+50] for i in range(0, len(ids), 50)]:
        resp = yt.videos().list(part="statistics", id=",".join(chunk)).execute()
        for item in resp.get("items", []):
            s = item["statistics"]
            stats[item["id"]] = {
                "views":    int(s.get("viewCount",    0)),
                "likes":    int(s.get("likeCount",    0)),
                "comments": int(s.get("commentCount", 0)),
            }

    return channel_videos, stats


def analyze(entries: list, stats: dict, channel_videos: list = None) -> dict:
    """Analisa padrões e retorna insights acionáveis."""
    videos = []

    # Vídeos da fila local (com horário de publicação e tags)
    seen_ids = set()
    for e in entries:
        vid_id = e.get("video_id", "")
        s = stats.get(vid_id, {"views": 0, "likes": 0, "comments": 0})
        videos.append({
            "slug":              e["slug"],
            "title":             e.get("title", ""),
            "date":              e.get("date", ""),
            "publish_hour_brt":  e.get("publish_hour_brt", 18),
            "views":             s["views"],
            "likes":             s["likes"],
            "comments":          s["comments"],
            "tags":              e.get("tags", []),
        })
        if vid_id:
            seen_ids.add(vid_id)

    # Vídeos do canal que não estão na fila local
    for cv in (channel_videos or []):
        vid_id = cv["video_id"]
        if vid_id in seen_ids:
            continue
        s = stats.get(vid_id, {"views": 0, "likes": 0, "comments": 0})
        videos.append({
            "slug":              vid_id,
            "title":             cv["title"],
            "date":              cv["published_at"][:10],
            "publish_hour_brt":  int(cv["published_at"][11:13]),
            "views":             s["views"],
            "likes":             s["likes"],
            "comments":          s["comments"],
            "tags":              [],
        })
        seen_ids.add(vid_id)

    if not videos:
        return {
            "best_hours":       [8, 14, 20],
            "top_videos":       [],
            "avg_views":        0,
            "videos_analyzed":  0,
            "hour_performance": {},
            "videos":           [],
        }

    # Melhor horário por views médias
    hour_views: dict = {}
    for v in videos:
        h = v["publish_hour_brt"]
        hour_views.setdefault(h, []).append(v["views"])
    hour_avg = {h: round(sum(vs) / len(vs), 1) for h, vs in hour_views.items()}

    best_hours = sorted(hour_avg, key=lambda h: hour_avg[h], reverse=True)[:3]
    # Garante 3 horários com fallback
    for h in [8, 14, 20]:
        if len(best_hours) < 3 and h not in best_hours:
            best_hours.append(h)
    best_hours = sorted(best_hours[:3])  # ordem cronológica

    top_videos = sorted(videos, key=lambda v: v["views"], reverse=True)[:5]
    avg_views  = round(sum(v["views"] for v in videos) / len(videos), 1)

    return {
        "best_hours":       best_hours,
        "top_videos":       top_videos,
        "avg_views":        avg_views,
        "videos_analyzed":  len(videos),
        "hour_performance": hour_avg,
        "videos":           videos,
        "generated_at":     date.today().isoformat(),
    }


def write_stats_to_queues(stats: dict, weeks_back: int = 4):
    """Salva métricas do YouTube de volta nos arquivos de fila."""
    queue_dir = BASE_DIR / "queue"
    today = date.today()
    updated = 0

    for i in range(weeks_back):
        check = today - timedelta(weeks=i)
        iso_year, iso_week, _ = check.isocalendar()
        qf = queue_dir / f"{iso_year}_W{iso_week:02d}.json"
        if not qf.exists():
            continue

        entries = json.loads(qf.read_text(encoding="utf-8"))
        changed = False
        for e in entries:
            vid_id = e.get("video_id", "")
            if vid_id and vid_id in stats:
                e["metrics"] = stats[vid_id]
                changed = True
                updated += 1

        if changed:
            qf.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")

    if updated:
        print(f"  {updated} entradas de fila atualizadas com métricas do YouTube")


def run(weeks_back: int = 4) -> dict:
    print(f"[Performance Analyst] Coletando métricas das últimas {weeks_back} semanas...")

    entries = collect_done_entries(weeks_back)
    print(f"  {len(entries)} vídeos 'done' encontrados nas filas locais")

    if not entries:
        report = analyze([], {})
        print("  Sem dados suficientes — usando horários padrão: 8h, 14h, 20h")
    else:
        try:
            yt = _youtube_client()
            channel_videos, all_stats = fetch_all_channel_stats(yt)
            print(f"  {len(channel_videos)} vídeos encontrados no canal")
            print(f"  {len(all_stats)} com estatísticas do YouTube")
            report = analyze(entries, all_stats, channel_videos)
            write_stats_to_queues(all_stats, weeks_back)
        except Exception as e:
            print(f"  Aviso: não foi possível buscar stats do YouTube ({e})")
            print("  Usando dados locais (sem views)")
            report = analyze(entries, {})

    out = DATA_DIR / "performance_report.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"  Relatório salvo: {out.name}")
    print(f"  Melhores horários BRT: {report['best_hours']}")
    print(f"  Views médias: {report['avg_views']}")
    if report["top_videos"]:
        print(f"  Top vídeo: '{report['top_videos'][0]['title']}' "
              f"({report['top_videos'][0]['views']} views)")

    return report


if __name__ == "__main__":
    weeks = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    run(weeks)
