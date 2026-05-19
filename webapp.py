"""
YT Shorts Studio — painel de controle completo.
Inicie com: python webapp.py
Acesse em:  http://localhost:8080
"""

import os, json, uuid, threading, time, asyncio, re
from pathlib import Path
from datetime import date, datetime, timezone, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

app = FastAPI(title="YT Shorts Studio")
BASE_DIR   = Path(__file__).parent
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", BASE_DIR / "outputs"))
ASSETS_DIR = BASE_DIR / "assets"
QUEUE_DIR  = BASE_DIR / "queue"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
QUEUE_DIR.mkdir(exist_ok=True)

W, H         = 1080, 1920
MUSIC_VOLUME = 0.12

VOICE_IDS = {
    "rachel": "21m00Tcm4TlvDq8ikWAM",
    "adam":   "pNInz6obpgDQGcFmaJgB",
    "domi":   "AZnzlk1XvdvUeBnXmlld",
    "elli":   "MF3mGyEYCl7XYWbV9V6O",
    "josh":   "TxGEqnHWrfWFTfGW9XjX",
    "arnold": "VR6AewLTigWG4xSOukaG",
}

# ── Job tracking ───────────────────────────────────────────────────────────────
_jobs: dict = {}
_production_lock = threading.Semaphore(1)  # serializa jobs pesados: 1 render por vez

def new_job(slug: str) -> str:
    job_id = str(uuid.uuid4())[:8]
    _jobs[job_id] = {
        "id": job_id, "slug": slug, "status": "pending",
        "step": "", "progress": 0, "message": "Iniciando...",
        "result": None, "error": None,
        "created_at": datetime.now().isoformat(),
    }
    return job_id

def update_job(job_id: str, **kw):
    if job_id in _jobs:
        _jobs[job_id].update(kw)


# ── Queue helpers ──────────────────────────────────────────────────────────────

def _queue_file_for(target: date) -> Path:
    y, w, _ = target.isocalendar()
    return QUEUE_DIR / f"{y}_W{w:02d}.json"

def _read_queue(path: Path) -> list:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))

def _write_queue(path: Path, entries: list):
    path.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")


# ── Stop words (keyword extraction) ───────────────────────────────────────────
STOP_WORDS = {
    "a","an","the","and","or","but","in","on","at","to","for","of","with",
    "is","are","was","were","be","been","have","has","had","do","does","did",
    "will","would","could","should","may","might","it","its","this","that",
    "i","you","he","she","we","they","your","my","our","their","not","no",
    "so","as","if","then","there","here","just","also","only","very","more",
    "most","some","all","can","get","make","like","know","think","why","how",
    "what","when","who","which","while","after","before","every",
}
FALLBACK_QUERIES = [
    "money cash bills dark cinematic", "brain neurons glowing dark",
    "person thinking decision dark", "savings coins growing dark",
    "success wealth ambition dark", "habits morning routine dark",
    "smartphone banking finance dark", "silhouette future success dark",
    "stress anxiety money dark", "procrastination lazy couch dark",
]

