"""
SIMPLE POLE BRACKET — every number, in one block.

This supersedes the over-centre/bayonet design. Two printed parts, two bolts, two
heat-set inserts. No hinge pin, no lever, no link, no detent balls, no springs, no
clips, no pitch index, no TPU nose. Print, insert, bolt, done.

What got deleted and why it was safe to delete it:

  Over-centre lever + steel link + 2 clevis pins + 2 R-clips
      A bolted split clamp reaches the same preload with a hex key. The toggle
      only earned its place if you needed tool-free release, and you don't.

  Hinge pin + 2 retainers + 3-knuckle interleave
      Two loose halves and two bolts assemble just as fast and cannot bind.

  Bayonet collar + spigot + 3 detent balls + 3 springs
      The cradle no longer detaches from the clamp at all. One rigid bracket.

  Pitch index plate + 2 pins + rear handle hook + TPU nose
      Level only. That also deletes the four unpublished handle-recess numbers —
      the speaker sits in a saddle like a cup instead of being hooked.

Two unknowns disappear entirely as a side effect:

  Pole OD (62-65 mm)   The bolted split clamp closes onto whatever is there. No
                       gauge coupon, no shim set. This is the big win.
  Base footprint       The saddle floor is open, so a charging base of any
                       plausible size drops in and the cable falls through.

RETARGETING TO A DIFFERENT SPEAKER: edit SPEAKER_W / SPEAKER_D below and nothing
else. Every saddle dimension derives from them.
"""

from __future__ import annotations

# ===========================================================================
# SPEAKER — the only block to edit for a different model
# ===========================================================================
# Sonos Move 2. Verified: 241 x 160 x 127 mm, 3.0 kg, IP56.
SPEAKER_W = 160.0
SPEAKER_D = 127.0
SPEAKER_H = 241.0
SPEAKER_MASS_G = 3000.0
BASE_MASS_G = 150.0

# For reference if you retarget — Sonos One is 161.45 tall x 119.7 dia, 1.85 kg.
# It is round, so the saddle would want a circular pocket rather than a
# rectangular one; say the word and I will switch the saddle profile.

# ===========================================================================
# POLE — a range, and the clamp simply closes onto it
# ===========================================================================
POLE_D_MAX = 65.0          # 2.56 in
POLE_D_MIN = 62.0          # 2.44 in
# Bore is cut for the LARGEST pole plus a little. Protective tape lines it, and
# the bolts take up whatever is left. A smaller pole just means the flanges pull
# closer together — there is nothing to select and nothing to shim.
BORE_CLEARANCE = 1.0
TAPE_T = 2.0               # adhesive EPDM/rubber tape, protects the rented pole

BAND_H = 55.0              # collar height up the pole
COLLAR_WALL = 5.0

# ===========================================================================
# CLAMP FLANGES — 2 x M5, heat-set inserts one side
# ===========================================================================
# ONE BOLT PER SIDE, at each end of the collar's split — which is how a split
# clamp actually works. The bracket wraps the front, the backer wraps the back,
# and the two bolts pull them together along Y until they grip the pole.
SPLIT_Y = -4.0             # the mating plane, at the collar ends
# Gap must allow enough travel to reach the SMALLEST pole. Free bore with tape is
# 66 mm; gripping a 62 mm pole means closing 4 mm, so the gap has to exceed that
# with margin. At 3.5 mm the clamp bottomed out at 63.4 mm and would not have
# gripped a 62 mm pole at all.
SPLIT_GAP = 6.0            # open gap between the pads; closes as you tighten
FLANGE_W = 17.0            # pad width, across the bolt
FLANGE_H_FRAC = 0.86       # pad height as a fraction of the band
FLANGE_INSERT_T = 12.0     # thick enough for a 9.5 mm M5 insert plus a floor
FLANGE_BOLT_T = 10.0
BOLT_D = 5.0
BOLT_CLEAR_D = 5.4
# NO COUNTERBORE, and use a PENNY WASHER under each head.
#
# At 172 N per bolt, an M5 cap head sunk in a 9.4 mm counterbore bears on 46 mm^2
# of PETG = 3.7 MPa, over the 3.15 MPa sustained allowable — it would slowly sink
# into the flange and the clamp would lose preload. A 15 mm penny washer on an
# uncounterbored face spreads the same load over 154 mm^2 = 1.1 MPa, and it
# leaves the full flange thickness behind the head.
WASHER_OD = 15.0           # M5 penny/fender washer
INSERT_D = 6.4             # M5 brass heat-set OD
INSERT_DEPTH = 9.5
INSERT_INTERFERENCE = -0.05   # bore slightly UNDER insert OD so brass bites
BOLT_Z_FRACTIONS = (0.25, 0.75)   # two bolts, spread up the band

