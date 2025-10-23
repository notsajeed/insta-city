# src/video_builder.py
import os
from pathlib import Path
from moviepy.editor import (
    ImageClip,
    concatenate_videoclips,
    TextClip,
    CompositeVideoClip,
    AudioFileClip,
)
from moviepy.video.fx.all import resize, fadein, fadeout

def build_video(
    image_paths,
    title_text,
    facts_text,
    output_path="assets/tmp/final.mp4",
    fps=30,
    duration_per_image=3,
    bg_music_path=None
):
    """
    Builds a vertical short video (Reels/TikTok style) from images and text.
    Applies zoom-in and fade effects. Optionally adds background music.
    """
    if not image_paths:
        raise ValueError("No images provided for the video.")

    w, h = 1080, 1920  # portrait
    clips = []

    # --- Create image clips ---
    for path in image_paths:
        try:
            clip = (
                ImageClip(path)
                .set_duration(duration_per_image)
                .resize(width=w)
                .fx(resize, lambda t: 1 + 0.02 * t)  # gentle zoom
                .fx(fadein, 0.5)
                .fx(fadeout, 0.5)
            )
            clip = clip.set_position("center")
            clips.append(clip)
        except Exception as e:
            print(f"[WARN] Skipping image '{path}': {e}")

    if not clips:
        raise RuntimeError("No valid clips built — check image paths or formats.")

    # --- Concatenate image clips ---
    seq = concatenate_videoclips(clips, method="compose")

    # --- Title overlay (top) ---
    try:
        title = (
            TextClip(
                txt=title_text.upper(),
                fontsize=80,
                color="white",
                font="Arial-Bold",
                stroke_color="black",
                stroke_width=2,
                method="caption",
                size=(w - 100, None)
            )
            .set_position(("center", 150))
            .set_duration(min(3, seq.duration / 2))
            .fadeout(0.5)
        )
    except Exception as e:
        print(f"[WARN] Could not render title: {e}")
        title = None

    # --- Facts overlay (bottom) ---
    try:
        facts = (
           TextClip(
            txt="Tokyo, Japan",
            fontsize=80,
            color="white",
            font="Arial",  # must exist on Windows
            method="caption",  # avoids ImageMagick
            size=(w-100, None)
        )

            .set_position(("center", h - 300))
            .set_duration(seq.duration)
        )
    except Exception as e:
        print(f"[WARN] Could not render facts: {e}")
        facts = None

    # --- Combine layers ---
    layers = [seq]
    if title:
        layers.append(title.set_start(0))
    if facts:
        layers.append(facts)

    final = CompositeVideoClip(layers, size=(w, h))

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
        logger=None  # cleaner output
    )

    print("[✅] Video build complete.")
    return output_path

# --- Example usage ---
if __name__ == "__main__":
    # Example images
    images = [
        "data/cities/Tokyo/images/photo1.jpeg",
        "data/cities/Tokyo/images/photo2.jpeg",
        "data/cities/Tokyo/images/photo3.jpeg"
    ]
    build_video(
        images,
        title_text="Tokyo, Japan",
        facts_text="Population: 37.7M\nKnown for: Skytree, Shibuya Crossing",
        output_path="assets/tmp/tokyo_reel.mp4"
    )
