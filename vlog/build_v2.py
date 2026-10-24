"""Vlog v2: cut to the beat of "Washed" with a faded film grade.

Usage: python3 -I vlog/build_v2.py <proxy_dir> <music_dir> <work_dir>
<music_dir> holds washed.mp3, pad.mp3 and washed_beats.json.
Writes <work_dir>/vlog_v2.mp4 and <work_dir>/timeline_v2.json.
"""
import glob
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edl_v2 import COLD_OPEN, END_SHOT, SONG  # noqa: E402

PROXY, MUSIC, WORK = sys.argv[1:4]
FPS = 24
FADE = 0.12
CAMP_TALK, CAMP_MONTAGE = 1.0, 0.12
SONG_UP, SONG_DUCK = 0.9, 0.2
SONG_END = 218.0  # the cover rings out after the last beat (~210.8 s); trim the quiet tail
# Faded film look: lifted blacks, softer highlights, warm, slightly muted, fine grain.
GRADE = (
    "eq=contrast=0.9:saturation=0.82,"
    "curves=master='0/0.09 0.5/0.52 1/0.94',"
    "colorbalance=rs=0.05:gs=0.01:bs=-0.05:rm=0.03:bm=-0.04:rh=0.02:bh=-0.03,"
    "noise=alls=5:allf=t"
)


def clip_path(num):
    return glob.glob(os.path.join(PROXY, f"DJI_*_{num}_D.mp4"))[0]


def run(*args):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *args], check=True)


def plan():
    """Lay every shot on the timeline; song shots start and end on beats."""
    beats = json.load(open(os.path.join(MUSIC, "washed_beats.json")))
    shots, t = [], 0.0
    for s in COLD_OPEN:
        shots.append({"clip": s[0], "in": s[1], "at": t, "dur": s[2], "kind": "t" if len(s) > 3 else "m"})
        t += s[2]
    song_start = t
    pos, i = 0.0, 0  # song time, beat index
    for s in SONG:
        if len(s) > 3:  # talk: natural length, snap the end to the next beat
            target = pos + s[2]
            j = next(k for k, b in enumerate(beats) if b >= target - 0.05)
        else:
            j = i + s[2]
        end = beats[j]
        shots.append({"clip": s[0], "in": s[1], "at": song_start + pos, "dur": end - pos,
                      "kind": "t" if len(s) > 3 else "m"})
        pos, i = end, j
    shots.append({"clip": END_SHOT[0], "in": END_SHOT[1], "at": song_start + pos,
                  "dur": SONG_END - pos, "kind": "m", "end": True})
    for s in shots:
        s["at"], s["dur"] = round(s["at"], 3), round(s["dur"], 3)
    return shots, song_start, song_start + SONG_END


def cut_shot(k, s):
    out = os.path.join(WORK, "shots_v2", f"{k:03d}.mp4")
    gain = CAMP_TALK if s["kind"] == "t" else CAMP_MONTAGE
    d = s["dur"]
    run(
        "-ss", str(s["in"]), "-t", str(d), "-i", clip_path(s["clip"]),
        "-vf", f"scale=1920:1080,fps={FPS},setsar=1,{GRADE}",
        "-af", f"loudnorm=I=-16:TP=-1.5:LRA=11,volume={gain},afade=t=in:d={FADE},"
               f"afade=t=out:st={max(d - FADE, 0)}:d={FADE},aresample=48000,apad,atrim=0:{d}",
        "-frames:v", str(round(d * FPS)),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", out,
    )
    return out


def main():
    os.makedirs(os.path.join(WORK, "shots_v2"), exist_ok=True)
    shots, song_start, total = plan()
    for s in shots:
        clip_len = float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", clip_path(s["clip"])],
            capture_output=True, text=True).stdout)
        if s["in"] + s["dur"] > clip_len:
            sys.exit(f"shot {s['clip']} @ {s['in']} runs past the clip ({clip_len:.1f} s)")

    paths = [cut_shot(k, s) for k, s in enumerate(shots)]
    with open(os.path.join(WORK, "list_v2.txt"), "w") as f:
        f.writelines(f"file '{p}'\n" for p in paths)
    joined = os.path.join(WORK, "joined_v2.mp4")
    run("-f", "concat", "-safe", "0", "-i", os.path.join(WORK, "list_v2.txt"), "-c", "copy", joined)

    # Music: pad under the cold open fading out as the song comes in; song ducked under talk.
    talk = [(s["at"], s["at"] + s["dur"]) for s in shots if s["kind"] == "t" and s["at"] >= song_start]
    ramp = 0.35
    duck = "+".join(f"clip(min((t-{a - ramp})/{ramp},({b + ramp}-t)/{ramp}),0,1)" for a, b in talk)
    song_vol = f"{SONG_UP}-({SONG_UP}-{SONG_DUCK})*min(1,{duck})"
    ms = int(song_start * 1000)
    run(
        "-i", joined,
        "-i", os.path.join(MUSIC, "pad.mp3"),
        "-i", os.path.join(MUSIC, "washed.mp3"),
        "-filter_complex",
        f"[1:a]atrim=0:{song_start + 6},loudnorm=I=-20:TP=-2,"
        f"afade=t=in:d=1.5,afade=t=out:st={song_start}:d=5,aresample=48000[pad];"
        f"[2:a]atrim=0:{total - song_start},loudnorm=I=-15:TP=-1.5:LRA=11,aresample=48000,"
        f"afade=t=out:st={total - song_start - 5}:d=5,adelay={ms}|{ms},"
        f"volume='{song_vol}':eval=frame[song];"
        f"[0:a][pad][song]amix=inputs=3:duration=first:normalize=0,alimiter=limit=0.95[a]",
        "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        os.path.join(WORK, "vlog_v2.mp4"),
    )
    json.dump({"duration": round(total, 3), "song_start": song_start, "shots": shots},
              open(os.path.join(WORK, "timeline_v2.json"), "w"), indent=1)
    print(f"{len(shots)} shots, {total:.1f} s (song from {song_start:.1f} s)")


if __name__ == "__main__":
    main()