# ===========================================================================
# ARM — twin webs, collar to saddle
# ===========================================================================
# The arm SPLAYS in plan: narrow where it leaves the collar, wide where it meets
# the saddle, so the load path reaches the saddle's outer thirds instead of leaving
# them cantilevered 57 mm off a pair of parallel webs. It is a vertical-walled
# shell open at the top, with the saddle floor closing the bottom — which in the
# print orientation means no overhang anywhere.
WEB_T = 5.0                # shell wall thickness
ARM_W_COLLAR = 52.0        # plan width where it leaves the collar
ARM_W_SADDLE = 128.0       # plan width where it lands on the saddle
# The arm's top TAPERS from full band height at the collar down to a low rail at
# the saddle. The bending moment falls off toward the tip, so the depth should
# too. In the saddle-down print orientation this costs nothing: the walls simply
# get shorter, so there is no new overhang — and it takes ~100 g out.
ARM_H_TIP = 20.0
SPEAKER_TO_COLLAR = 6.0    # air between the speaker's back and the collar OD

# ===========================================================================
# SADDLE — the cup the speaker stands in
# ===========================================================================
SADDLE_T = 5.0
LIP_H = 11.0               # front and side retention lip
LIP_T = 3.5
LOCATE_CLEARANCE = 1.5     # so a cold wet speaker still drops in
RIM_W = 11.0               # width of the floor rim the speaker bears on
# Floor is open in the middle: a charging base of any plausible size sits in it
# and the cable falls straight through instead of pooling water.
CROSS_RIB_W = 8.0
CROSS_RIB_COUNT = 2

# ===========================================================================
# BACKSTOP — anti-topple, no handle-recess dimensions needed
# ===========================================================================
BACKSTOP_H = 52.0          # rises behind the speaker
BACKSTOP_W = 118.0         # narrower than the saddle; it only needs to catch the
                           # speaker's back, not span the full width
BACKSTOP_T = 4.5
BACKSTOP_LIP = 7.0         # small forward return at the top, an anti-roll catch

# ===========================================================================
# PRINT
# ===========================================================================
FILLET_R = 2.5
CHAMFER = 1.0


def bore_d() -> float:
    """Bore must swallow the biggest pole PLUS the tape lining it.

    Omitting the tape gave a bore of 66 mm and a grip range of 56-62 mm — a clamp
    that physically would not go onto a 65 mm pole at all.
    """
    return POLE_D_MAX + 2.0 * TAPE_T + BORE_CLEARANCE


def collar_od() -> float:
    return bore_d() + 2.0 * COLLAR_WALL


def grip_min() -> float:
    """Smallest pole the clamp still grips, with tape fitted.

    The two halves can travel together by the full SPLIT_GAP before the pads meet,
    and each mm of travel takes ~1 mm out of the clamped dimension.
    """
    return bore_d() - 2.0 * TAPE_T - SPLIT_GAP


def grip_max() -> float:
    return bore_d() - 2.0 * TAPE_T


def saddle_w() -> float:
    return SPEAKER_W + 2.0 * LOCATE_CLEARANCE + 2.0 * LIP_T


def saddle_d() -> float:
    return SPEAKER_D + 2.0 * LOCATE_CLEARANCE + LIP_T


def saddle_centre_y() -> float:
    """Forward offset of the saddle centre from the pole axis (negative = forward)."""
    return -(collar_od() / 2.0 + SPEAKER_TO_COLLAR + SPEAKER_D / 2.0)


def arm_reach() -> float:
    return abs(saddle_centre_y()) - SPEAKER_D / 2.0 - collar_od() / 2.0


def suspended_mass_g() -> float:
    return SPEAKER_MASS_G + BASE_MASS_G


def load_n() -> float:
    return suspended_mass_g() / 1000.0 * 9.80665


def moment_nmm() -> float:
    """About the pole axis. Level only, so this is the whole load case."""
    return load_n() * abs(saddle_centre_y())
