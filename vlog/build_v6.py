"""Vlog v6: documentary cut. Voices carry it, "Washed" under the montages, the pad under speech.

Usage: python3 -I vlog/build_v6.py <proxy_dir> <music_dir> <work_dir>
Writes <work_dir>/vlog_v6.mp4 and <work_dir>/timeline_v6.json.
Reuses the cutting, grading and mixing helpers of build_v3. Refuses to build if any footage
repeats or one clip follows itself.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_v3 as b  # noqa: E402
from edl_v6 import SEGMENTS  # noqa: E402

GAP = 0.45          # silence between voice lines
VOICE_AMBIENCE = 0.1
PAD_LUFS = -24      # pad under speech
PAD_NAT_LUFS = -27  # pad under natural-sound shots


def check(visual):
    """visual: [(clip, in, dur)] in film order. No repeated footage, no clip followed by itself."""
    errs = []
    for k, (c, a, d) in enumerate(visual):
        if k and visual[k - 1][0] == c:
            errs.append(f"clip {c} follows itself at shot {k}")
        for c2, a2, d2 in visual[k + 1:]:
            if c == c2 and a < a2 + d2 - 0.05 and a2 < a + d - 0.05:
                errs.append(f"clip {c} repeats footage: {a}+{d:.1f} and {a2}+{d2:.1f}")
    if errs:
        sys.exit("\n".join(errs))


def pad_bed(name, length, offset, lufs, fade_in, fade_out):
    out = os.path.join(b.OUT, f"{name}.wav")
    b.run("-ss", str(offset), "-t", str(length), "-i", os.path.join(b.MUSIC, "pad.mp3"), "-af",
          f"loudnorm=I={lufs}:TP=-3,aresample=48000,afade=t=in:d={fade_in},"
          f"afade=t=out:st={max(length - fade_out, 0)}:d={fade_out},apad,atrim=0:{length}",
          "-ac", "2", out)
    return out


def voice_track(name, ranges):
    ins, parts = [], []
    for k, (c, a, e) in enumerate(ranges):
        ins += ["-ss", str(a), "-t", str(e - a), "-i", b.clip_path(c)]
        parts.append(f"[{k}:a]loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000,afade=t=in:d=0.08,"
                     f"afade=t=out:st={e - a - 0.12}:d=0.12,apad=pad_dur={GAP}[v{k}]")
    chain = ";".join(parts) + ";" + "".join(f"[v{k}]" for k in range(len(ranges))) + \
        f"concat=n={len(ranges)}:v=0:a=1[a]"
    out = os.path.join(b.OUT, f"{name}.wav")
    b.run(*ins, "-filter_complex", chain, "-map", "[a]", "-ac", "2", out)
    return out, b.duration(out)


def mix(name, video, layers):
    """layers: audio files laid over the video's own sound, all from 0."""
    ins = ["-i", video]
    for f in layers:
        ins += ["-i", f]
    n = len(layers) + 1
    out = os.path.join(b.OUT, f"{name}.mp4")
    b.run(*ins, "-filter_complex",
          "".join(f"[{k}:a]" for k in range(n)) + f"amix=inputs={n}:duration=first:normalize=0,alimiter=limit=0.95[a]",
          "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", out)
    return out


def main():
    b.OUT = os.path.join(b.WORK, "v6")
    os.makedirs(b.OUT, exist_ok=True)
    beats = json.load(open(os.path.join(b.MUSIC, "washed_beats.json")))

    # Plan the visual order first and refuse doubled footage before spending time cutting.
    visual = []
    for seg in SEGMENTS:
        if seg[0] == "voice":
            visual += [(c, a, d) for c, a, d in seg[2]]
        elif seg[0] == "nat":
            visual.append(seg[1])
        elif seg[0] == "song":
            visual += [(s[0], s[1], s[2] if len(s) > 3 else s[2] * 0.441) for s in seg[2]]
    check(visual)

    parts, timeline, t, pad_at, logo_at, card_at = [], [], 0.0, 0.0, None, None
    for k, seg in enumerate(SEGMENTS):
        name = f"seg{k}"
        if seg[0] == "voice":
            _, ranges, shots, dip_in, dip_out = seg
            voice, vlen = voice_track(f"{name}_voice", ranges)
            fixed = sum(s[2] for s in shots[:-1])
            last = shots[-1]
            shots = shots[:-1] + [(last[0], last[1], round(vlen - fixed, 3))]
            if shots[-1][2] < 1.0:
                sys.exit(f"{name}: shots run longer than the voice ({vlen:.1f} s)")
            video = b.join(f"{name}_video", [b.cut(f"{name}_{i}", c, a, d, VOICE_AMBIENCE)
                                             for i, (c, a, d) in enumerate(shots)])
            pad = pad_bed(f"{name}_pad", vlen, pad_at, PAD_LUFS, 1.5, 1.5)
            pad_at += vlen
            out = mix(name, video, [voice, pad])
            if dip_in or dip_out:
                out = b.dip(out, dip_in, dip_out)
            timeline.append({"kind": "voice", "at": round(t, 3), "dur": round(vlen, 3), "shots": shots})
        elif seg[0] == "nat":
            c, a, d = seg[1]
            video = b.cut(f"{name}_0", c, a, d, b.CAMP_TALK)
            pad = pad_bed(f"{name}_pad", d, pad_at, PAD_NAT_LUFS, 0.6, 0.8)
            pad_at += d
            out = mix(name, video, [pad])
            timeline.append({"kind": "nat", "at": round(t, 3), "dur": d, "shots": [seg[1]]})
        elif seg[0] == "song":
            _, from_beat, shots, fade_out, dip_out = seg
            video, span, laid, _ = b.song_part(name, shots, beats, from_beat)
            out = b.mix_song(name, video, span, laid, fade_in=0.05 if from_beat == 0 else 0.8,
                             fade_out=fade_out)
            if dip_out:
                out = b.dip(out, False, True)
            if logo_at is None:
                logo_at = (round(t, 3), round(laid[0]["dur"], 3))
            timeline.append({"kind": "song", "at": round(t, 3), "dur": round(span[1] - span[0], 3), "shots": laid})
        else:  # card
            d = seg[1]
            card = b.black(f"{name}_black", d)
            pad = pad_bed(f"{name}_pad", d, pad_at, PAD_LUFS, 0.3, d - 0.5)
            out = mix(name, card, [pad])
            card_at = (round(t, 3), d)
        parts.append(out)
        t += b.duration(out)

    final = os.path.join(b.WORK, "vlog_v6.mp4")
    lst = os.path.join(b.OUT, "parts.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    b.run("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", final)
    total = b.duration(final)

    # Same shape make_comp.py reads for v3-v5: logo over the first song shot, card at the end.
    json.dump({"duration": round(total, 3), "song_start": logo_at[0], "card_at": card_at[0],
               "card_dur": round(total - card_at[0], 3),
               "parts": [{"part": "part1", "at": logo_at[0], "dur": logo_at[1],
                          "shots": [{"dur": logo_at[1]}]}],
               "segments": timeline},
              open(os.path.join(b.WORK, "timeline_v6.json"), "w"), indent=1)
    print(f"{total:.1f} s in {len(SEGMENTS)} segments, {len(visual)} shots")


if __name__ == "__main__":
    main()
