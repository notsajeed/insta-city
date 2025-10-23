# src/video_builder.py
import os
from pathlib import Path
from moviepy.editor import ImageClip, concatenate_videoclips, CompositeVideoClip, AudioFileClip
from moviepy.video.fx.all import resize, fadein, fadeout
from utils import text_to_image

def build_video(
    image_paths,
    title_text,
    facts_chunks=None, 
    output_path="assets/tmp/final.mp4",
    fps=30,
    duration_per_image=3,
    bg_music_path=None
):
    """
    Builds a vertical short video (Reels/TikTok style) from images and text.
    Uses Pillow to render title and facts captions (avoiding ImageMagick).
    facts_chunks: list of strings to overlay sequentially
    """
    if not image_paths:
        raise ValueError("No images provided for the video.")

    w, h = 1080, 1920 
    clips = []

    # --- Create image clips with zoom/fade effects ---
    for path in image_paths:
        try:
            clip = (
                ImageClip(path)
                .set_duration(duration_per_image)
                .resize(width=w)
                .fx(resize, lambda t: 1 + 0.02 * t)
                .fx(fadein, 0.5)
                .fx(fadeout, 0.5)
            )
            clip = clip.set_position("center")
            clips.append(clip)
        except Exception as e:
            print(f"[WARN] Skipping image '{path}': {e}")

    if not clips:
        raise RuntimeError("No valid clips built — check image paths or formats.")

    seq = concatenate_videoclips(clips, method="compose")

    # --- Title overlay ---
    title_img_path = text_to_image(title_text.upper(), width=w-100, height=200, fontsize=80)
    title_clip = ImageClip(title_img_path).set_duration(min(3, seq.duration/2)).set_position(("center", 150))

    # --- Facts overlay: sequential chunks ---
    fact_clips = []
    if facts_chunks:
        total_chunks = len(facts_chunks)
        chunk_duration = seq.duration / total_chunks
        for i, chunk in enumerate(facts_chunks):
            fact_img_path = text_to_image(chunk, width=w-200, height=400, fontsize=50)
            clip = ImageClip(fact_img_path).set_duration(chunk_duration).set_position(("center", h-400)).set_start(i*chunk_duration)
            fact_clips.append(clip)

    # --- Combine layers ---
    final = CompositeVideoClip([seq, title_clip, *fact_clips], size=(w, h))

    # --- Background music ---
    if bg_music_path and os.path.exists(bg_music_path):
        try:
            audio = AudioFileClip(bg_music_path).volumex(0.4)
            final = final.set_audio(audio.set_duration(final.duration))
        except Exception as e:
            print(f"[WARN] Could not add background music: {e}")

    # --- Ensure output directory exists ---
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Rendering video to: {output_path}")
    final.write_videofile(
        output_path,
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium",
        bitrate="3000k",
        logger=None
    )

    print("[✅] Video build complete.")
    return output_path

