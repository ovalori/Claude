"""Cut the vlog from 1080p proxies: shots -> base video, live-music bed ducked under talk.

Usage: python3 -I vlog/build.py <proxy_dir> <work_dir>
Writes <work_dir>/vlog_base.mp4 (video + final mixed audio) and <work_dir>/timeline.json.
"""
import glob
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edl import MUSIC, SHOTS  # noqa: E402

PROXY, WORK = sys.argv[1], sys.argv[2]
FADE = 0.25  # audio fade at each cut, seconds
MUSIC_UP, MUSIC_DUCK = 0.85, 0.12
CAMP_MONTAGE = 0.25  # camp sound level under montage shots


def clip_path(num):
    return glob.glob(os.path.join(PROXY, f"DJI_*_{num}_D.mp4"))[0]


def run(*args):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *args], check=True)


def cut_shot(i, shot):
    num, start, dur, kind = shot[:4]
    out = os.path.join(WORK, "shots", f"{i:02d}.mp4")
    gain = 1.0 if kind == "t" else CAMP_MONTAGE
    af = (
        f"loudnorm=I=-16:TP=-1.5:LRA=11,volume={gain},"
        f"afade=t=in:d={FADE},afade=t=out:st={dur - FADE}:d={FADE},aresample=48000"
    )
    run(
        "-ss", str(start), "-t", str(dur), "-i", clip_path(num),
        "-vf", "scale=1920:1080,fps=30,setsar=1", "-af", af,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", out,
    )
    return out


def main():
    os.makedirs(os.path.join(WORK, "shots"), exist_ok=True)

    timeline, t = [], 0.0
    paths = []
    for i, shot in enumerate(SHOTS):
        paths.append(cut_shot(i, shot))
        num, start, dur, kind, caps = shot[:5]
        section = shot[5] if len(shot) > 5 else None
        timeline.append({
            "clip": num, "at": round(t, 3), "dur": dur, "kind": kind, "section": section,
            "captions": [
                {"start": round(t + max(a, start) - start, 3), "end": round(t + min(b, start + dur) - start, 3), "text": txt}
                for a, b, txt in caps
            ],
        })
        t += dur
    total = round(t, 3)

    with open(os.path.join(WORK, "list.txt"), "w") as f:
        f.writelines(f"file '{p}'\n" for p in paths)
    run("-f", "concat", "-safe", "0", "-i", os.path.join(WORK, "list.txt"), "-c", "copy",
        os.path.join(WORK, "shots_joined.mp4"))

    # Music bed: chain the live camp music with 2 s crossfades, normalise, trim to length.
    ins, chain = [], ""
    for k, (num, a, b) in enumerate(MUSIC):
        ins += ["-ss", str(a), "-t", str(b - a), "-i", clip_path(num)]
    prev = "[0:a]"
    for k in range(1, len(MUSIC)):
        chain += f"{prev}[{k}:a]acrossfade=d=2[x{k}];"
        prev = f"[x{k}]"
    chain += (
        f"{prev}loudnorm=I=-16:TP=-1.5:LRA=11,atrim=0:{total},"
        f"afade=t=in:d=1.5,afade=t=out:st={total - 4}:d=4[bed]"
    )
    bed = os.path.join(WORK, "music_bed.wav")
    run(*ins, "-filter_complex", chain, "-map", "[bed]", "-ar", "48000", "-ac", "2", bed)

    # Duck the bed under talk shots (0.4 s ramps), then mix with the camp sound.
    talk = [(s["at"], s["at"] + s["dur"]) for s in timeline if s["kind"] == "t"]
    ramp = 0.4
    duck_terms = "+".join(
        f"clip(min((t-{a - ramp})/{ramp},({b + ramp}-t)/{ramp}),0,1)" for a, b in talk
    )
    vol = f"{MUSIC_UP}-({MUSIC_UP}-{MUSIC_DUCK})*min(1,{duck_terms})"
    run(
        "-i", os.path.join(WORK, "shots_joined.mp4"), "-i", bed,
        "-filter_complex",
        f"[1:a]volume='{vol}':eval=frame[m];[0:a][m]amix=inputs=2:duration=first:normalize=0,"
        f"alimiter=limit=0.95[a]",
        "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        os.path.join(WORK, "vlog_base.mp4"),
    )

    with open(os.path.join(WORK, "timeline.json"), "w") as f:
        json.dump({"duration": total, "shots": timeline}, f, indent=1, ensure_ascii=False)
    print("total", total, "s")


if __name__ == "__main__":
    main()
