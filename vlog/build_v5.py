"""Vlog v5: one continuous beat-cut on "Washed" after a short cold open on the pad.

Usage: python3 -I vlog/build_v5.py <proxy_dir> <music_dir> <work_dir>
Writes <work_dir>/vlog_v5.mp4 and <work_dir>/timeline_v5.json.
Reuses the cutting, grading and mixing helpers of build_v3.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_v3 as b  # noqa: E402
from edl_v5 import COLD_OPEN, SONG  # noqa: E402

CARD = 6.0  # logo on black while the song fades


def main():
    b.OUT = os.path.join(b.WORK, "v5")
    os.makedirs(b.OUT, exist_ok=True)
    beats = json.load(open(os.path.join(b.MUSIC, "washed_beats.json")))

    paths = [b.cut(f"open_{k}", s[0], s[1], s[2], b.CAMP_TALK if len(s) > 3 else b.CAMP_MONTAGE)
             for k, s in enumerate(COLD_OPEN)]
    open_v = b.join("open_video", paths)
    open_len = b.duration(open_v)
    open_mix = os.path.join(b.OUT, "open.mp4")
    b.run("-i", open_v, "-i", os.path.join(b.MUSIC, "pad.mp3"), "-filter_complex",
          f"[1:a]atrim=0:{open_len},loudnorm=I=-20:TP=-2,afade=t=in:d=1.0,"
          f"afade=t=out:st={open_len - 1.2}:d=1.2,aresample=48000[p];"
          f"[0:a][p]amix=inputs=2:duration=first:normalize=0[a]",
          "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", open_mix)

    video, span, laid, _ = b.song_part("s", SONG, beats, 0)
    shots_len = b.duration(video)
    with_card = b.join("s_card_video", [video, b.black("card", CARD)])
    song = b.mix_song("s", with_card, (span[0], span[1] + CARD), laid, fade_in=0.05, fade_out=4.0)

    final = os.path.join(b.WORK, "vlog_v5.mp4")
    lst = os.path.join(b.OUT, "parts.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in (open_mix, song))
    b.run("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", final)

    total = b.duration(final)
    json.dump({"duration": round(total, 3), "song_start": round(open_len, 3),
               "card_at": round(open_len + shots_len, 3), "card_dur": round(total - open_len - shots_len, 3),
               "parts": [{"part": "part1", "at": round(open_len, 3), "dur": round(shots_len, 3), "shots": laid}]},
              open(os.path.join(b.WORK, "timeline_v5.json"), "w"), indent=1)
    print(f"{total:.1f} s, {len(laid)} song shots")


if __name__ == "__main__":
    main()
