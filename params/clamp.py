"""
CLAMP LAYOUT — the angular plan both shells derive from.

Neither shell owns the split. Both read it from here, so moving the hinge or the
lever moves the mating feature on the other half in the same edit.

Angular convention, looking down the pole axis (Z up):

        90 deg  = +Y   aft, behind the pole
       180 deg  = -X   LEVER side
       270 deg  = -Y   forward, where the boom exits
         0 deg  = +X   HINGE side

    swing shell wraps the +Y half, fixed shell wraps the -Y half, and the two
    gaps at 0 and 180 deg are where the hinge knuckles and the lever live.

The boom exits at 270 deg on the FIXED shell, so the load path runs boom -> fixed
shell -> pole without crossing the hinge or the lever. Neither the hinge pin nor
the lever link is in the suspended path; they only close the band. That is the
single most important thing about this layout: the mechanism cannot drop the
speaker because the mechanism is not carrying it.
"""

from __future__ import annotations

HINGE_DEG = 0.0
BOOM_DEG = 270.0
LEVER_DEG = 180.0

# Each shell wraps this much. The remainder is split between the two gaps.
SHELL_WRAP_DEG = 170.0
FIXED_CENTRE_DEG = 270.0
SWING_CENTRE_DEG = 90.0

# --- Hinge ------------------------------------------------------------------
# Two knuckles on the fixed shell, one between them on the swing shell. The odd
# count puts the swing half's single knuckle in double shear, which is what a
# hinge should be.
HINGE_PIN_D = 4.0                # M4 plain dowel, not threaded — see BOM
HINGE_KNUCKLE_W = 12.0
HINGE_KNUCKLE_GAP = 1.0
HINGE_BOSS_R = 6.0               # material around the pin bore
# Standoff is DERIVED from the boss radius, not chosen. If the axis sits closer
# to the shell than the boss is wide, the boss reaches back inside the band OD —
# where it collides with the OTHER shell's band, because the hinge axis is shared
# and each boss is a full cylinder. Both shells still validate alone; the clamp
# simply cannot close. Keeping the boss entirely outboard of the band is the
# structural condition that makes a shared-axis hinge possible at all.
BOSS_CLEAR = 0.6                 # air between boss inner face and band OD
HINGE_STANDOFF = HINGE_BOSS_R + BOSS_CLEAR

# --- Lever ------------------------------------------------------------------
# The pivot and the catch must sit on OPPOSITE sides of the parting gap, each on
# its own shell. Putting both at LEVER_DEG makes them coaxial, which is
# geometrically degenerate: pivot_to_catch collapses toward zero and the required
# link length goes NEGATIVE. An over-centre linkage needs a real base distance to
# swing the crank through.
#
# Pivot goes just inside the FIXED shell's span, catch just inside the SWING
# shell's. Each therefore stays clear of the other shell's band without relying
# on any trim.
# Which shell hosts which matters, and not for a subtle reason: the lever arm is
# 58 mm long and sweeps in the plane of the band. With the pivot on the FIXED
# (forward) side the arm swings toward 270 deg — straight into the bayonet collar,
# 3.6 cm^3 of interference. Pivot on the SWING (aft) side and the arm sweeps aft
# into open air.
#
# So: lever ears on the SWING half, catch pin on the FIXED half. The mechanism is
# identical either way; only the swept volume differs.
LEVER_PIVOT_DEG = LEVER_DEG - 24.0      # 156 deg, inside the SWING wrap
CATCH_DEG = LEVER_DEG + 24.0            # 204 deg, inside the FIXED wrap
# 24 deg, not 15: at 15 the pivot-to-catch chord is only 25 mm, and the crank has
# to be longer than LEVER_BOSS_R + LINK_END_R (12.5 mm) or the link's end boss
# intersects the lever's own pivot boss. A 13 mm crank then leaves too little
# chord for a buildable link. Widening the spread fixes both at once.

