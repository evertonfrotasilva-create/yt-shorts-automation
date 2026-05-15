"""
Montagem automática do Short — sem CapCut.
Entrada : outputs/wired_to_quit/ (narration.mp3 + 16 clipes .mp4)
Saída   : outputs/wired_to_quit/final_video.mp4  (1080x1920, pronto para upload)

Música de fundo: coloque o arquivo em assets/background.mp3
(baixado do Epidemic Sound) — será mixado automaticamente a -18dB.
"""

import os
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    VideoFileClip, AudioFileClip, CompositeVideoClip,
    concatenate_videoclips, ImageClip
)
from moviepy.audio.fx import MultiplyVolume

# ── CONFIGURAÇÃO ──────────────────────────────────────────────────────────────

WORK_DIR   = Path(__file__).parent / "outputs" / "wired_to_quit"
NARRATION  = WORK_DIR / "narration.mp3"
OUTPUT     = WORK_DIR / "final_video.mp4"
BACKGROUND = Path(__file__).parent / "assets" / "background.mp3"
W, H       = 1080, 1920   # 9:16 vertical

# Volume da música de fundo (0.0 = mudo, 0.12 = sutil, 0.20 = moderado)
MUSIC_VOLUME = 0.12

# Shotlist: (arquivo, duração_s, legenda)
SHOTLIST = [
    ("01_hook_brain",        3,  "Your brain is wired\nto make you BROKE."),
    ("02_promise_money",     3,  "Here's the neuroscience\nof why you quit on money."),
    ("03_two_systems",       4,  "Your brain runs\non two systems."),
    ("04_reward_now",        3,  "One screams for\nthe reward RIGHT NOW."),
    ("05_plans_later",       3,  "The loud one\nalmost always wins."),
    ("06_saving_pain",       4,  "That's why saving\nfeels like PAIN."),
    ("07_present_bias",      4,  "Scientists call it\nPRESENT BIAS."),
    ("08_future_stranger",   4,  "Your brain treats future you\nlike a total stranger."),
    ("09_payday_negotiation",5,  "Every payday becomes\na negotiation."),
    ("10_stranger_losing",   5,  "And future you\nkeeps losing."),
    ("11_not_discipline",    4,  "The fix isn't\nmore discipline."),
    ("12_remove_decision",   4,  "It's REMOVING\nthe decision."),
    ("13_automate_transfer", 4,  "Automate the transfer\nthe second you get paid."),
    ("14_twist_wealth",      4,  "People who build wealth\naren't stronger."),
    ("15_system_brain",      3,  "They just built a system\ntheir lazy brain can't argue with."),
    ("16_cta_loop",          3,  "Still running on willpower?\nWatch again."),
]


# ── LEGENDAS ──────────────────────────────────────────────────────────────────

def make_subtitle(text: str, duration: float) -> ImageClip:
    """Cria um clip de legenda com fundo semitransparente."""
    pad   = 40
    fsize = 68
    shadow_offset = 3

    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", fsize)
    except Exception:
        font = ImageFont.load_default(size=fsize)

    # Mede o texto
    dummy = Image.new("RGBA", (1, 1))
    draw  = ImageDraw.Draw(dummy)
    bbox  = draw.multiline_textbbox((0, 0), text, font=font, align="center")
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    img_w = int(min(tw + pad * 2, W - 60))
    img_h = int(th + pad * 2)

    img  = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Fundo preto semitransparente
    draw.rounded_rectangle([0, 0, img_w - 1, img_h - 1], radius=18,
                           fill=(0, 0, 0, 180))

    cx = img_w // 2
    cy = img_h // 2

    # Sombra
    draw.multiline_text((cx + shadow_offset, cy + shadow_offset), text,
                        font=font, fill=(0, 0, 0, 200),
                        anchor="mm", align="center")
    # Texto branco
    draw.multiline_text((cx, cy), text,
                        font=font, fill=(255, 255, 255, 255),
                        anchor="mm", align="center")

    arr = np.array(img)
    clip = (ImageClip(arr, duration=duration)
            .with_position(("center", H - img_h - 120)))
    return clip


# ── CROP / RESIZE ─────────────────────────────────────────────────────────────

