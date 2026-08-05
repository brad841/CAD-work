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
LEVER_PIVOT_D = 4.0
LEVER_EAR_W = 6.0
LEVER_EAR_GAP = 14.0             # clear space between ears for the lever blade
LEVER_BOSS_R = 6.0
LEVER_STANDOFF = LEVER_BOSS_R + BOSS_CLEAR   # same reason as the hinge
# The catch the link pulls against, on the swing half.
CATCH_PIN_D = 4.0
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


def fixed_arc() -> tuple[float, float]:
    return FIXED_CENTRE_DEG, SHELL_WRAP_DEG


def swing_arc() -> tuple[float, float]:
    return SWING_CENTRE_DEG, SHELL_WRAP_DEG


def gap_deg() -> float:
    """Angular gap at each parting line, before the mechanism is added."""
    return (360.0 - 2.0 * SHELL_WRAP_DEG) / 2.0