LEVER_PIVOT_D = 5.0        # M5 clevis pin, steel
LEVER_EAR_W = 9.0
# 9, not 6. At 6 mm the two ears give 60 mm^2 of bearing against the steel pivot
# pin and the gauntlet put this at 1.10x — the weakest member in the assembly, and
# it was bearing-on-plastic, the least forgiving kind of margin to run thin. The
# band is 73 mm tall, so the width is free.
LEVER_EAR_GAP = 20.0             # clear space between ears for the lever blade
LEVER_BOSS_R = 6.0
# Standoff has TWO drivers, and the second one is easy to miss. Besides keeping the
# boss outboard of the band (as the hinge does), the axis must be far enough out
# that the LINK — which runs as a chord between the pivot and the catch — clears
# the band with its full width. The chord's closest approach to the pole axis is
# r_axis * cos(offset), and half the strap sits inboard of that.
#
# At the boss-only standoff the link's inner edge sat 1.6 mm INSIDE the band OD.
LINK_STRAP_W = 8.0          # must equal lever.LINK_W — asserted in tests
LINK_BAND_CLEAR = 2.0


def _lever_standoff() -> float:
    from math import cos, radians
    boss_driven = LEVER_BOSS_R + BOSS_CLEAR
    # Solved from: r_axis*cos(offset) - LINK_STRAP_W/2 >= r_out + LINK_BAND_CLEAR
    # expressed as a standoff, using the shell OD as the reference radius.
    from . import derived as _D
    d = _D.compute()
    r_out = d.shell_bore_d / 2.0 + d.shell_wall_t
    need_axis = (r_out + LINK_BAND_CLEAR + LINK_STRAP_W / 2.0) / cos(radians(24.0))
    return max(boss_driven, need_axis - r_out)


LEVER_STANDOFF = LEVER_BOSS_R + BOSS_CLEAR   # boss-driven floor; see lever_standoff()
# The catch the link pulls against, on the swing half.
CATCH_PIN_D = 5.0
CATCH_BOSS_R = 5.5

# --- Boom / collar mounting pad ---------------------------------------------
# Flat pad on the fixed shell at BOOM_DEG carrying M5 heat-set inserts. Four
# bolts in a rectangle rather than two, so the pad resists the boom's moment as
# a couple instead of relying on bolt bending.
PAD_W = 46.0
PAD_H = 62.0
PAD_T = 5.0
M5_BOSS_D = 9.0
M5_INSERT_D = 6.4                # heat-set insert OD; bore is this minus the
                                 # named interference in clearances.py
M5_INSERT_DEPTH = 9.5
PAD_BOLT_DX = 30.0
PAD_BOLT_DZ = 42.0

# --- Liner ------------------------------------------------------------------
# The liner wraps further than the shell so its edge, not the shell's, is what
# meets the pole at the parting lines. A printed shell edge on powder coat is
# exactly the point load priority 2 forbids.
LINER_WRAP_EXTRA_DEG = 6.0
LINER_LIP_H = 2.0                # small lip top and bottom so it cannot walk out

# --- Shim -------------------------------------------------------------------
SHIM_WRAP_DEG = 150.0            # narrower than the liner; it only takes up slack
SHIM_HEIGHT_FRACTION = 0.85      # of the band height, so it cannot foul the lips


def lever_standoff() -> float:
    """Lever axis standoff, whichever driver is larger. Lazy: needs derived."""
    return _lever_standoff()


def fixed_arc() -> tuple[float, float]:
    return FIXED_CENTRE_DEG, SHELL_WRAP_DEG


def swing_arc() -> tuple[float, float]:
    return SWING_CENTRE_DEG, SHELL_WRAP_DEG


def gap_deg() -> float:
    """Angular gap at each parting line, before the mechanism is added."""
    return (360.0 - 2.0 * SHELL_WRAP_DEG) / 2.0
