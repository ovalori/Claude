"""Vlog v3: three-part camp film modelled on the SEP North Luzon reference.

cold open (pad) -> part 1 on "Washed" -> black -> part 2: bonfire talk as voiceover over
b-roll with the pad -> black -> part 3 as "Washed" resumes -> title card on black.

Usage: python3 -I vlog/build_v3.py <proxy_dir> <music_dir> <work_dir>
<music_dir> holds washed.mp3, pad.mp3 and washed_beats.json.
Writes <work_dir>/vlog_v3.mp4 and <work_dir>/timeline_v3.json.
"""
import glob
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edl_v3 import COLD_OPEN, PART1, PART3, VOICE, VOICE_BROLL  # noqa: E402

PROXY, MUSIC, WORK = sys.argv[1:4]
OUT = os.path.join(WORK, "v3")
FPS = 24
FADE = 0.12
CAMP_TALK, CAMP_MONTAGE = 1.0, 0.12
SONG_UP, SONG_DUCK = 0.9, 0.2
SONG_END = 218.0      # trim the cover's quiet ring-out
BLACK = 1.4           # hold on black between parts
DIP = 0.7             # fade to / from black at part edges
CARD = 8.0            # closing title on black (the song rings out under it)
GRADE = (
    "eq=contrast=0.9:saturation=0.82,"
    "curves=master='0/0.09 0.5/0.52 1/0.94',"
    "colorbalance=rs=0.05:gs=0.01:bs=-0.05:rm=0.03:bm=-0.04:rh=0.02:bh=-0.03,"
    "noise=alls=5:allf=t"
)
ENC = ["-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]


def clip_path(num):
    return glob.glob(os.path.join(PROXY, f"DJI_*_{num}_D.mp4"))[0]


def run(*args):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *args], check=True)


def duration(path):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True).stdout)


def cut(name, clip, start, dur, gain):
    if start + dur > duration(clip_path(clip)) + 0.01:
        sys.exit(f"shot {clip} @ {start} + {dur} runs past the clip")
    out = os.path.join(OUT, f"{name}.mp4")
    run(
        "-ss", str(start), "-t", str(dur), "-i", clip_path(clip),
        "-vf", f"scale=1920:1080,fps={FPS},setsar=1,{GRADE}",
        "-af", f"loudnorm=I=-16:TP=-1.5:LRA=11,volume={gain},afade=t=in:d={FADE},"
               f"afade=t=out:st={max(dur - FADE, 0)}:d={FADE},aresample=48000,apad,atrim=0:{dur}",
        "-frames:v", str(round(dur * FPS)), *ENC, out,
    )
    return out


