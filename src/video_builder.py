from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, TextClip, CompositeVideoClip
from pathlib import Path

def build_video(image_paths, title_text, facts_text, output_path='assets/tmp/final.mp4', fps=24, duration_per_image=3):
    clips = []
    w, h = 1080, 1920  # portrait reel
    for p in image_paths:
        clip = (ImageClip(p)
                .set_duration(duration_per_image)
                .resize(width=w)
                .fx(lambda c: c))
        # simple zoom-in effect
        clip = clip.fx(vfx.resize, lambda t: 1 + 0.02 * t) if hasattr(clip, 'fx') else clip
        clips.append(clip)

    seq = concatenate_videoclips(clips, method='compose')

    # overlay title for first 2 seconds
    title = (TextClip(title_text, fontsize=70, font='Arial-Bold')
             .set_position(('center', 150))
             .set_duration(2))

    facts = (TextClip(facts_text, fontsize=40, font='Arial', align='West')
             .set_position(('center', 1700))
             .set_duration(seq.duration))

    final = CompositeVideoClip([seq, title.set_start(0), facts])

    # optional background music
    # audio = AudioFileClip('templates/music.mp3').volumex(0.6)
    # final = final.set_audio(audio.set_duration(final.duration))

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    final.write_videofile(output_path, fps=fps)
    return output_path