def fit_clip(clip: VideoFileClip, duration: float) -> VideoFileClip:
    """Redimensiona e corta para 1080x1920, limita duração."""
    # Garante duração mínima disponível
    dur = min(duration, clip.duration)
    clip = clip.subclipped(0, dur)

    cw, ch = clip.size
    target_ratio = W / H

    if cw / ch > target_ratio:
        # Muito largo — escala pela altura, corta largura
        clip = clip.resized(height=H)
        excess = (clip.w - W) / 2
        clip = clip.cropped(x1=excess, x2=clip.w - excess)
    else:
        # Muito alto — escala pela largura, corta altura
        clip = clip.resized(width=W)
        excess = (clip.h - H) / 2
        clip = clip.cropped(y1=excess, y2=clip.h - excess)

    # Padding para fechar exatamente a duração pedida
    if clip.duration < duration:
        last = clip.to_ImageClip(clip.duration - 0.05).with_duration(
            duration - clip.duration
        )
        from moviepy import concatenate_videoclips as cat
        clip = cat([clip, last])

    return clip.without_audio()


# ── PIPELINE PRINCIPAL ────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("MONTAGEM AUTOMÁTICA — Why Your Brain Is Wired To Quit")
    print("=" * 55)

    # Carrega narração e ajusta duração total
    print("\n[1/4] Carregando narração...")
    narration = AudioFileClip(str(NARRATION))
    audio_dur = narration.duration
    total_declared = sum(d for _, d, _ in SHOTLIST)
    scale = audio_dur / total_declared
    print(f"  Narração: {audio_dur:.1f}s | Vídeo declarado: {total_declared}s | Escala: {scale:.3f}")

    # Monta os takes
    print("\n[2/4] Montando takes...")
    final_clips = []
    for i, (fname, dur_declared, subtitle) in enumerate(SHOTLIST, 1):
        path = WORK_DIR / f"{fname}.mp4"
        dur  = round(dur_declared * scale, 2)

        if not path.exists():
            print(f"  [{i:02d}] AVISO: {fname}.mp4 não encontrado — usando frame preto")
            black = np.zeros((H, W, 3), dtype=np.uint8)
            vc = ImageClip(black, duration=dur)
        else:
            raw = VideoFileClip(str(path))
            vc  = fit_clip(raw, dur)

        sub  = make_subtitle(subtitle, dur)
        comp = CompositeVideoClip([vc, sub], size=(W, H))
        final_clips.append(comp)
        print(f"  [{i:02d}] {fname} — {dur:.1f}s")

    # Concatena tudo
    print("\n[3/4] Concatenando e adicionando áudio...")
    video = concatenate_videoclips(final_clips, method="compose")

    # Mixagem: narração + música de fundo (se existir)
    if BACKGROUND.exists():
        print(f"  Música de fundo: {BACKGROUND.name} (volume {int(MUSIC_VOLUME*100)}%)")
        music_raw = AudioFileClip(str(BACKGROUND))
        # Loopa a música se for mais curta que o vídeo
        if music_raw.duration < audio_dur:
            from moviepy import concatenate_audioclips
            loops = int(audio_dur / music_raw.duration) + 1
            music_raw = concatenate_audioclips([music_raw] * loops)
        music = (music_raw
                 .subclipped(0, audio_dur)
                 .with_effects([MultiplyVolume(MUSIC_VOLUME)]))
        from moviepy import CompositeAudioClip
        mixed = CompositeAudioClip([narration, music])
        video = video.with_audio(mixed)
    else:
        print("  Sem música de fundo (coloque assets/background.mp3 para ativar)")
        video = video.with_audio(narration)

    # Exporta
    print(f"\n[4/4] Exportando -> {OUTPUT.name}")
    print("  (pode levar 2–4 minutos)...")
    video.write_videofile(
        str(OUTPUT),
        fps=30,
        codec="libx264",
        audio_codec="aac",
        preset="fast",
        ffmpeg_params=["-crf", "23"],
        logger="bar",
    )

    size_mb = OUTPUT.stat().st_size / (1024 * 1024)
    print(f"\n{'=' * 55}")
    print(f"CONCLUÍDO")
    print(f"  Arquivo : {OUTPUT}")
    print(f"  Tamanho : {size_mb:.1f} MB")
    print(f"  Duração : {audio_dur:.1f}s")
    print(f"{'=' * 55}")
    print("\nPRÓXIMO PASSO: suba o final_video.mp4 no YouTube Studio")


if __name__ == "__main__":
    main()
