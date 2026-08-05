"""
BAYONET INTERFACE — one definition, consumed by both halves.

The male spigot lives on the cradle, the female collar lives on the dock. They
are separate parts printed separately, so the only way they reliably fit is if
neither owns the interface: both derive it from here. Editing a lug angle here
moves the slot in the collar and the lug on the spigot in the same commit.

The mechanism, per the brief: the cradle drops in axially, then rotates 15 deg to
lock against a sprung detent you can feel. Two motions, nothing droppable, and
the lock is positive rather than frictional.

Load path through the joint: the suspended load arrives as an overturning moment,
which the lugs take in SHEAR against the slot's lower ramp face. That is why the
lug count is 3 and not 2 — three points define the seating plane, so the cradle
cannot rock on a diagonal, and the moment is shared rather than couple-loaded
through one pair.
"""

from __future__ import annotations

from math import pi

from . import clearances as C

# --- Spigot -----------------------------------------------------------------
# Sized so the spigot wall carries the boom moment in bending well inside the
# PETG allowable. Diameter buys section modulus far more cheaply than wall does,
# so this runs large and thin rather than small and thick.
SPIGOT_D = 38.0
SPIGOT_WALL = 4.0
SPIGOT_ENGAGE_H = 22.0          # axial length inside the collar

# --- Lugs -------------------------------------------------------------------
LUG_COUNT = 3
LUG_ARC_DEG = 34.0
LUG_RADIAL = 4.0                # radial projection past the spigot OD
LUG_AXIAL_H = 5.0               # thickness in the load direction
LUG_Z = 14.0                    # height of the lug's underside up the spigot

# How far below the collar's top face the lug's underside sits when locked.
# This is the joint's real datum: the collar's groove is cut from it, and the
# spigot only has to be able to reach it.
LOCK_DEPTH = 12.0

# --- Twist ------------------------------------------------------------------
TWIST_DEG = 15.0                # the brief's number, and the whole feel of it
DETENT_D = 4.0                  # sprung ball
DETENT_POCKET_DEPTH = 3.2

# --- Collar -----------------------------------------------------------------
COLLAR_WALL = 6.0
COLLAR_H = 26.0


def collar_bore_d() -> float:
    """Bore the spigot drops into, with its named clearance."""
    return SPIGOT_D + 2.0 * C.BAYONET_SPIGOT_TO_BORE


def collar_od() -> float:
    return collar_bore_d() + 2.0 * LUG_RADIAL + 2.0 * COLLAR_WALL


def slot_arc_deg() -> float:
    """Angular width of the axial entry slot.

    Wider than the lug by the radial clearance expressed as an angle, so the
    clearance the coupon verifies is the same variable the collar is cut with.
    """
    r = (SPIGOT_D / 2.0) + LUG_RADIAL / 2.0
    ang_clear = (C.BAYONET_LUG_RADIAL / r) * (180.0 / pi)
    return LUG_ARC_DEG + 2.0 * ang_clear


def lug_angles() -> list[float]:
    return [i * 360.0 / LUG_COUNT for i in range(LUG_COUNT)]


def groove_bottom_z() -> float:
    """Z of the groove floor — the face the lug bears down on under load."""
    return COLLAR_H - LOCK_DEPTH


def groove_height() -> float:
    """Axial height of the circumferential groove, lug plus its clearance."""
    return LUG_AXIAL_H + C.BAYONET_LUG_AXIAL


def travel_arc_deg() -> float:
    """Circumferential slot sweep: the twist plus the overtravel that lets the
    detent seat against a hard stop rather than against the lug itself."""
    return TWIST_DEG + C.BAYONET_ANGULAR_OVERTRAVEL


def lug_shear_area_mm2() -> float:
    """Total lug bearing area resisting the moment, for the failure critic."""
    r_mid = SPIGOT_D / 2.0 + LUG_RADIAL / 2.0
    arc_len = 2.0 * pi * r_mid * (LUG_ARC_DEG / 360.0)
    return LUG_COUNT * arc_len * LUG_RADIAL
