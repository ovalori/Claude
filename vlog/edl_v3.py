# Edit list for vlog v3, structured like the SEP North Luzon reference film:
# cold open on the pad -> part 1 montage on "Washed" -> black -> part 2, the bonfire talk as
# voiceover over b-roll with the pad -> black -> part 3 montage as the song resumes -> title on black.
#
# Shot forms:
#   ("clip", in_s, secs[, "t"])   cold open / voiceover b-roll, timed in seconds ("t" keeps camp sound)
#   ("clip", in_s, n)             song montage shot lasting n beats (camp sound low)
#   ("clip", in_s, secs, "t")     song talking shot; its end snaps to the next beat
from edl_v2 import COLD_OPEN, SONG

_part1_end = SONG.index(("0226", 154.0, 4)) + 1
PART1 = SONG[:_part1_end] + [
    ("0227", 46.0, 4),
    ("0227", 4.9, 5.2, "t"),   # "Papunta na po kami sa bonfire. Dorm 1B!"
]

# Part 2: the bonfire talk plays whole as the voice; these shots cover it (they must sum to its length).
VOICE = ("0228", 0.0, 48.8)
VOICE_BROLL = [
    ("0228", 0.0, 8.0),    # the speaker at the fire, in sync
    ("0227", 145.0, 4.0),
    ("0229", 4.0, 4.0),
    ("0230", 3.0, 5.0),
    ("0236", 220.0, 4.0),
    ("0195", 0.5, 4.0),
    ("0222", 8.0, 4.0),
    ("0237", 45.0, 4.0),
    ("0229", 15.0, 4.0),
    ("0228", 41.0, 7.8),   # back to the fire for "…a fire to each and every one of us"
]

_games = SONG.index(("0231", 2.0, 4))
_last = SONG.index(("0273", 2.0, 4))
PART3 = SONG[_games:_last] + [
    # Nature and wide shots between moments, like the reference's leaves and sky.
    ("0262", 1.0, 4),
    ("0244", 2.0, 4),
    ("0245", 5.0, 4),
    ("0249", 3.0, 4),
    ("0252", 30.0, 4),
    ("0253", 20.0, 4),
    ("0241", 30.0, 4),
    ("0241", 60.0, 4),
    ("0257", 3.0, 2),
    ("0259", 3.0, 2),
    ("0261", 1.0, 4),
    ("0269", 5.0, 4),
    ("0269", 20.0, 4),
    ("0265", 6.0, 2),
    ("0273", 22.0, 4),
    ("0274", 10.0, 4),
    ("0274", 150.0, 4),
] + SONG[_last:]

# Clean-up pass: drop shots that show feet, backs, lens-blocking hands or blur, and the stutter.
DROP = {
    ("0211", 16.0), ("0218", 5.0), ("0223", 4.0), ("0225", 22.0),
    ("0231", 8.0), ("0235", 10.0), ("0238", 7.0), ("0256", 3.0), ("0265", 1.0),
    ("0268", 2.0), ("0270", 7.0), ("0262", 1.0), ("0257", 3.0), ("0274", 150.0),
    ("0248", 160.0), ("0248", 160.6), ("0248", 161.2), ("0248", 161.8),
}
# Steadier in-points found within a few seconds of the original moment: (clip, old_in) -> new_in.
STEADY = {}


def _clean(shots):
    return [(s[0], STEADY.get((s[0], s[1]), s[1]), *s[2:]) for s in shots if (s[0], s[1]) not in DROP]


PART1 = _clean(PART1)
PART3 = _clean(PART3)
VOICE_BROLL = [("0228", 25.0, 4.0) if s[:2] == ("0227", 145.0) else s for s in VOICE_BROLL]
VOICE_BROLL = _clean(VOICE_BROLL)

# The opening logo reads better over the dark night shot than on top of the real banner.
_a, _b = PART1.index(("0183", 21.5, 8)), PART1.index(("0190", 2.0, 8))
PART1[_a], PART1[_b] = PART1[_b], PART1[_a]