CONCEPT_QUERIES = {
    "sav":       "savings coins money jar dark cinematic",
    "invest":    "investment stock market growth chart dark",
    "debt":      "debt credit card bills stress dark",
    "loan":      "loan debt signing papers dark",
    "budget":    "budget planning finance notebook dark",
    "retir":     "retirement freedom beach relax dark",
    "salary":    "salary paycheck money raise dark",
    "income":    "income paycheck cash money dark",
    "wealth":    "wealth luxury success mansion dark",
    "rich":      "wealthy luxury success dark cinematic",
    "broke":     "broke empty wallet poverty stress dark",
    "spend":     "shopping spending cart money dark",
    "inflat":    "grocery store price increase dark",
    "habit":     "morning routine daily habit dark",
    "mindset":   "brain mindset thinking focus dark",
    "decis":     "decision crossroads choice path dark",
    "stress":    "stress anxiety shadow dark",
    "fear":      "fear anxiety dark shadow",
    "freedom":   "freedom success open road bright",
    "bank":      "bank building finance professional dark",
    "mortgag":   "house real estate property dark",
    "stock":     "stock market trading screen dark",
    "market":    "financial market chart trading dark",
    "emerg":     "emergency fund safety security dark",
    "compound":  "compound interest growth exponential dark",
    "automat":   "automation system technology dark",
    "disciplin": "discipline focus determination dark",
    "credit":    "credit card payment dark cinematic",
    "paycheck":  "paycheck salary envelope money dark",
    "money":     "money cash bills wallet dark cinematic",
    "financ":    "finance professional money dark cinematic",
    "percent":   "percentage statistics numbers chart dark",
    "rule":      "rules book law text dark",
    "strateg":   "strategy planning success dark",
    "motivat":   "motivation energy determination dark",
    "success":   "success achievement celebration dark",
    "fail":      "failure disappointment dark cinematic",
    "goal":      "goal target achievement dark",
    "brain":     "brain neuron thinking psychology dark",
    "psychol":   "psychology brain mental dark cinematic",
    "behav":     "behavior choice decision dark",
    "procrast":  "procrastination lazy couch dark",
    "raise":     "salary raise promotion success dark",
    "earn":      "earning money income work dark",
    "employ":    "employment job career dark",
    "boss":      "boss office corporate dark",
    "freelanc":  "freelance remote work laptop dark",
    "passive":   "passive income stream money dark",
    "asset":     "assets wealth portfolio dark",
    "liabil":    "liability debt financial dark",
    "profit":    "profit growth success chart dark",
    "loss":      "loss failure financial dark",
    "future":    "future success vision dark cinematic",
    "time":      "time clock urgency dark cinematic",
    "trust":     "trust handshake professional dark",
    "build":     "building construction growth dark",
    "system":    "organized system process dark",
}

def _extract_query(text: str, idx: int) -> str:
    clean = re.sub(r"[^a-z\s]", "", text.lower())
    words = clean.split()
    # 1. Stem-based concept map — percorre todas as palavras do take
    for word in words:
        for stem, query in CONCEPT_QUERIES.items():
            if word.startswith(stem):
                return query
    # 2. Keyword extraction com palavras longas e não-stop
    kw = [w for w in words if len(w) > 5 and w not in STOP_WORDS]
    if len(kw) >= 2:
        return " ".join(kw[:3]) + " dark cinematic"
    return FALLBACK_QUERIES[idx % len(FALLBACK_QUERIES)]

def _subtitle(text: str) -> str:
    words = text.split()
    if len(words) <= 5:
        return text
    mid = len(words) // 2
    return " ".join(words[:mid]) + "\n" + " ".join(words[mid:mid+5])

def _split_into_takes(narration: str, num_takes: int, duration: int) -> list:
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', narration) if s.strip()]
    if not sentences:
        sentences = [narration]
    total = sum(len(s) for s in sentences)
    target = total / num_takes
    groups, cur, cur_len = [], [], 0
    for s in sentences:
        cur.append(s); cur_len += len(s)
        if cur_len >= target and len(groups) < num_takes - 1:
            groups.append(" ".join(cur)); cur, cur_len = [], 0
    if cur:
        if groups: groups[-1] += " " + " ".join(cur)
        else: groups.append(" ".join(cur))
    while len(groups) < num_takes:
        groups.append(groups[-1] if groups else narration)
    groups = groups[:num_takes]
    dur_each  = duration // num_takes
    remainder = duration - dur_each * num_takes
    takes = []
    for i, g in enumerate(groups):
        dur  = dur_each + (1 if i < remainder else 0)
        word = re.sub(r"[^a-z]", "", g.split()[0].lower())[:8] if g.split() else "part"
        takes.append({
            "slug": f"{i+1:02d}_{word}", "duration": dur,
            "subtitle": _subtitle(g), "query": _extract_query(g, i),
        })
    return takes


# ── Shared production pipeline ─────────────────────────────────────────────────

def _generate_narration(text: str, voice: str, out_path: Path):
    el_key = os.getenv("ELEVENLABS_API_KEY", "")
    if el_key.startswith("sk_"):
        from elevenlabs.client import ElevenLabs
        client = ElevenLabs(api_key=el_key)
        audio  = client.text_to_speech.convert(
            voice_id=VOICE_IDS.get(voice, VOICE_IDS["rachel"]),
            text=text, model_id="eleven_turbo_v2", output_format="mp3_44100_128",
        )
        with open(out_path, "wb") as f:
            for chunk in audio: f.write(chunk)
    else:
        import edge_tts
        async def _r():
            await edge_tts.Communicate(text, "en-US-AriaNeural").save(str(out_path))
        asyncio.run(_r())


