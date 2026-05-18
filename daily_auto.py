"""
Automação diária: lê a entrada de hoje na fila semanal,
produz o vídeo e sobe para o YouTube no horário agendado.

Uso:
  python daily_auto.py            # produção normal
  python daily_auto.py --dry-run  # testa sem produzir nem subir
  python daily_auto.py --skip-upload  # produz mas não sobe
"""

import os, sys, json, time, asyncio, logging, argparse
from pathlib import Path
from datetime import date, datetime, timezone, timedelta
import re

from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

# ── Configuração de log ────────────────────────────────────────────────────────
log_dir   = BASE_DIR / "logs"
log_dir.mkdir(exist_ok=True)
today_str = date.today().isoformat()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s  %(message)s",
    handlers=[
        logging.FileHandler(log_dir / f"{today_str}.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("daily_auto")

# ── Constantes ────────────────────────────────────────────────────────────────
OUTPUT_DIR   = Path(os.getenv("OUTPUT_DIR", BASE_DIR / "outputs"))
ASSETS_DIR   = BASE_DIR / "assets"
QUEUE_DIR    = BASE_DIR / "queue"
W, H         = 1080, 1920
MUSIC_VOLUME = 0.12

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

# Mapeamento stem → query visual para Pexels
# Chave = prefixo (stem) da palavra; valor = query com intenção visual clara
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
    "work":      "work professional office dark cinematic",
    "employ":    "employment job career dark",
    "boss":      "boss office corporate dark",
    "freelanc":  "freelance remote work laptop dark",
    "passive":   "passive income stream money dark",
    "asset":     "assets wealth portfolio dark",
    "liabil":    "liability debt financial dark",
    "profit":    "profit growth success chart dark",
    "loss":      "loss failure financial dark",
    "number":    "finance numbers calculator dark",
    "future":    "future success vision dark cinematic",
    "time":      "time clock urgency dark cinematic",
    "trust":     "trust handshake professional dark",
    "build":     "building construction growth dark",
    "system":    "organized system process dark",
}


# ── Fila ──────────────────────────────────────────────────────────────────────

def find_today_entry() -> tuple:
    """Retorna (queue_file, entries, entry, index) para hoje."""
    today = date.today()
    iso_year, iso_week, _ = today.isocalendar()
    queue_file = QUEUE_DIR / f"{iso_year}_W{iso_week:02d}.json"

    if not queue_file.exists():
        raise FileNotFoundError(
            f"Arquivo de fila não encontrado: {queue_file}\n"
            f"Crie o arquivo para a semana {iso_week} de {iso_year} "
            f"ou rode: python make_queue.py"
        )

    entries = json.loads(queue_file.read_text(encoding="utf-8"))
    today_iso = today.isoformat()

    for i, entry in enumerate(entries):
        if entry.get("date") == today_iso:
            return queue_file, entries, entry, i

    raise ValueError(
        f"Nenhuma entrada encontrada para hoje ({today_iso}) em {queue_file.name}"
    )


def save_queue(queue_file: Path, entries: list):
    queue_file.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")


# ── TTS ───────────────────────────────────────────────────────────────────────

VOICE_IDS = {
    "rachel": "21m00Tcm4TlvDq8ikWAM",
    "adam":   "pNInz6obpgDQGcFmaJgB",
    "domi":   "AZnzlk1XvdvUeBnXmlld",
    "elli":   "MF3mGyEYCl7XYWbV9V6O",
    "josh":   "TxGEqnHWrfWFTfGW9XjX",
    "arnold": "VR6AewLTigWG4xSOukaG",
}


def generate_narration(text: str, voice: str, out_path: Path):
    el_key = os.getenv("ELEVENLABS_API_KEY", "")

    if el_key.startswith("sk_"):
        log.info("  TTS: ElevenLabs")
        from elevenlabs.client import ElevenLabs
        client   = ElevenLabs(api_key=el_key)
        voice_id = VOICE_IDS.get(voice, VOICE_IDS["rachel"])
        audio = client.text_to_speech.convert(
            voice_id=voice_id, text=text,
            model_id="eleven_turbo_v2", output_format="mp3_44100_128",
        )
        with open(out_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)
    else:
        log.info("  TTS: edge-tts (fallback gratuito)")
        import edge_tts
        async def _run():
            comm = edge_tts.Communicate(text, "en-US-AriaNeural")
            await comm.save(str(out_path))
        asyncio.run(_run())


# ── Shotlist automático ───────────────────────────────────────────────────────

def _extract_query(text: str, index: int) -> str:
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
    return FALLBACK_QUERIES[index % len(FALLBACK_QUERIES)]


def _make_subtitle(text: str) -> str:
    words = text.split()
    if len(words) <= 5:
        return text
    mid = len(words) // 2
    return " ".join(words[:mid]) + "\n" + " ".join(words[mid:mid + 5])


def auto_shotlist(narration: str, num_takes: int, duration: int) -> list:
    """Divide a narração em takes balanceados por tamanho."""
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', narration) if s.strip()]
    if not sentences:
        sentences = [narration]

    total_chars  = sum(len(s) for s in sentences)
    target       = total_chars / num_takes
    groups, cur, cur_len = [], [], 0

    for sent in sentences:
        cur.append(sent)
        cur_len += len(sent)
        if cur_len >= target and len(groups) < num_takes - 1:
            groups.append(" ".join(cur))
            cur, cur_len = [], 0
    if cur:
        if groups:
            groups[-1] += " " + " ".join(cur)
        else:
            groups.append(" ".join(cur))

    while len(groups) < num_takes:
        groups.append(groups[-1] if groups else narration)
    groups = groups[:num_takes]

    dur_each  = duration // num_takes
    remainder = duration - dur_each * num_takes

    takes = []
    for i, group in enumerate(groups):
        dur  = dur_each + (1 if i < remainder else 0)
        word = re.sub(r"[^a-z]", "", group.split()[0].lower())[:8] if group.split() else "part"
        takes.append({
            "slug":     f"{i+1:02d}_{word}",
            "duration": dur,
            "subtitle": _make_subtitle(group),
            "query":    _extract_query(group, i),
        })
    return takes


# ── Download de clips ─────────────────────────────────────────────────────────

def download_clip(query: str, out_path: Path) -> bool:
    import requests
    pexels_key = os.getenv("PEXELS_API_KEY", "")
    try:
        r = requests.get(
            "https://api.pexels.com/videos/search",
            headers={"Authorization": pexels_key},
            params={"query": query, "per_page": 5, "orientation": "portrait"},
            timeout=15,
        )
        r.raise_for_status()
        videos = r.json().get("videos", [])
        if not videos:
            return False
        files = videos[0].get("video_files", [])
        vert  = [f for f in files if f.get("width", 0) < f.get("height", 1)]
        best  = max(vert or files, key=lambda f: f.get("height", 0))
        with requests.get(best["link"], stream=True, timeout=60) as resp:
            resp.raise_for_status()
            out_path.write_bytes(resp.content)
        return True
    except Exception as e:
        log.warning(f"    Clip falhou ({query}): {e}")
        return False


# ── Edição de vídeo ───────────────────────────────────────────────────────────

def edit_video(work_dir: Path, takes: list, narr_path: Path) -> Path:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    from moviepy import (
        VideoFileClip, AudioFileClip, CompositeVideoClip,
        concatenate_videoclips, ImageClip, concatenate_audioclips, CompositeAudioClip,
    )
    from moviepy.audio.fx import MultiplyVolume

    def make_subtitle(text, duration):
        pad, fsize = 40, 68
        font_candidates = [
            "C:/Windows/Fonts/arialbd.ttf",           # Windows
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Ubuntu
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",          # Ubuntu fallback
        ]
        font = ImageFont.load_default(size=fsize)
        for path in font_candidates:
            try: font = ImageFont.truetype(path, fsize); break
            except: pass
        dummy = Image.new("RGBA", (1, 1))
        draw  = ImageDraw.Draw(dummy)
        bbox  = draw.multiline_textbbox((0, 0), text, font=font, align="center")
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        iw = int(min(tw + pad * 2, W - 60))
        ih = int(th + pad * 2)
        img  = Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([0, 0, iw - 1, ih - 1], radius=18, fill=(0, 0, 0, 180))
        cx, cy = iw // 2, ih // 2
        draw.multiline_text((cx + 3, cy + 3), text, font=font, fill=(0, 0, 0, 200),
                            anchor="mm", align="center")
        draw.multiline_text((cx, cy), text, font=font, fill=(255, 255, 255, 255),
                            anchor="mm", align="center")
        return (ImageClip(np.array(img), duration=duration)
                .with_position(("center", H - ih - 120)))

    def fit_clip(clip, duration):
        dur  = min(duration, clip.duration)
        clip = clip.subclipped(0, dur)
        cw, ch = clip.size
        if cw / ch > W / H:
            clip = clip.resized(height=H)
            ex   = (clip.w - W) / 2
            clip = clip.cropped(x1=ex, x2=clip.w - ex)
        else:
            clip = clip.resized(width=W)
            ex   = (clip.h - H) / 2
            clip = clip.cropped(y1=ex, y2=clip.h - ex)
        if clip.duration < duration:
            last = clip.to_ImageClip(clip.duration - 0.05).with_duration(duration - clip.duration)
            clip = concatenate_videoclips([clip, last])
        return clip.without_audio()

    narration = AudioFileClip(str(narr_path))
    audio_dur = narration.duration
    total_declared = sum(t["duration"] for t in takes)
    scale = audio_dur / total_declared

    final_clips = []
    for i, take in enumerate(takes, 1):
        slug = take["slug"]
        dur  = round(take["duration"] * scale, 2)
        path = work_dir / f"{slug}.mp4"

        if not path.exists():
            log.warning(f"  [{i:02d}] {slug}.mp4 ausente — fundo preto")
            black = np.zeros((H, W, 3), dtype=np.uint8)
            vc = ImageClip(black, duration=dur)
        else:
            vc = fit_clip(VideoFileClip(str(path)), dur)

        sub  = make_subtitle(take["subtitle"], dur)
        comp = CompositeVideoClip([vc, sub], size=(W, H))
        final_clips.append(comp)
        log.info(f"  [{i:02d}/{len(takes)}] {slug} — {dur:.1f}s")

    video = concatenate_videoclips(final_clips, method="compose")

    bg_path = ASSETS_DIR / "background.mp3"
    if bg_path.exists():
        music_raw = AudioFileClip(str(bg_path))
        if music_raw.duration < audio_dur:
            loops     = int(audio_dur / music_raw.duration) + 1
            music_raw = concatenate_audioclips([music_raw] * loops)
        music = (music_raw.subclipped(0, audio_dur)
                 .with_effects([MultiplyVolume(MUSIC_VOLUME)]))
        mixed = CompositeAudioClip([narration, music])
        video = video.with_audio(mixed)
        log.info(f"  Musica de fundo: {bg_path.name} ({int(MUSIC_VOLUME*100)}%)")
    else:
        video = video.with_audio(narration)
        log.warning("  Sem musica de fundo (coloque assets/background.mp3 para ativar)")

    output = work_dir / "final_video.mp4"
    video.write_videofile(
        str(output), fps=30, codec="libx264", audio_codec="aac",
        preset="fast", ffmpeg_params=["-crf", "23"], logger="bar",
    )
    return output


# ── Upload YouTube ─────────────────────────────────────────────────────────────

def upload_youtube(video_path: Path, entry: dict) -> str:
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN", "")

    if refresh_token:
        # Modo cloud (GitHub Actions): usa refresh token da env var
        from google.oauth2.credentials import Credentials
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("YOUTUBE_CLIENT_ID", ""),
            client_secret=os.getenv("YOUTUBE_CLIENT_SECRET", ""),
        )
        creds.refresh(Request())
    else:
        # Modo local: usa pickle salvo pelo OAuth interativo
        import pickle
        from google_auth_oauthlib.flow import InstalledAppFlow
        SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
        token_file     = BASE_DIR / "youtube_token.pkl"
        client_secrets = BASE_DIR / "youtube_client_secrets.json"
        if not client_secrets.exists():
            client_secrets.write_text(json.dumps({"installed": {
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
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow  = InstalledAppFlow.from_client_secrets_file(str(client_secrets), SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_file, "wb") as f:
                pickle.dump(creds, f)

    yt = build("youtube", "v3", credentials=creds)

    # Horário de publicação: hoje às publish_hour_brt no fuso BRT (UTC-3)
    publish_hour = entry.get("publish_hour_brt", 18)
    today        = date.today()
    brt          = timezone(timedelta(hours=-3))
    publish_dt   = datetime(today.year, today.month, today.day, publish_hour, 0, 0, tzinfo=brt)

    body = {
        "snippet": {
            "title":           (entry.get("title") or entry["slug"])[:100],
            "description":     (entry.get("description") or "")[:5000],
            "tags":            entry.get("tags", []),
            "categoryId":      "22",
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus":           "private",
            "selfDeclaredMadeForKids": False,
            "publishAt":               publish_dt.isoformat(),
        },
    }

    media   = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True, chunksize=1024 * 1024)
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        _, response = request.next_chunk()

    return response["id"]


# ── Main ──────────────────────────────────────────────────────────────────────

def ensure_next_week_queue():
    """Se hoje é domingo, cria automaticamente a fila da próxima semana."""
    today = date.today()
    if today.weekday() != 6:   # 6 = domingo
        return
    next_week = today + timedelta(days=7)
    iso_year, iso_week, _ = next_week.isocalendar()
    queue_file = QUEUE_DIR / f"{iso_year}_W{iso_week:02d}.json"
    if queue_file.exists():
        return

    mon = next_week - timedelta(days=next_week.weekday())
    day_names = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
    day_pt    = ["Segunda","Terca","Quarta","Quinta","Sexta","Sabado","Domingo"]
    day_slugs = ["mon","tue","wed","thu","fri","sat","sun"]
    entries = []
    for i in range(7):
        d = mon + timedelta(days=i)
        entries.append({
            "day": day_names[i], "day_pt": day_pt[i], "date": d.isoformat(),
            "slug": f"video_{day_slugs[i]}_{d.strftime('%m%d')}",
            "narration": "", "num_takes": 12, "duration": 75, "voice": "rachel",
            "title": "", "description": "", "tags": [],
            "publish_hour_brt": 18, "status": "pending", "error_msg": "",
        })
    queue_file.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info(f"Fila da semana {iso_week} criada automaticamente: {queue_file.name}")


def main():
    parser = argparse.ArgumentParser(description="Automação diária de vídeo")
    parser.add_argument("--dry-run",      action="store_true", help="Mostra o que faria, sem produzir")
    parser.add_argument("--skip-upload",  action="store_true", help="Produz mas nao sobe para o YouTube")
    parser.add_argument("--force",        action="store_true", help="Reproduz mesmo se status for 'done'")
    args = parser.parse_args()

    log.info("=" * 60)
    log.info(f"DAILY AUTO  {date.today().isoformat()}")
    log.info("=" * 60)

    # Domingo: cria fila da próxima semana automaticamente
    ensure_next_week_queue()

    # ── 1. Carregar entrada de hoje
    try:
        queue_file, entries, entry, idx = find_today_entry()
    except (FileNotFoundError, ValueError) as e:
        log.error(str(e))
        sys.exit(1)

    log.info(f"Entrada: {entry['slug']} | status: {entry['status']}")

    if entry["status"] == "producing" and not args.force:
        log.info("Status 'producing' — ja esta em producao. Use --force para reproduzir.")
        return
    if entry["status"] == "done" and not args.force:
        log.info("Status 'done' — video ja produzido. Use --force para reproduzir.")
        return
    if not entry.get("narration", "").strip():
        if args.dry_run:
            log.warning("DRY-RUN: narracao vazia — preencha o campo 'narration' antes de rodar.")
            return
        log.error("Narracao vazia! Preencha o campo 'narration' no JSON da fila.")
        entries[idx]["status"]    = "error"
        entries[idx]["error_msg"] = "Narracao vazia"
        save_queue(queue_file, entries)
        sys.exit(1)

    if args.dry_run:
        takes = auto_shotlist(entry["narration"], entry.get("num_takes", 12), entry.get("duration", 75))
        log.info(f"DRY-RUN: {len(takes)} takes | voz: {entry.get('voice','rachel')} | "
                 f"upload: {entry.get('publish_hour_brt',18)}h BRT")
        for t in takes[:3]:
            log.info(f"  {t['slug']} ({t['duration']}s) — {t['query']}")
        log.info("  ...")
        return

    # ── 2. Marcar como produzindo
    entries[idx]["status"] = "producing"
    save_queue(queue_file, entries)

    work_dir = OUTPUT_DIR / entry["slug"]
    work_dir.mkdir(parents=True, exist_ok=True)

    try:
        # ── 3. Narração
        narr_path = work_dir / "narration.mp3"
        if narr_path.exists():
            log.info("[1/4] Narracao ja existe — pulando TTS")
        else:
            log.info("[1/4] Gerando narracao...")
            generate_narration(entry["narration"], entry.get("voice", "rachel"), narr_path)
            log.info(f"  OK — {narr_path.stat().st_size // 1024} KB")

        # ── 4. Shotlist + download de clips
        takes = auto_shotlist(entry["narration"], entry.get("num_takes", 12), entry.get("duration", 75))
        log.info(f"[2/4] Baixando {len(takes)} clips do Pexels...")
        for i, take in enumerate(takes):
            slug  = take["slug"]
            query = take.get("query", "abstract dark cinematic")
            out   = work_dir / f"{slug}.mp4"
            if out.exists():
                log.info(f"  [{i+1:02d}/{len(takes)}] {slug} [cache]")
                continue
            ok = download_clip(query, out)
            log.info(f"  [{i+1:02d}/{len(takes)}] {slug} {'OK' if ok else 'PRETO (clip nao encontrado)'}")
            time.sleep(0.3)

        # ── 5. Edição
        final_path = work_dir / "final_video.mp4"
        if final_path.exists() and not args.force:
            log.info("[3/4] final_video.mp4 ja existe — pulando edicao")
        else:
            log.info("[3/4] Editando video (3-5 min)...")
            final_path = edit_video(work_dir, takes, narr_path)
        size_mb = final_path.stat().st_size / (1024 * 1024)
        log.info(f"  OK — {size_mb:.1f} MB")

        # ── 6. Upload YouTube
        if args.skip_upload:
            log.info("[4/4] --skip-upload ativo — upload ignorado")
            video_id = ""
            yt_url   = f"file://{final_path}"
        else:
            log.info("[4/4] Fazendo upload para o YouTube...")
            video_id = upload_youtube(final_path, entry)
            yt_url   = f"https://www.youtube.com/shorts/{video_id}"
            log.info(f"  OK — {yt_url} (agendado {entry.get('publish_hour_brt', 18)}h BRT)")

        # ── 7. Marcar como done
        entries[idx].update({
            "status":      "done",
            "video_id":    video_id,
            "youtube_url": yt_url,
            "produced_at": datetime.now().isoformat(),
            "error_msg":   "",
        })
        save_queue(queue_file, entries)

        log.info("=" * 60)
        log.info(f"CONCLUIDO  {yt_url}")
        log.info("=" * 60)

    except Exception as e:
        log.error(f"ERRO: {e}", exc_info=True)
        # Recarrega entradas para evitar sobrescrever mudancas concorrentes
        entries = json.loads(queue_file.read_text(encoding="utf-8"))
        entries[idx]["status"]    = "error"
        entries[idx]["error_msg"] = str(e)
        save_queue(queue_file, entries)
        sys.exit(1)


if __name__ == "__main__":
    main()
