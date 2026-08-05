"""
OVER-CENTRE LEVER GEOMETRY — the mechanism that generates the 343 N preload.

How over-centre works, and why the numbers below are what they are:

The lever pivots on the fixed shell. A short crank on the lever carries one end
of a link; the link's other end hooks the catch pin on the swing shell. As the
lever closes, the crank pin swings THROUGH the straight line between pivot and
catch, and just past it. At that crossing the link is at maximum stretch — that
is where peak preload happens. Past it, the geometry slackens very slightly and
the link tension pulls the lever HARD against its closed stop.

That last few degrees is the whole trick: the load itself holds the lever shut.
Nothing threaded, nothing to back off, and vibration cannot walk it open because
opening requires first increasing tension.

  CRANK_R        distance pivot -> crank pin. Sets the mechanical advantage.
  OVER_TRAVEL    how far past dead-centre the crank goes. Too little and the
                 lever creeps open; too much and it takes two hands to close.

Mechanical advantage at the crossing is roughly ARM_LEN / CRANK_R, so a 58 mm arm
on a 13 mm crank gives about 4.5x. A hand comfortably applies 60 N, so this yields
~270 N of link tension against the 172 N required. That margin is deliberately
slim: a lever that can generate far more than needed is a lever that can crush
the liner and mar the pole.
"""

from __future__ import annotations

from math import hypot

from . import clamp as L

# --- Lever blade -------------------------------------------------------------
CRANK_R = 13.0
# Must exceed L.LEVER_BOSS_R + LINK_END_R or the link's end boss overlaps the
# lever's pivot boss — 9 mm did, for 9 mm^3 of interference against the shell.
ARM_LEN = 58.0
OVER_TRAVEL_DEG = 7.0

BLADE_W = 19.0                  # sits inside L.LEVER_EAR_GAP
PIVOT_BOSS_R = 7.0
TIP_R = 7.5
BLADE_WAIST = 12.0              # narrowest part of the arm
# Waist is 12 not 9: at 9 mm the closing stress is 13.6 MPa against a 22.5 MPa
# transient allowable, which is only 1.7x. The lever is a TRANSIENT member — it
# is loaded while you close it and unloaded once over centre, resting on its
# stop — so short-term yield governs it, not creep. 12 mm brings it to 7.6 MPa.

# Slot down the blade centre so the link runs INSIDE the lever rather than
# beside it. Keeps the mechanism symmetric, so the pivot pin sees no couple.
LINK_SLOT_W = 4.0               # steel link is 3 mm thick
LINK_SLOT_DEPTH = 26.0

# --- Link --------------------------------------------------------------------
# The link is STEEL, not printed. At 172 N of SUSTAINED tension a PETG link
# reaches only 1.5x over the 5x-derated in-plane allowable even at 8 x 10 mm, and
# its pin bearing (4.6 MPa on M5) exceeds the sustained tensile allowable
# outright. 3 mm mild steel gives 21x at 7.5 g. It is also the part the brief
# wants reading as hardware rather than as a printed strap.
LINK_T = 3.0                    # steel plate thickness
LINK_W = 8.0                    # strap width, in the plane of rotation
LINK_END_R = 6.5
LINK_PIN_D = 5.0

# --- Hand feel ---------------------------------------------------------------
# Chamfers where a hand goes, fillets where load goes. Rubric item 6.
HAND_CHAMFER = 1.2
LOAD_FILLET = 2.0
GRIP_SCALLOP_R = 22.0           # concave thumb relief on the arm's outer edge


def pivot_to_catch() -> float:
    """Straight-line distance from lever pivot to catch pin, clamp closed.

    Chord between the pivot angle and the catch angle at the pivot radius. Both
    angles are offset to opposite sides of the parting gap — see clamp.py — so
    this is a real base length rather than the degenerate zero it would be if
    both sat on the parting line itself.
    """
    from math import radians, sin

    from . import derived as D
    d = D.compute()
    r_axis = d.shell_bore_d / 2.0 + d.shell_wall_t + L.lever_standoff()
    half = radians(abs(L.LEVER_PIVOT_DEG - L.CATCH_DEG) / 2.0)
    return 2.0 * r_axis * sin(half)


def link_length() -> float:
    """Pin-centre to pin-centre, set so the crank crosses dead centre.

    At dead centre the crank pin lies on the pivot-catch line, so
    link = pivot_to_catch - CRANK_R. The link is then made very slightly SHORTER
    than that, by the over-travel chord, which is what puts the mechanism past
    centre and locks it.
    """
    from math import radians, sin
    dead_centre = pivot_to_catch() - CRANK_R
    over = 2.0 * CRANK_R * sin(radians(OVER_TRAVEL_DEG) / 2.0)
    length = dead_centre - over
    if length <= 2.0 * LINK_END_R:
        raise ValueError(
            f"link_length() = {length:.2f} mm is not buildable: it must exceed "
            f"2 x LINK_END_R ({2*LINK_END_R:.1f} mm) or the two pin bosses "
            f"overlap. pivot_to_catch is {pivot_to_catch():.2f} mm — widen the "
            f"pivot/catch angular offset in params/clamp.py."
        )
    return length


def mechanical_advantage() -> float:
    return ARM_LEN / CRANK_R


def hand_force_for_preload(preload_n: float) -> float:
    """Hand force at the lever tip needed to reach a given link tension."""
    return preload_n / mechanical_advantage()


def link_tension_capacity(hand_n: float = 60.0) -> float:
    return hand_n * mechanical_advantage()


def blade_length() -> float:
    return ARM_LEN + PIVOT_BOSS_R + TIP_R