def join(name, paths):
    lst = os.path.join(OUT, f"{name}.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in paths)
    out = os.path.join(OUT, f"{name}.mp4")
    run("-f", "concat", "-safe", "0", "-i", lst, "-map", "0:v:0", "-map", "0:a:0", "-c", "copy", out)
    return out


def black(name, dur):
    out = os.path.join(OUT, f"{name}.mp4")
    run("-f", "lavfi", "-i", f"color=black:s=1920x1080:r={FPS}:d={dur}",
        "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo", "-t", str(dur), *ENC, out)
    return out


def duck_expr(talk, up, down, ramp=0.35):
    if not talk:
        return str(up)
    terms = "+".join(f"clip(min((t-{a - ramp})/{ramp},({b + ramp}-t)/{ramp}),0,1)" for a, b in talk)
    return f"{up}-({up}-{down})*min(1,{terms})"


def song_part(name, shots, beats, song_from_beat, tail=0.0):
    """Lay shots on the beat grid from beat index song_from_beat; return clip, song span, shot list."""
    i = song_from_beat
    pos0 = beats[i] if i > 0 else 0.0
    pos, laid, paths = pos0, [], []
    for k, s in enumerate(shots):
        if len(s) > 3:
            j = next(n for n, b in enumerate(beats) if b >= pos + s[2] - 0.05)
        else:
            j = i + s[2]
        if j >= len(beats):
            sys.exit(f"{name}: ran out of beats at shot {k} ({s})")
        dur = beats[j] - pos
        kind = "t" if len(s) > 3 else "m"
        paths.append(cut(f"{name}_{k:03d}", s[0], s[1], dur, CAMP_TALK if kind == "t" else CAMP_MONTAGE))
        laid.append({"clip": s[0], "in": s[1], "at": round(pos - pos0, 3), "dur": round(dur, 3), "kind": kind})
        pos, i = beats[j], j
    video = join(f"{name}_video", paths)
    span = (pos0, pos + tail)
    return video, span, laid, i


def mix_song(name, video, span, laid, fade_in, fade_out):
    """Put the song segment under a part, ducked under its talking shots."""
    a, b = span
    length = b - a
    talk = [(s["at"], s["at"] + s["dur"]) for s in laid if s["kind"] == "t"]
    out = os.path.join(OUT, f"{name}.mp4")
    run(
        "-i", video, "-ss", str(a), "-t", str(length), "-i", os.path.join(MUSIC, "washed.mp3"),
        "-filter_complex",
        f"[1:a]loudnorm=I=-15:TP=-1.5:LRA=11,aresample=48000,"
        f"afade=t=in:d={fade_in},afade=t=out:st={length - fade_out}:d={fade_out},"
        f"volume='{duck_expr(talk, SONG_UP, SONG_DUCK)}':eval=frame[s];"
        f"[0:a][s]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95[a]",
        "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", out,
    )
    return out


def dip(path, fade_in, fade_out):
    """Fade a part's picture from / to black at its edges."""
    d = duration(path)
    vf = []
    if fade_in:
        vf.append(f"fade=t=in:d={DIP}")
    if fade_out:
        vf.append(f"fade=t=out:st={d - DIP}:d={DIP}")
    out = path.replace(".mp4", "_dip.mp4")
    run("-i", path, "-vf", ",".join(vf), "-c:a", "copy", "-c:v", "libx264", "-preset", "fast",
        "-crf", "18", "-pix_fmt", "yuv420p", out)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    beats = json.load(open(os.path.join(MUSIC, "washed_beats.json")))
    parts, timeline, t = [], [], 0.0

    # Cold open on the pad.
    paths = [cut(f"open_{k}", s[0], s[1], s[2], CAMP_TALK if len(s) > 3 else CAMP_MONTAGE)
             for k, s in enumerate(COLD_OPEN)]
    open_v = join("open_video", paths)
    open_len = duration(open_v)
    open_mix = os.path.join(OUT, "open.mp4")
    run("-i", open_v, "-i", os.path.join(MUSIC, "pad.mp3"), "-filter_complex",
        f"[1:a]atrim=0:{open_len},loudnorm=I=-20:TP=-2,afade=t=in:d=1.5,"
        f"afade=t=out:st={open_len - 1.5}:d=1.5,aresample=48000[p];"
        f"[0:a][p]amix=inputs=2:duration=first:normalize=0[a]",
        "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", open_mix)
    parts.append(open_mix)
    timeline.append({"part": "open", "at": 0.0, "dur": round(open_len, 3)})
    t += open_len

    # Part 1 on "Washed" from its start; fades to black at the end.
    v1, span1, laid1, last_beat = song_part("p1", PART1, beats, 0)
    p1 = dip(mix_song("p1", v1, span1, laid1, fade_in=0.05, fade_out=1.2), False, True)
    parts.append(p1)
    timeline.append({"part": "part1", "at": round(t, 3), "dur": round(duration(p1), 3), "shots": laid1})
    t += duration(p1)
    parts.append(black("black1", BLACK))
    t += BLACK

    # Part 2: the bonfire talk as one continuous voice over muted b-roll, pad underneath.
    vc, vin, vlen = VOICE
    if abs(sum(s[2] for s in VOICE_BROLL) - vlen) > 0.05:
        sys.exit("VOICE_BROLL must add up to the voice length")
    paths = [cut(f"p2_{k}", s[0], s[1], s[2], 0.0) for k, s in enumerate(VOICE_BROLL)]
    v2 = join("p2_video", paths)
    p2_mix = os.path.join(OUT, "p2.mp4")
    run("-i", v2, "-ss", str(vin), "-t", str(vlen), "-i", clip_path(vc),
        "-ss", "60", "-i", os.path.join(MUSIC, "pad.mp3"), "-filter_complex",
        f"[1:a]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,afade=t=in:d=0.3,"
        f"afade=t=out:st={vlen - 0.6}:d=0.6[v];"
        f"[2:a]atrim=0:{vlen},loudnorm=I=-24:TP=-3,aresample=48000,afade=t=in:d=2,"
        f"afade=t=out:st={vlen - 2}:d=2[p];"
        f"[v][p]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]",
        "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", p2_mix)
    p2 = dip(p2_mix, True, True)
    parts.append(p2)
    timeline.append({"part": "part2", "at": round(t, 3), "dur": round(duration(p2), 3),
                     "shots": [{"clip": s[0], "in": s[1], "dur": s[2]} for s in VOICE_BROLL]})
    t += duration(p2)
    parts.append(black("black2", BLACK))
    t += BLACK

    # Part 3: the song resumes where part 1 left it; the ring-out plays under the title card.
    v3, span3, laid3, _ = song_part("p3", PART3, beats, last_beat)
    shots_len = duration(v3)
    tail = min(CARD, SONG_END - span3[1])
    card = black("card", tail)
    v3_card = join("p3_card_video", [v3, card])
    p3 = dip(mix_song("p3", v3_card, (span3[0], span3[1] + tail), laid3, fade_in=1.0, fade_out=3.0),
             True, False)
    parts.append(p3)
    timeline.append({"part": "part3", "at": round(t, 3), "dur": round(duration(p3), 3), "shots": laid3})
    card_at = t + shots_len
    t += duration(p3)

    final = os.path.join(WORK, "vlog_v3.mp4")
    lst = os.path.join(OUT, "parts.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    run("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", final)

    total = duration(final)
    json.dump({"duration": round(total, 3), "song_start": round(open_len, 3),
               "card_at": round(card_at, 3), "card_dur": round(total - card_at, 3), "parts": timeline},
              open(os.path.join(WORK, "timeline_v3.json"), "w"), indent=1)
    print(f"{total:.1f} s; part1 {span1[1] - span1[0]:.1f} s of song, part3 {span3[1] - span3[0]:.1f} s")


if __name__ == "__main__":
    main()
