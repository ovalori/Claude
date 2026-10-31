"""Write the HyperFrames composition for the mini film from mini_timeline.json.

Usage: python3 -I vlog/make_mini_comp.py <mini_timeline.json> <project_dir>
Small centered title on the first shot (like the template's "A FILM BY"), logo on black at the end.
"""
import json
import sys

tl = json.load(open(sys.argv[1]))
total, title, card_at = tl["duration"], tl["title"], tl["card_at"]
card_dur = round(total - card_at, 3)

page = f"""<!doctype html>
<html lang="en" data-resolution="landscape">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      :root {{ --ink: #f6efe4; --gold: #f2c14e; --font-small: "Outfit"; --font-serif: "Playfair Display"; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; }}
      #footage {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; object-fit: cover; }}
      .centered {{
        position: absolute; left: 0; top: 0; width: 1920px; height: 1080px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        color: var(--ink); text-align: center;
      }}
      .small {{ font: 600 22px var(--font-small); letter-spacing: 0.42em; text-transform: uppercase; }}
      .serif {{ font: italic 400 46px var(--font-serif); margin-top: 10px; letter-spacing: 0.02em; }}
      #title {{ text-shadow: 0 2px 18px rgba(0, 0, 0, 0.45); }}
      #logo {{ width: 700px; height: auto; }}
      #card .small {{ margin-top: 30px; color: var(--gold); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1920" data-height="1080">
      <video id="footage" class="clip" src="assets/mini_base.mp4" data-start="0" data-duration="{total}" data-track-index="0" data-has-audio="true" playsinline></video>
      <div id="title" class="centered clip" data-start="{title['at']}" data-duration="{title['dur']}" data-track-index="1">
        <div id="title-small" class="small">A mini film</div>
        <div id="title-serif" class="serif">Chosen Gen · North Luzon 2026</div>
      </div>
      <div id="card" class="centered clip" data-start="{card_at}" data-duration="{card_dur}" data-track-index="1">
        <img id="logo" src="assets/logo.png" alt="Chosen Gen" />
        <div id="card-small" class="small">until next camp ✦</div>
      </div>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo(["#title-small", "#title-serif"], {{ opacity: 0 }}, {{ opacity: 1, duration: 1.2, stagger: 0.3, ease: "power2.out" }}, {title['at'] + 0.2});
      tl.to(["#title-small", "#title-serif"], {{ opacity: 0, duration: 0.8, ease: "power2.in" }}, {title['at'] + title['dur'] - 0.9});
      tl.fromTo("#logo", {{ opacity: 0, scale: 0.96 }}, {{ opacity: 1, scale: 1, duration: 1.2, ease: "power2.out" }}, {card_at + 0.2});
      tl.fromTo("#card-small", {{ opacity: 0 }}, {{ opacity: 1, duration: 1.0, ease: "power2.out" }}, {card_at + 0.9});
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
open(f"{sys.argv[2]}/index.html", "w").write(page)
print("mini film composition written")
