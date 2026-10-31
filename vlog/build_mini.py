"""Mini film (~60 s), after the CapCut "mini film" template: long calm holds with hard cuts,
one short insert, gentle slow motion, teal-orange grade, music only, fade to black.

Usage: python3 -I vlog/build_mini.py <proxy_dir> <music_dir> <work_dir>
Writes <work_dir>/mini_base.mp4 and <work_dir>/mini_timeline.json.
"""
import glob
import json
import os
import subprocess
import sys

PROXY, MUSIC, WORK = sys.argv[1:4]
OUT = os.path.join(WORK, "mini")
FPS = 24
SLOW = 0.75          # playback speed of every shot
SONG_FROM_BEAT = 80  # "Washed" from its build (~38 s in)
END_FADE = 1.5       # last shot fades to black
CARD = 4.5           # logo on black while the song fades
GRADE = (
    "eq=contrast=1.06:saturation=0.86,"
    "colorbalance=rs=-0.06:gs=0.0:bs=0.07:rm=0.02:bm=-0.03:rh=0.08:gh=0.02:bh=-0.08,"
    "curves=master='0/0.04 0.5/0.5 1/0.95',vignette=PI/5,noise=alls=4:allf=t"
)

# (clip, in_s, beats). Wide, atmospheric frames; one 3-beat insert like the template's bridge.
SHOTS = [
    ("0184", 4.0, 8),     # window onto the pines (title)
    ("0206", 8.0, 8),     # walking in through the garden
    ("0212", 2.25, 8),    # the overlook
    ("0241", 25.0, 8),    # courts under the pines and blue sky
    ("0190", 14.75, 3),   # insert: the light cross at night
    ("0229", 6.0, 8),     # bonfire, silhouettes
    ("0227", 268.0, 8),   # the fire
    ("0245", 5.0, 8),     # courts under the clouds
    ("0248", 142.0, 8),   # the umbrella wave
    ("0264", 4.0, 8),     # walking under the pines
    ("0254", 24.0, 8),    # group photo
    ("0273", 3.0, 8),     # stone steps
    ("0266", 4.0, 8),     # the bus
    ("0270", 3.0, 8),     # waving from the bus
    ("0183", 25.0, 8),    # the banner, last shot
]


def clip_path(num):
    return glob.glob(os.path.join(PROXY, f"DJI_*_{num}_D.mp4"))[0]


def run(*args):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *args], check=True)


def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                 "csv=p=0", path], capture_output=True, text=True).stdout)


def main():
    os.makedirs(OUT, exist_ok=True)
    clips = [s[0] for s in SHOTS]
    if len(set(clips)) != len(clips):
        sys.exit("a clip is used twice")
    beats = json.load(open(os.path.join(MUSIC, "washed_beats.json")))

    i, pos0, paths, laid = SONG_FROM_BEAT, beats[SONG_FROM_BEAT], [], []
    for k, (c, start, n) in enumerate(SHOTS):
        dur = beats[i + n] - beats[i]
        src = dur * SLOW
        if start + src + 0.2 > duration(clip_path(c)):
            sys.exit(f"shot {c} @ {start} runs past the clip")
        out = os.path.join(OUT, f"{k:02d}.mp4")
        fade = f",fade=t=out:st={dur - END_FADE}:d={END_FADE}" if k == len(SHOTS) - 1 else ""
        if not os.path.exists(out):
            run("-ss", str(start), "-t", str(src + 0.2), "-i", clip_path(c), "-an", "-vf",
                f"scale=1920:1080,setpts=PTS/{SLOW},minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:"
                f"me_mode=bidir,{GRADE}{fade},trim=duration={dur},setpts=PTS-STARTPTS",
                "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", out)
        paths.append(out)
        laid.append({"clip": c, "in": start, "at": round(beats[i] - pos0, 3), "dur": round(dur, 3)})
        i += n
        print(k, c, round(dur, 2), flush=True)

    black = os.path.join(OUT, "card.mp4")
    run("-f", "lavfi", "-i", f"color=black:s=1920x1080:r={FPS}:d={CARD}", "-c:v", "libx264",
        "-pix_fmt", "yuv420p", black)
    lst = os.path.join(OUT, "list.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in paths + [black])
    video = os.path.join(OUT, "video.mp4")
    run("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video)

    total = duration(video)
    final = os.path.join(WORK, "mini_base.mp4")
    run("-i", video, "-ss", str(pos0), "-t", str(total), "-i", os.path.join(MUSIC, "washed.mp3"),
        "-map", "0:v", "-map", "1:a", "-af",
        f"loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=in:d=2.5,afade=t=out:st={total - CARD - 1}:d={CARD + 1}",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", final)
    json.dump({"duration": round(duration(final), 3), "title": {"at": 0.4, "dur": round(laid[0]["dur"] - 0.6, 3)},
               "card_at": round(total - CARD, 3), "shots": laid},
              open(os.path.join(WORK, "mini_timeline.json"), "w"), indent=1)
    print(f"mini film {duration(final):.1f} s")


if __name__ == "__main__":
    main()
