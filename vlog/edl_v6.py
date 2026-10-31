# Edit list for vlog v6: a short documentary. Voices from the camp carry it; "Washed" plays
# under the two montages; "A Pad" sits under every spoken part.
#
# Segment kinds:
#   ("voice", [(clip, from_s, to_s), ...], [(clip, in_s, secs), ...], dip_in, dip_out)
#       the ranges play back to back as the voice; the shots (camp sound low) cover it, and the
#       last shot is stretched or trimmed to end with the voice.
#   ("nat", (clip, in_s, secs))        one shot with its own sound up, pad low underneath.
#   ("song", from_beat, shots, fade_out, dip_out)
#       beat-cut montage on "Washed" starting at that beat. Shot forms as in edl_v5.
#   ("card", secs)                     logo on black, pad fading out.
SEGMENTS = [
    ("voice",
     [("0236", 258.6, 265.9), ("0236", 291.0, 294.0)],
     # "Have you ever felt like you have to prove yourself first…" / "Very young people feel that pressure."
     [("0184", 4.0, 3.6), ("0185", 30.0, 3.6), ("0183", 0.0, 3.0)],
     False, False),
    ("nat", ("0189", 0.8, 3.6)),       # "Hi guys! Hi to my vlog, guys!"
    ("song", 0, [
        ("0190", 0.0, 8),              # logo
        ("0206", 8.0, 6),
        ("0197", 37.0, 6),
        ("0203", 0.0, 6),
        ("0191", 43.0, 6),
        ("0210", 0.0, 3.8, "t"),       # "Hi vlog! Day 1!"
        ("0215", 1.0, 4),
        ("0216", 0.0, 4),
        ("0217", 1.0, 4),
        ("0224", 14.0, 4),
        ("0226", 81.4, 6.8, "t"),      # "Anong masasabi mo sa experience…?" "Masaya po!"
        ("0222", 17.0, 4),
        ("0226", 131.0, 4),
        ("0227", 4.9, 5.2, "t"),       # "Papunta na po kami sa bonfire. Dorm 1B!"
     ], 2.5, True),
    ("voice",
     [("0228", 0.0, 8.0), ("0228", 38.4, 48.8)],
     # "There are times that I don't feel like living… nanglalamig ako sa Lord…"
     # "…let's be reminded that it is the Holy Spirit living inside of us…"
     [("0228", 0.0, 8.0), ("0227", 268.0, 4.0), ("0229", 20.0, 4.0), ("0228", 41.0, 1.0)],
     True, False),
    ("voice",
     [("0236", 308.5, 316.2), ("0236", 397.6, 402.4), ("0236", 418.2, 425.9),
      ("0236", 426.6, 431.6), ("0236", 440.5, 444.3)],
     # "…we didn't earn our place" / "God chose us before the foundation of the world" /
     # "His choice is rooted in love and not on our performance" / "kahit anong gawin natin…" /
     # "Mahal ka ng Panginoon. At inibig ka niya."
     [("0230", 10.0, 4.5), ("0236", 140.0, 4.0), ("0212", 2.25, 4.0), ("0233", 31.0, 3.5),
      ("0213", 6.0, 3.5), ("0237", 59.0, 3.5), ("0245", 5.0, 4.0), ("0264", 4.0, 1.0)],
     False, False),
    ("song", 205, [
        ("0241", 6.5, 7.8, "t"),       # "This is me, day 2 of the camp. Pickleballs!"
        ("0243", 1.0, 2),
        ("0242", 18.0, 2),
        ("0241", 73.0, 2),
        ("0243", 163.0, 2),
        ("0247", 50.0, 4),
        ("0251", 5.0, 2),
        ("0248", 142.0, 4),
        ("0253", 4.0, 2),
        ("0254", 2.0, 4),
        ("0255", 0.0, 3.5, "t"),       # "1, 2, 3! Hug pose! Open arms!"
        ("0258", 15.0, 2),
        ("0254", 24.0, 4),
        ("0263", 3.0, 4),
        ("0271", 14.0, 4),
        ("0272", 7.0, 4),
        ("0271", 37.0, 4),
     ], 2.5, False),
    ("nat", ("0278", 0.0, 4.2)),       # "This is my last day! Cheers!"
    ("voice",
     [("0236", 457.5, 458.9), ("0236", 586.3, 590.9), ("0236", 593.5, 598.6)],
     # "He already chose you." / "you are invited to his dance of love and relationship" /
     # "you do not have to perform, we just have to follow the lead."
     [("0273", 3.0, 3.5), ("0274", 58.0, 4.0), ("0278", 42.0, 2.5), ("0183", 25.0, 1.0)],
     False, True),
    ("card", 6.0),
]
