# Edit list for vlog v5: about 2:15, day by day, slow -> build -> slow.
# Shots picked from a second-by-second scan of every clip (faces, sharpness, shake).
#   ("clip", in_s, secs[, "t"])   cold open, timed in seconds ("t" keeps camp sound)
#   ("clip", in_s, n)             song shot lasting n beats of "Washed" (camp sound low)
#   ("clip", in_s, secs, "t")     song talking shot; its end snaps to the next beat
COLD_OPEN = [
    ("0189", 0.8, 3.6, "t"),   # "Hi guys! Hi to my vlog, guys!"
    ("0184", 4.75, 3.0),
]

SONG = [
    # April 29, the night before: slow holds. The logo sits on the first shot.
    ("0190", 0.0, 8),
    ("0190", 14.75, 6),
    # April 30 morning.
    ("0197", 37.0, 6),
    ("0203", 0.0, 6),
    ("0206", 8.0, 8),
    ("0191", 43.0, 6),
    ("0207", 0.0, 4),
    ("0210", 0.0, 3.8, "t"),   # "Hi vlog! Day 1!"
    # Day one builds: registration, meals, sessions.
    ("0215", 1.0, 4),
    ("0216", 0.0, 4),
    ("0217", 1.0, 4),
    ("0215", 12.0, 4),
    ("0224", 14.0, 4),
    ("0226", 86.0, 4),
    ("0226", 131.0, 4),
    ("0222", 17.0, 4),
    ("0226", 156.0, 4),
    # Bonfire night: slow again, the talk carries it.
    ("0227", 9.0, 4),
    ("0227", 4.9, 5.2, "t"),   # "Papunta na po kami sa bonfire. Dorm 1B!"
    ("0229", 6.0, 8),
    ("0228", 0.0, 8.0, "t"),   # "There are times… nanglalamig ako sa Lord."
    ("0228", 38.4, 10.4, "t"), # "…the Holy Spirit living inside of us…"
    ("0227", 268.0, 6),
    ("0230", 10.0, 6),
    # May 1 games: fast.
    ("0233", 31.0, 4),
    ("0234", 10.0, 2),
    ("0234", 31.0, 2),
    # May 2: pickleball, photos, the walk out.
    ("0241", 6.5, 7.8, "t"),   # "This is me, day 2 of the camp. Pickleballs!"
    ("0241", 25.0, 2),
    ("0241", 73.0, 2),
    ("0242", 18.0, 2),
    ("0243", 1.0, 2),
    ("0243", 163.0, 2),
    ("0243", 247.0, 2),
    ("0247", 50.0, 4),
    ("0248", 142.0, 4),
    ("0251", 5.0, 2),
    ("0253", 4.0, 2),
    ("0254", 2.0, 4),
    ("0255", 0.0, 3.5, "t"),   # "1, 2, 3! Hug pose! Open arms!"
    ("0254", 24.0, 4),
    ("0258", 15.0, 2),
    ("0263", 3.0, 4),
    ("0264", 4.0, 4),
    # May 2 party night.
    ("0271", 14.0, 4),
    ("0271", 37.0, 4),
    ("0272", 7.0, 4),
    # May 3, last day: slow to the end.
    ("0273", 3.0, 6),
    ("0274", 58.0, 8),
    ("0278", 0.0, 4.2, "t"),   # "This is my last day! Cheers!"
    ("0278", 42.0, 6),
    ("0183", 25.0, 8),
]
