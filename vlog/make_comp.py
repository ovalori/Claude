"""Write the HyperFrames composition (index.html) for the vlog from timeline.json.

Usage: python3 -I vlog/make_comp.py <timeline.json> <project_dir>
"""
import html
import json
import sys

timeline = json.load(open(sys.argv[1]))
out_dir = sys.argv[2]
total = timeline["duration"]
shots = timeline["shots"]

TITLE_SHOT, END_SHOT = 1, len(shots) - 1
SECTION_HOLD = 2.8

clips, tweens = [], []


def esc(s):
    return html.escape(s, quote=True)


# Opening title over the banner shot.
t = shots[TITLE_SHOT]
clips.append(
    f'<div id="title" class="card clip" data-start="{t["at"]}" data-duration="{t["dur"]}" data-track-index="1">'
    f'<div id="title-kicker" class="kicker">North Luzon · Weekend Youth Camp 2026</div>'
    f'<div id="title-big" class="big">Chosen Gen</div></div>'
)
tweens += [
    f'tl.fromTo("#title-kicker", rise, {{ ...land }}, {t["at"] + 0.2});',
    f'tl.fromTo("#title-big", rise, {{ ...land }}, {t["at"] + 0.35});',
    f'tl.to(["#title-kicker", "#title-big"], {{ opacity: 0, duration: 0.4, ease: "power2.in" }}, {t["at"] + t["dur"] - 0.5});',
]

# Closing card over the last banner shot.
e = shots[END_SHOT]
clips.append(
    f'<div id="outro" class="card clip" data-start="{e["at"]}" data-duration="{round(total - e["at"], 3)}" data-track-index="1">'
    f'<div id="outro-kicker" class="kicker">Chosen Gen</div>'
    f'<div id="outro-big" class="big">until next camp ✦</div></div>'
)
tweens += [
    f'tl.fromTo("#outro-kicker", rise, {{ ...land }}, {e["at"] + 0.3});',
    f'tl.fromTo("#outro-big", rise, {{ ...land }}, {e["at"] + 0.45});',
]

# Date labels at each section start.
for i, s in enumerate(shots):
    if not s["section"]:
        continue
    sid = f"sec{i}"
    clips.append(
        f'<div id="{sid}" class="section clip" data-start="{s["at"]}" data-duration="{SECTION_HOLD}" data-track-index="2">'
        f'<span id="{sid}-t">{esc(s["section"])}</span></div>'
    )
    tweens += [
        f'tl.fromTo("#{sid}-t", {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "power3.out" }}, {s["at"] + 0.1});',
        f'tl.to("#{sid}-t", {{ opacity: 0, duration: 0.3, ease: "power2.in" }}, {s["at"] + SECTION_HOLD - 0.35});',
    ]

# Captions on the talking shots.
n = 0
for s in shots:
    for c in s["captions"]:
        dur = round(c["end"] - c["start"], 3)
        if dur <= 0.2:
            continue
        cid = f"cap{n}"
        n += 1
        clips.append(
            f'<div id="{cid}" class="caption clip" data-start="{c["start"]}" data-duration="{dur}" data-track-index="3">'
            f'<span id="{cid}-t">{esc(c["text"])}</span></div>'
        )
        tweens.append(
            f'tl.fromTo("#{cid}-t", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.2, ease: "power2.out" }}, {c["start"]});'
        )

page = f"""<!doctype html>
<html lang="en" data-resolution="landscape">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      :root {{
        --ink: #fdf6e3;
        --accent: #f2c14e;
        --font-display: "Archivo Black";
        --font-body: "Outfit";
      }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; }}
      #footage {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; object-fit: cover; }}
      .card {{
        position: absolute; left: 50%; top: 330px; transform: translateX(-50%); width: max-content; max-width: 1536px;
        padding: 40px 72px 48px; border-radius: 28px; background: rgba(0, 0, 0, 0.5);
        display: flex; flex-direction: column; align-items: center; text-align: center;
        color: var(--ink); text-shadow: 0 4px 28px rgba(0, 0, 0, 0.6);
      }}
      .kicker {{ font-family: var(--font-body); font-weight: 600; font-size: 38px; letter-spacing: 0.3em; text-transform: uppercase; }}
      .big {{ font-family: var(--font-display); font-size: 132px; line-height: 1.02; margin-top: 14px; text-wrap: balance; }}
      .section {{ position: absolute; left: 160px; top: 110px; }}
      .section span {{
        display: inline-block; font-family: var(--font-body); font-weight: 700; font-size: 44px;
        color: var(--ink); padding: 10px 26px; border-left: 6px solid var(--accent);
        background: rgba(0, 0, 0, 0.45); letter-spacing: 0.04em;
      }}
      .caption {{ position: absolute; left: 192px; top: 860px; width: 1536px; text-align: center; }}
      .caption span {{
        display: inline-block; font-family: var(--font-body); font-weight: 700; font-size: 50px; line-height: 1.25;
        color: #fff; padding: 8px 22px; border-radius: 12px; background: rgba(0, 0, 0, 0.55);
      }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1920" data-height="1080">
      <video id="footage" class="clip" src="assets/vlog_base.mp4" data-start="0" data-duration="{total}" data-track-index="0" data-has-audio="true" playsinline></video>
      {chr(10).join("      " + c for c in clips).lstrip()}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      const rise = {{ opacity: 0, y: 40, filter: "blur(8px)" }};
      const land = {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.6, ease: "power3.out" }};
      {chr(10).join("      " + tw for tw in tweens).lstrip()}
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
open(f"{out_dir}/index.html", "w").write(page)
print(f"{len(clips)} overlay clips, {n} captions")