def _download_clip(query: str, out_path: Path) -> bool:
    import requests as rq
    pexels_key = os.getenv("PEXELS_API_KEY", "")
    try:
        r = rq.get("https://api.pexels.com/videos/search",
                   headers={"Authorization": pexels_key},
                   params={"query": query, "per_page": 5, "orientation": "portrait"},
                   timeout=15)
        r.raise_for_status()
        videos = r.json().get("videos", [])
        if not videos: return False
        files = videos[0].get("video_files", [])
        vert  = [f for f in files if f.get("width", 0) < f.get("height", 1)]
        pool  = vert or files
        hd    = [f for f in pool if f.get("height", 0) <= 1080]
        best  = max(hd or pool, key=lambda f: f.get("height", 0))
        with rq.get(best["link"], stream=True, timeout=60) as resp:
            resp.raise_for_status()
            out_path.write_bytes(resp.content)
        return True
    except Exception:
        return False


def _assemble_video(work_dir: Path, takes: list, narr_path: Path,
                    bg_music: bool = True) -> Path:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    from moviepy import (
        VideoFileClip, AudioFileClip, CompositeVideoClip,
        concatenate_videoclips, ImageClip, concatenate_audioclips, CompositeAudioClip,
    )
    from moviepy.audio.fx import MultiplyVolume

    def make_sub(text, duration):
        pad, fsize = 40, 68
        font_candidates = [
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
        font = ImageFont.load_default(size=fsize)
        for fp in font_candidates:
            try: font = ImageFont.truetype(fp, fsize); break
            except: pass
        dummy = Image.new("RGBA", (1, 1))
        draw  = ImageDraw.Draw(dummy)
        bbox  = draw.multiline_textbbox((0, 0), text, font=font, align="center")
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        iw, ih = int(min(tw+pad*2, W-60)), int(th+pad*2)
        img  = Image.new("RGBA", (iw, ih), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([0,0,iw-1,ih-1], radius=18, fill=(0,0,0,180))
        cx, cy = iw//2, ih//2
        draw.multiline_text((cx+3,cy+3), text, font=font, fill=(0,0,0,200), anchor="mm", align="center")
        draw.multiline_text((cx,cy),     text, font=font, fill=(255,255,255,255), anchor="mm", align="center")
        return ImageClip(np.array(img), duration=duration).with_position(("center", H-ih-120))

    def fit_clip(clip, duration):
        dur  = min(duration, clip.duration)
        clip = clip.subclipped(0, dur)
        cw, ch = clip.size
        if cw/ch > W/H:
            clip = clip.resized(height=H); ex=(clip.w-W)/2
            clip = clip.cropped(x1=ex, x2=clip.w-ex)
        else:
            clip = clip.resized(width=W); ex=(clip.h-H)/2
            clip = clip.cropped(y1=ex, y2=clip.h-ex)
        if clip.duration < duration:
            last = clip.to_ImageClip(clip.duration-0.05).with_duration(duration-clip.duration)
            clip = concatenate_videoclips([clip, last])
        return clip.without_audio()

    narration = AudioFileClip(str(narr_path))
    audio_dur = narration.duration
    total_dec = sum(t.get("duration", 4) for t in takes)
    scale     = audio_dur / total_dec

    clips = []
    for take in takes:
        dur  = round(take.get("duration", 4) * scale, 2)
        path = work_dir / f"{take['slug']}.mp4"
        vc   = fit_clip(VideoFileClip(str(path)), dur) if path.exists() \
               else ImageClip(np.zeros((H, W, 3), dtype=np.uint8), duration=dur)
        clips.append(CompositeVideoClip([vc, make_sub(take.get("subtitle",""), dur)], size=(W, H)))

    video = concatenate_videoclips(clips, method="compose")
    bg    = ASSETS_DIR / "background.mp3"
    if bg_music and bg.exists():
        music = AudioFileClip(str(bg))
        if music.duration < audio_dur:
            music = concatenate_audioclips([music] * (int(audio_dur/music.duration)+1))
        music = music.subclipped(0, audio_dur).with_effects([MultiplyVolume(MUSIC_VOLUME)])
        video = video.with_audio(CompositeAudioClip([narration, music]))
    else:
        video = video.with_audio(narration)

    out = work_dir / "final_video.mp4"
    video.write_videofile(str(out), fps=30, codec="libx264",
                          audio_codec="aac", preset="fast",
                          ffmpeg_params=["-crf","23"], logger=None)
    return out


YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]

def _load_youtube_creds():
    import pickle
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    token_file   = BASE_DIR / "youtube_token.pkl"
    secrets_file = BASE_DIR / "youtube_client_secrets.json"

    if not secrets_file.exists():
        secrets_file.write_text(json.dumps({"installed": {
            "client_id":     os.getenv("YOUTUBE_CLIENT_ID", ""),
            "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET", ""),
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
            "auth_uri":  "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }}))

    creds = None
    if token_file.exists():
        with open(token_file, "rb") as f:
            creds = pickle.load(f)
        # Regenera se o token não tiver os dois escopos necessários
        token_scopes = set(creds.scopes or [])
        if not set(YOUTUBE_SCOPES).issubset(token_scopes):
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow  = InstalledAppFlow.from_client_secrets_file(str(secrets_file), YOUTUBE_SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "wb") as f:
            pickle.dump(creds, f)

    return creds


def _upload_youtube(video_path: Path, entry: dict) -> str:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    yt  = build("youtube", "v3", credentials=_load_youtube_creds())
    brt = timezone(timedelta(hours=-3))
    today = date.today()
    ph  = entry.get("publish_hour_brt", 18)
    pub = datetime(today.year, today.month, today.day, ph, 0, 0, tzinfo=brt).isoformat()

    body = {
        "snippet": {
            "title":           (entry.get("title") or entry["slug"])[:100],
            "description":     (entry.get("description") or "")[:5000],
            "tags":            entry.get("tags", []),
            "categoryId":      "22",
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": "private",
            "selfDeclaredMadeForKids": False,
            "publishAt": pub,
        },
    }
    media   = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True, chunksize=1024*1024)
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        _, response = request.next_chunk()
    return response["id"]


# ── Pipeline runner for queue entries ──────────────────────────────────────────

def _run_queue_production(job_id: str, entry: dict, queue_file: Path):
    slug     = entry["slug"]
    work_dir = OUTPUT_DIR / slug
    work_dir.mkdir(parents=True, exist_ok=True)

    def set_queue_status(status: str, **extra):
        entries = _read_queue(queue_file)
        for e in entries:
            if e["slug"] == slug:
                e["status"] = status
                e.update(extra)
        _write_queue(queue_file, entries)

    update_job(job_id, status="running", step="queued", progress=1,
               message="Aguardando slot de produção...")
    with _production_lock:
        try:
            # 1 — Narração
            update_job(job_id, status="running", step="narration", progress=5,
                       message="Gerando narração com ElevenLabs...")
            narr_path = work_dir / "narration.mp3"
            if not narr_path.exists():
                _generate_narration(entry["narration"], entry.get("voice","rachel"), narr_path)
            update_job(job_id, progress=15, message="Narração gerada.")

            # 2 — Clips
            takes = _split_into_takes(entry["narration"], entry.get("num_takes",12), entry.get("duration",75))
            total = len(takes)
            for i, take in enumerate(takes):
                pct = 15 + int((i/total)*45)
                update_job(job_id, progress=pct, message=f"Baixando clip {i+1}/{total}...")
                out = work_dir / f"{take['slug']}.mp4"
                if not out.exists():
                    _download_clip(take.get("query","abstract dark cinematic"), out)
                time.sleep(0.3)
            update_job(job_id, progress=60, message="Clips prontos. Editando vídeo...")

            # 3 — Edição
            update_job(job_id, step="editing", progress=62, message="Montando vídeo (3–5 min)...")
            final = work_dir / "final_video.mp4"
            # apaga arquivo parcial de render anterior com falha
            if final.exists() and final.stat().st_size < 5_000_000:
                final.unlink()
            if not final.exists():
                final = _assemble_video(work_dir, takes, narr_path)
            size_mb = round(final.stat().st_size / (1024*1024), 1)
            update_job(job_id, progress=88, message=f"Vídeo pronto ({size_mb} MB). Subindo para o YouTube...")

            # 4 — Upload YouTube
            update_job(job_id, step="upload", progress=90, message="Enviando para o YouTube...")
            video_id = _upload_youtube(final, entry)
            yt_url   = f"https://www.youtube.com/shorts/{video_id}"
            update_job(job_id, progress=100, message=f"Publicado! {yt_url}")

            # 5 — Marcar done
            update_job(job_id, status="done", step="done",
                       result={"file": str(final), "size_mb": size_mb,
                               "youtube_url": yt_url, "video_id": video_id})
            set_queue_status("done", video_id=video_id, youtube_url=yt_url,
                             produced_at=datetime.now().isoformat(), error_msg="")

        except Exception as e:
            # remove render parcial para permitir re-tentativa limpa
            final = work_dir / "final_video.mp4"
            if final.exists() and final.stat().st_size < 5_000_000:
                final.unlink()
            update_job(job_id, status="error", message=str(e), error=str(e))
            set_queue_status("error", error_msg=str(e))


# ── Pipeline runner for single (avulso) production ────────────────────────────

class ProduceRequest(BaseModel):
    topic_slug: str
    narration: str
    takes: list
    voice: str = "rachel"
    background_music: bool = True

def _run_single_production(job_id: str, req: ProduceRequest):
    work_dir = OUTPUT_DIR / req.topic_slug
    work_dir.mkdir(parents=True, exist_ok=True)
    try:
        update_job(job_id, status="running", step="narration", progress=5,
                   message="Gerando narração...")
        narr = work_dir / "narration.mp3"
        if not narr.exists():
            _generate_narration(req.narration, req.voice, narr)
        update_job(job_id, progress=15, message="Narração gerada.")

        total = len(req.takes)
        for i, take in enumerate(req.takes):
            pct = 15 + int((i/total)*45)
            update_job(job_id, progress=pct, message=f"Baixando clip {i+1}/{total}...")
            out = work_dir / f"{take['slug']}.mp4"
            if not out.exists():
                _download_clip(take.get("query","abstract dark cinematic"), out)
            time.sleep(0.3)
        update_job(job_id, progress=60, message="Editando vídeo...")

        update_job(job_id, step="editing", progress=62, message="Montando vídeo (3–5 min)...")
        final = _assemble_video(work_dir, req.takes, narr, req.background_music)
        size_mb = round(final.stat().st_size/(1024*1024), 1)
        audio_s = round(__import__("moviepy").AudioFileClip(str(narr)).duration, 1)

        update_job(job_id, status="done", step="done", progress=100,
                   message="Vídeo pronto!",
                   result={"file": str(final), "size_mb": size_mb,
                           "duration_s": audio_s, "topic_slug": req.topic_slug})
    except Exception as e:
        update_job(job_id, status="error", message=str(e), error=str(e))


# ── API — Queue ────────────────────────────────────────────────────────────────

def _monday_of_week(year: int, week: int) -> date:
    jan4 = date(year, 1, 4)
    return jan4 - timedelta(days=jan4.weekday()) + timedelta(weeks=week - 1)

def _create_queue_file(target: date, overwrite: bool = False) -> Path:
    y, w, _ = target.isocalendar()
    qf  = QUEUE_DIR / f"{y}_W{w:02d}.json"
    if qf.exists() and not overwrite:
        return qf
    mon = _monday_of_week(y, w)
    day_names = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
    day_pt    = ["Segunda","Terca","Quarta","Quinta","Sexta","Sabado","Domingo"]
    day_slugs = ["mon","tue","wed","thu","fri","sat","sun"]
    entries = []
    for i in range(7):
        d = mon + timedelta(days=i)
        entries.append({
            "day": day_names[i], "day_pt": day_pt[i],
            "date": d.isoformat(),
            "slug": f"video_{day_slugs[i]}_{d.strftime('%m%d')}",
            "narration": "", "num_takes": 12, "duration": 75, "voice": "rachel",
            "title": "", "description": "", "tags": [],
            "publish_hour_brt": 18, "status": "pending", "error_msg": "",
        })
    _write_queue(qf, entries)
    return qf


def _find_queue_for_slug(slug: str):
    """Busca o arquivo de fila e entries que contém o slug."""
    for qf in sorted(QUEUE_DIR.glob("*.json"), reverse=True):
        entries = _read_queue(qf)
        if any(e["slug"] == slug for e in entries):
            return qf, entries
    return None, None


@app.get("/api/queue")
async def get_queue(week_offset: int = 0):
    target  = date.today() + timedelta(weeks=week_offset)
    qf      = _queue_file_for(target)
    entries = _read_queue(qf)
    y, w, _ = target.isocalendar()

    next_week   = target + timedelta(weeks=1)
    ny, nw, _   = next_week.isocalendar()
    next_qf     = _queue_file_for(next_week)
    next_monday = _monday_of_week(ny, nw)

    prev_week   = target - timedelta(weeks=1)
    py, pw, _   = prev_week.isocalendar()
    prev_qf     = _queue_file_for(prev_week)

    return JSONResponse({
        "week_file": qf.name, "iso_week": w, "iso_year": y,
        "entries": entries, "week_offset": week_offset,
        "next_week": {
            "iso_week": nw, "iso_year": ny,
            "exists": next_qf.exists(),
            "monday": next_monday.isoformat(),
        },
        "prev_week": {
            "iso_week": pw, "iso_year": py,
            "exists": prev_qf.exists(),
        },
    })


class QueueEntryUpdate(BaseModel):
    narration: str = ""
    title: str = ""
    description: str = ""
    tags: list = []
    voice: str = "rachel"
    publish_hour_brt: int = 18

@app.put("/api/queue/{slug}")
async def update_queue_entry(slug: str, req: QueueEntryUpdate):
    qf, entries = _find_queue_for_slug(slug)
    if qf is None:
        raise HTTPException(status_code=404, detail=f"Entrada {slug} não encontrada")
    for e in entries:
        if e["slug"] == slug:
            e.update(req.model_dump())
            _write_queue(qf, entries)
            return JSONResponse({"ok": True})


@app.post("/api/queue/{slug}/produce")
async def produce_queue_entry(slug: str):
    qf, entries = _find_queue_for_slug(slug)
    if qf is None:
        raise HTTPException(status_code=404, detail=f"Entrada {slug} não encontrada")
    entry = next((e for e in entries if e["slug"] == slug), None)
    if not entry.get("narration","").strip():
        raise HTTPException(status_code=422, detail="Narração vazia — preencha antes de produzir")
    if entry.get("status") == "producing":
        raise HTTPException(status_code=409, detail="Já em produção")

    for e in entries:
        if e["slug"] == slug: e["status"] = "producing"
    _write_queue(qf, entries)

    job_id = new_job(slug)
    threading.Thread(target=_run_queue_production,
                     args=(job_id, entry, qf), daemon=True).start()
    return JSONResponse({"job_id": job_id})


@app.post("/api/queue/{slug}/reset")
async def reset_queue_entry(slug: str):
    qf, entries = _find_queue_for_slug(slug)
    if qf is None:
        raise HTTPException(status_code=404, detail=f"Entrada {slug} não encontrada")
    for e in entries:
        if e["slug"] == slug:
            if e.get("status") != "producing":
                raise HTTPException(status_code=409, detail="Status não é 'producing'")
            e["status"]    = "pending"
            e["error_msg"] = ""
    _write_queue(qf, entries)
    return JSONResponse({"ok": True})


@app.post("/api/queue/create-week")
async def create_week(week_offset: int = 0):
    """Cria fila vazia (formato legado, sem agentes)."""
    target = date.today() + timedelta(weeks=week_offset)
    qf = _create_queue_file(target)
    y, w, _ = target.isocalendar()
    return JSONResponse({"ok": True, "file": qf.name, "iso_week": w, "iso_year": y})


@app.post("/api/agents/generate-week")
async def generate_week(week_offset: int = 1, skip_analyst: bool = False):
    """Roda Performance Analyst + Script Writer para gerar a fila da semana alvo."""
    import sys as _sys
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not anthropic_key:
        raise HTTPException(status_code=400, detail="ANTHROPIC_API_KEY não configurado no .env")

    target = date.today() + timedelta(weeks=week_offset)
    y, w, _ = target.isocalendar()
    qf = QUEUE_DIR / f"{y}_W{w:02d}.json"
    if qf.exists():
        raise HTTPException(status_code=409,
            detail=f"Fila {qf.name} já existe. Delete-a primeiro para regenerar.")

    job_id = new_job(f"agents_w{w}")

    def _run():
        try:
            update_job(job_id, status="running", step="analyst", progress=10,
                       message="Performance Analyst: coletando métricas...")
            if not skip_analyst:
                _sys.path.insert(0, str(BASE_DIR))
                from agents import performance_analyst
                performance_analyst.run()

            update_job(job_id, step="writer", progress=40,
                       message="Script Writer: gerando 21 roteiros com Claude...")
            from agents import script_writer
            queue_file = script_writer.run()

            update_job(job_id, status="done", step="done", progress=100,
                       message=f"Fila {queue_file.name} criada com 21 roteiros!",
                       result={"file": queue_file.name, "iso_week": w, "iso_year": y})
        except Exception as e:
            update_job(job_id, status="error", message=str(e), error=str(e))

    threading.Thread(target=_run, daemon=True).start()
    return JSONResponse({"job_id": job_id, "iso_week": w, "iso_year": y})


@app.get("/api/queue/job/{slug}")
async def queue_job_by_slug(slug: str):
    job = next((j for j in _jobs.values() if j.get("slug") == slug), None)
    if not job:
        raise HTTPException(status_code=404, detail="Nenhum job ativo para este slug")
    return JSONResponse(job)


# ── API — Script (Produção Avulsa) ─────────────────────────────────────────────

class PrepareRequest(BaseModel):
    narration: str
    num_takes: int = 12
    duration: int = 75
    topic: str = ""

@app.post("/api/script/prepare")
async def prepare_script(req: PrepareRequest):
    try:
        takes = _split_into_takes(req.narration.strip(), req.num_takes, req.duration)
        topic = req.topic or "video"
        slug  = "".join(c for c in topic.lower().replace(" ","_") if c.isalnum() or c=="_")[:40]
        return JSONResponse({
            "narration": req.narration.strip(), "takes": takes,
            "title_options": [
                f"{topic} — The Truth Nobody Tells You",
                f"Why {topic} Destroys Most People",
                f"Stop Believing This About {topic}",
            ],
            "description": f"In this video, we explore {topic} using psychology and neuroscience.\n\n#psychology #mindset #shorts",
            "tags": ["psychology","mindset","finance","behavior","neuroscience","habits","motivation","shorts"],
            "suggested_slug": slug or "my_video",
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class TranslateRequest(BaseModel):
    text: str

@app.post("/api/script/translate")
async def translate_script(req: TranslateRequest):
    try:
        from deep_translator import GoogleTranslator
        t = req.text
        if len(t) <= 4500:
            translated = GoogleTranslator(source="en", target="pt").translate(t)
        else:
            chunks = [t[i:i+4500] for i in range(0, len(t), 4500)]
            translated = " ".join(GoogleTranslator(source="en", target="pt").translate(c) for c in chunks)
        return JSONResponse({"translated": translated})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/produce/start")
async def start_production(req: ProduceRequest):
    slug = "".join(c for c in req.topic_slug.lower().replace(" ","_") if c.isalnum() or c=="_")
    req.topic_slug = slug or f"video_{int(time.time())}"
    job_id = new_job(req.topic_slug)
    threading.Thread(target=_run_single_production, args=(job_id, req), daemon=True).start()
    return JSONResponse({"job_id": job_id, "topic_slug": req.topic_slug})


@app.get("/api/produce/status/{job_id}")
async def get_status(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    return JSONResponse(job)


@app.post("/api/metrics/refresh")
async def refresh_metrics(week_offset: int = 0):
    from googleapiclient.discovery import build

    target  = date.today() + timedelta(weeks=week_offset)
    qf      = _queue_file_for(target)
    entries = _read_queue(qf)
    if not entries:
        raise HTTPException(status_code=404, detail="Fila não encontrada para esta semana")

    done = [e for e in entries if e.get("status") == "done" and e.get("video_id")]
    if not done:
        return JSONResponse({"ok": True, "updated": 0, "message": "Nenhum vídeo publicado esta semana"})

    try:
        yt       = build("youtube", "v3", credentials=_load_youtube_creds())
        ids      = [e["video_id"] for e in done]
        response = yt.videos().list(part="statistics", id=",".join(ids)).execute()

        stats_map = {item["id"]: item.get("statistics", {}) for item in response.get("items", [])}

        updated = 0
        for e in entries:
            vid_id = e.get("video_id")
            if vid_id and vid_id in stats_map:
                s = stats_map[vid_id]
                e["metrics"] = {
                    "views":      int(s.get("viewCount",    0)),
                    "likes":      int(s.get("likeCount",    0)),
                    "comments":   int(s.get("commentCount", 0)),
                    "fetched_at": datetime.now().isoformat(),
                }
                updated += 1

        _write_queue(qf, entries)
        return JSONResponse({"ok": True, "updated": updated})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _queue_meta_index() -> dict:
    """Retorna dict slug -> {title, youtube_url, date} lendo todos os arquivos de fila."""
    index = {}
    for qf in QUEUE_DIR.glob("*.json"):
        for e in _read_queue(qf):
            index[e["slug"]] = {
                "title":       e.get("title") or "",
                "youtube_url": e.get("youtube_url") or "",
                "date":        e.get("date") or "",
            }
    return index


@app.get("/api/videos")
async def list_videos():
    meta  = _queue_meta_index()
    videos = []
    if OUTPUT_DIR.exists():
        for folder in sorted(OUTPUT_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            if not folder.is_dir(): continue
            final = folder / "final_video.mp4"
            m = meta.get(folder.name, {})
            videos.append({
                "slug":        folder.name,
                "has_video":   final.exists(),
                "size_mb":     round(final.stat().st_size/1024/1024, 1) if final.exists() else None,
                "created":     datetime.fromtimestamp(folder.stat().st_mtime).strftime("%d/%m %H:%M"),
                "title":       m.get("title", ""),
                "youtube_url": m.get("youtube_url", ""),
                "date":        m.get("date", ""),
            })
    return JSONResponse(videos)


@app.get("/api/download/{slug}")
async def download_video(slug: str):
    path = OUTPUT_DIR / slug / "final_video.mp4"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    return FileResponse(str(path), media_type="video/mp4", filename=f"{slug}_final.mp4")


@app.get("/api/video/{slug}/preview")
async def preview_video(slug: str):
    path = OUTPUT_DIR / slug / "final_video.mp4"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    return FileResponse(str(path), media_type="video/mp4")


# ── Static + index ─────────────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

@app.get("/favicon.ico")
async def favicon():
    from fastapi.responses import Response
    svg = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="#f59e0b"/><text x="16" y="23" font-size="20" text-anchor="middle" fill="#000">&#127909;</text></svg>'
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/")
async def index():
    return FileResponse(str(BASE_DIR / "static" / "index.html"))


# ── API — Advisor ─────────────────────────────────────────────────────────────

class AdvisorChatRequest(BaseModel):
    message: str
    history: list = []


@app.post("/api/advisor/chat")
async def advisor_chat(req: AdvisorChatRequest):
    """Chat streaming com o Advisor Agent via SSE."""
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not anthropic_key:
        raise HTTPException(status_code=400, detail="ANTHROPIC_API_KEY não configurado")

    import sys as _sys
    _sys.path.insert(0, str(BASE_DIR))
    from agents.advisor import chat_stream

    def generate():
        try:
            for chunk in chat_stream(req.message, req.history):
                # SSE format
                safe = chunk.replace("\n", "\\n")
                yield f"data: {safe}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "X-Accel-Buffering": "no"})


@app.post("/api/advisor/weekly")
async def advisor_weekly():
    """Roda a orquestração semanal do Advisor em background."""
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not anthropic_key:
        raise HTTPException(status_code=400, detail="ANTHROPIC_API_KEY não configurado")

    job_id = new_job("advisor_weekly")

    def _run():
        import sys as _sys
        _sys.path.insert(0, str(BASE_DIR))
        try:
            update_job(job_id, status="running", step="advisor", progress=10,
                       message="Advisor analisando canal...")
            from agents.advisor import orchestrate_weekly
            report = orchestrate_weekly()
            update_job(job_id, status="done", step="done", progress=100,
                       message="Orquestração concluída! Fila gerada com estratégia do Advisor.",
                       result={"steps": report.get("steps", []),
                               "strategy_preview": (report.get("strategy") or "")[:300]})
        except Exception as e:
            update_job(job_id, status="error", message=str(e), error=str(e))

    threading.Thread(target=_run, daemon=True).start()
    return JSONResponse({"job_id": job_id})


if __name__ == "__main__":
    import uvicorn, webbrowser
    print("=" * 50)
    print("  YT Shorts Studio")
    print("  http://localhost:8080")
    print("=" * 50)
    webbrowser.open("http://localhost:8080")
    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="warning")
