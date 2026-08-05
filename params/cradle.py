"""
CRADLE GEOMETRY — boom, tray, hook, pitch index.

Gravity does the work. The speaker sits UPRIGHT ON the tray and compresses into
the charging contacts under its own weight. The body is never clamped. The only
other contact is the rear-handle hook, which engages the moulded recess in SHEAR
and exists purely to stop the speaker walking forward off the tray when pitched
nose-down.

Datum: tray top face is z = 0 in cradle coordinates, speaker centre at x = 0,
+y aft toward the pole. The bayonet spigot axis is vertical and sits aft of the
tray, so the boom reaches forward and the speaker hangs over nothing.

The pitch index is a plate of discrete holes rather than a friction joint. A
friction pitch joint creeps — over an overnight in a hot tent it would sag, and
the Sonos limit would be silently exceeded. Discrete holes cannot creep past a
position that does not exist, which is how the -20/+5 limit is made structural
instead of advisory.
"""

from __future__ import annotations

from . import derived as D
from . import gate0 as G

# --- Tray --------------------------------------------------------------------
# Footprint follows the speaker with its named locating clearance, not a guess.
TRAY_T = 5.0
# The floor is a RIB GRID, not a plate. A solid 6 mm floor over the speaker's
# footprint is 170 g on its own — 42% of the entire printed budget for a surface
# the speaker only touches at four pads. Ribs under the pad positions carry the
# same load and drain better.
RIB_W = 5.0
WINDOW_COLS = 4
WINDOW_ROWS = 3
TRAY_LIP_H = 9.0                # front and side retention lip height
TRAY_LIP_T = 3.4
# Aft edge is open so the charging base's cable can leave downward and so the
# speaker can be slid in from behind against the hook.
PAD_RECESS_D = 22.0             # anti-slip pad recesses
PAD_RECESS_DEPTH = 1.2
PAD_COUNT = 4

# Lightening cutouts in the tray floor. Also the drain path — a solid tray would
# hold a puddle under an IP56 speaker, and standing water is what finds its way
# into a charging base that Sonos rates indoor only.
DRAIN_SLOT_W = 9.0
DRAIN_SLOT_L = 46.0
DRAIN_COUNT = 3

# --- Boom --------------------------------------------------------------------
BOOM_W_ROOT = 44.0              # at the spigot, where the moment is highest
BOOM_W_TIP = 30.0               # at the tray, where it is lowest
BOOM_H_ROOT = 26.0
BOOM_H_TIP = 16.0
BOOM_FILLET = 3.0

# --- Pitch index -------------------------------------------------------------
PITCH_PIN_D = 5.0
PITCH_PLATE_T = 5.0
PITCH_PLATE_R = 30.0            # index radius; longer arm = finer angular feel
PITCH_HINGE_PIN_D = 6.0
# How far below the tray's top face the hinge bore sits. The boom fork's bore is
# placed to match, so the two cannot drift: an earlier version had the tray's bore
# 22 mm from the fork's and the lug 57 mm from the fork entirely.
LUG_HINGE_DROP = 22.0

# --- Rear handle hook --------------------------------------------------------
# The hook is one part: a slotted upright plus the shear nose. Its height is set
# by the installer, because the recess height above the speaker base is one of
# the unpublished numbers. See gate0.HOOK_HEIGHT_ADJUST_*.
HOOK_POST_W = 26.0
HOOK_POST_T = 7.0
HOOK_SLOT_W = 5.4               # M5 clamping bolt rides in this
HOOK_NOSE_REACH = 16.0          # how far forward the nose projects into the recess
HOOK_NOSE_H = 10.0
HOOK_NOSE_T = 5.0

# --- USB-C retainer (Module B) ----------------------------------------------
# Right-angle plug. Dimensions are the connector shell, which is standardised —
# unlike the charging base, this needs no measurement.
USBC_SHELL_W = 9.0
USBC_SHELL_T = 3.4
USBC_BODY_W = 14.0
USBC_BODY_H = 22.0
USBC_BODY_T = 9.0
# Strain relief breaks the water track BEFORE the plug: the cable is forced into
# a downward loop so surface water runs off the low point instead of following
# the jacket into the connector.
DRIP_LOOP_R = 11.0
RELIEF_THROAT_W = 6.0


def tray_w() -> float:
    from . import clearances as C
    return G.SPEAKER_W + 2.0 * C.TRAY_TO_SPEAKER_FOOTPRINT + 2.0 * TRAY_LIP_T


def tray_d() -> float:
    from . import clearances as C
    return G.SPEAKER_D + 2.0 * C.TRAY_TO_SPEAKER_FOOTPRINT + TRAY_LIP_T


def boom_reach() -> float:
    """Horizontal distance from the bayonet axis to the tray centre.

    Derived from the boom length the load path already computed, less the
    speaker's half-depth that boom_length included. Keeping it derived means a
    changed pole range moves the boom without anyone editing the cradle.
    """
    d = D.compute()
    return d.boom_length - G.SPEAKER_D / 2.0


def hook_post_h() -> float:
    """Tall enough to reach the top of the adjustment range, plus slot margin."""
    return G.HOOK_HEIGHT_ADJUST_MAX + 18.0
