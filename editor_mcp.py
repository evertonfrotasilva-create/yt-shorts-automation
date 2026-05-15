"""MCP server — orquestra o pipeline completo de produção de Shorts.
Expõe ferramentas que o Cowork pode chamar diretamente.
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(Path(__file__).parent / ".env")

mcp = FastMCP("video-editor")

BASE_DIR   = Path(__file__).parent
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", BASE_DIR / "outputs"))


@mcp.tool()
def run_pipeline(
    topic_slug: str,
    narration_text: str,
    shotlist: str,
) -> str:
    """
    Etapa 1 do pipeline: gera narração (ElevenLabs) e baixa clipes do Pexels.

    Args:
        topic_slug: Nome curto sem espaços para a pasta (ex: "brain_money_habits").
        narration_text: Texto completo da narração em inglês.
        shotlist: JSON com lista de takes. Formato:
                  [{"slug": "01_hook", "query": "brain glowing dark cinematic", "duration": 3, "subtitle": "Your brain\\nis lying to you."}]

    Returns:
        JSON com status, caminho da pasta de saída e lista de arquivos gerados.
    """
    work_dir = OUTPUT_DIR / topic_slug
    work_dir.mkdir(parents=True, exist_ok=True)

    shots = json.loads(shotlist)
    results = {"topic": topic_slug, "work_dir": str(work_dir), "steps": []}

    # ── Narração ──────────────────────────────────────────────────────────────
    narration_path = work_dir / "narration.mp3"
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY", "")

    if elevenlabs_key.startswith("sk_") and not narration_path.exists():
        try:
            from elevenlabs.client import ElevenLabs
            voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
            client = ElevenLabs(api_key=elevenlabs_key)
            audio = client.text_to_speech.convert(
                voice_id=voice_id,
                text=narration_text,
                model_id="eleven_turbo_v2",
                output_format="mp3_44100_128",
            )
            with open(narration_path, "wb") as f:
                for chunk in audio:
                    f.write(chunk)
            results["steps"].append({"step": "narration", "engine": "elevenlabs", "file": str(narration_path)})
        except Exception as e:
            results["steps"].append({"step": "narration", "error": str(e)})
    elif narration_path.exists():
        results["steps"].append({"step": "narration", "status": "cached", "file": str(narration_path)})

    # ── Clipes Pexels ─────────────────────────────────────────────────────────
    import requests, time
    pexels_key = os.getenv("PEXELS_API_KEY", "")
    clip_results = []

    for shot in shots:
        slug     = shot["slug"]
        query    = shot["query"]
        out_path = work_dir / f"{slug}.mp4"

        if out_path.exists():
            clip_results.append({"slug": slug, "status": "cached", "file": str(out_path)})
            continue

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
                clip_results.append({"slug": slug, "error": "no results"})
                continue
            files  = videos[0].get("video_files", [])
            vert   = [f for f in files if f.get("width", 0) < f.get("height", 1)]
            best   = max(vert or files, key=lambda f: f.get("height", 0))
            with requests.get(best["link"], stream=True, timeout=60) as resp:
                resp.raise_for_status()
                out_path.write_bytes(resp.content)
            clip_results.append({"slug": slug, "file": str(out_path), "res": f"{best.get('width')}x{best.get('height')}"})
        except Exception as e:
            clip_results.append({"slug": slug, "error": str(e)})
        time.sleep(0.3)

    results["steps"].append({"step": "clips", "results": clip_results})

    # Salva shotlist para uso pelo editor
    shotlist_path = work_dir / "shotlist.json"
    shotlist_path.write_text(json.dumps(shots, indent=2, ensure_ascii=False))
    results["shotlist_file"] = str(shotlist_path)

    ok_clips = sum(1 for c in clip_results if "file" in c)
    results["summary"] = f"Narração OK | {ok_clips}/{len(shots)} clipes baixados"
    return json.dumps(results, indent=2, ensure_ascii=False)


@mcp.tool()
def edit_video(
    topic_slug: str,
    background_music: bool = True,
    music_volume: float = 0.12,
) -> str:
    """
    Etapa 2 do pipeline: monta e exporta o vídeo final (1080x1920, 30fps).
    Lê narration.mp3 + clips + shotlist.json da pasta do topic_slug.

    Args:
        topic_slug: Mesmo slug usado no run_pipeline (ex: "brain_money_habits").
        background_music: Adiciona música de fundo de assets/background.mp3 se True.
        music_volume: Volume da música (0.0–1.0). Padrão 0.12 (sutil).

    Returns:
        JSON com caminho do vídeo final e tamanho em MB.
    """
    work_dir = OUTPUT_DIR / topic_slug
    if not work_dir.exists():
        return json.dumps({"error": f"Pasta não encontrada: {work_dir}"})

    shotlist_path = work_dir / "shotlist.json"
    narration_path = work_dir / "narration.mp3"
    output_path = work_dir / "final_video.mp4"

    if not narration_path.exists():
        return json.dumps({"error": "narration.mp3 não encontrado. Rode run_pipeline primeiro."})
    if not shotlist_path.exists():
        return json.dumps({"error": "shotlist.json não encontrado. Rode run_pipeline primeiro."})

    shots = json.loads(shotlist_path.read_text(encoding="utf-8"))

    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    from moviepy import (
        VideoFileClip, AudioFileClip, CompositeVideoClip,
        concatenate_videoclips, ImageClip
    )
    from moviepy.audio.fx import MultiplyVolume

    W, H = 1080, 1920

    def make_subtitle(text, duration):
        pad, fsize = 40, 68
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", fsize)
        except Exception:
            font = ImageFont.load_default(size=fsize)
        dummy = Image.new("RGBA", (1, 1))
        draw  = ImageDraw.Draw(dummy)
        bbox  = draw.multiline_textbbox((0, 0), text, font=font, align="center")
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        img_w = int(min(tw + pad * 2, W - 60))
        img_h = int(th + pad * 2)
        img   = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
        draw  = ImageDraw.Draw(img)
        draw.rounded_rectangle([0, 0, img_w - 1, img_h - 1], radius=18, fill=(0, 0, 0, 180))
        cx, cy = img_w // 2, img_h // 2
        draw.multiline_text((cx + 3, cy + 3), text, font=font, fill=(0, 0, 0, 200), anchor="mm", align="center")
        draw.multiline_text((cx, cy), text, font=font, fill=(255, 255, 255, 255), anchor="mm", align="center")
        arr = np.array(img)
        return ImageClip(arr, duration=duration).with_position(("center", H - img_h - 120))

    def fit_clip(clip, duration):
        dur  = min(duration, clip.duration)
        clip = clip.subclipped(0, dur)
        cw, ch = clip.size
        if cw / ch > W / H:
            clip = clip.resized(height=H)
            excess = (clip.w - W) / 2
            clip = clip.cropped(x1=excess, x2=clip.w - excess)
        else:
            clip = clip.resized(width=W)
            excess = (clip.h - H) / 2
            clip = clip.cropped(y1=excess, y2=clip.h - excess)
        if clip.duration < duration:
            last = clip.to_ImageClip(clip.duration - 0.05).with_duration(duration - clip.duration)
            clip = concatenate_videoclips([clip, last])
        return clip.without_audio()

    narration = AudioFileClip(str(narration_path))
    audio_dur  = narration.duration
    total_declared = sum(s.get("duration", 4) for s in shots)
    scale = audio_dur / total_declared

    final_clips = []
    for shot in shots:
        slug     = shot["slug"]
        dur      = round(shot.get("duration", 4) * scale, 2)
        subtitle = shot.get("subtitle", "")
        path     = work_dir / f"{slug}.mp4"

        if not path.exists():
            black = np.zeros((H, W, 3), dtype=np.uint8)
            vc = ImageClip(black, duration=dur)
        else:
            vc = fit_clip(VideoFileClip(str(path)), dur)

        sub  = make_subtitle(subtitle, dur)
        comp = CompositeVideoClip([vc, sub], size=(W, H))
        final_clips.append(comp)

    video = concatenate_videoclips(final_clips, method="compose")

    # Música de fundo
    bg_path = BASE_DIR / "assets" / "background.mp3"
    if background_music and bg_path.exists():
        music_raw = AudioFileClip(str(bg_path))
        if music_raw.duration < audio_dur:
            from moviepy import concatenate_audioclips
            loops = int(audio_dur / music_raw.duration) + 1
            music_raw = concatenate_audioclips([music_raw] * loops)
        music = music_raw.subclipped(0, audio_dur).with_effects([MultiplyVolume(music_volume)])
        from moviepy import CompositeAudioClip
        video = video.with_audio(CompositeAudioClip([narration, music]))
    else:
        video = video.with_audio(narration)

    video.write_videofile(
        str(output_path),
        fps=30,
        codec="libx264",
        audio_codec="aac",
        preset="fast",
        ffmpeg_params=["-crf", "23"],
        logger=None,
    )

    size_mb = output_path.stat().st_size / (1024 * 1024)
    return json.dumps({
        "success": True,
        "file": str(output_path),
        "size_mb": round(size_mb, 1),
        "duration_s": round(audio_dur, 1),
        "resolution": "1080x1920",
    })


@mcp.tool()
def list_videos() -> str:
    """Lista todos os vídeos já produzidos na pasta outputs."""
    videos = []
    for folder in sorted(OUTPUT_DIR.iterdir()):
        if not folder.is_dir():
            continue
        final = folder / "final_video.mp4"
        narr  = folder / "narration.mp3"
        clips = list(folder.glob("*.mp4"))
        videos.append({
            "topic": folder.name,
            "final_video": final.exists(),
            "narration": narr.exists(),
            "clips": len([c for c in clips if c.name != "final_video.mp4"]),
            "size_mb": round(final.stat().st_size / 1024 / 1024, 1) if final.exists() else None,
        })
    return json.dumps(videos, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport="stdio")
