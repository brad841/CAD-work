"""
GATE 0 — MEASURED INPUTS.

This is the ONLY file you edit when the physical situation changes.
Every dimension in every part generator derives from these values.

Units: millimetres, grams, degrees. No inches anywhere below the
protocol doc — convert once, here, and write the converted number.

Each UNMEASURED() below is a live tripwire, not a placeholder comment.
It raises on any arithmetic, so no part generator can produce geometry
from a guessed number. Replace the call with a float to clear it.

Measurement procedure for every field: docs/GATE0_MEASUREMENT_PROTOCOL.md
"""

from __future__ import annotations


class Unmeasured:
    """A number that refuses to be a number.

    Exists so that a missing Gate 0 measurement fails loudly at geometry
    time instead of silently defaulting to something plausible. Any attempt
    to compute with it raises; any attempt to compare or cast raises.
    """

    __slots__ = ("field", "note")

    def __init__(self, field: str, note: str = "") -> None:
        self.field = field
        self.note = note

    def _explode(self, *_args, **_kwargs):
        raise UnmeasuredParameterError(self.field, self.note)

    # Arithmetic, comparison, casting — all closed off.
    __add__ = __radd__ = __sub__ = __rsub__ = _explode
    __mul__ = __rmul__ = __truediv__ = __rtruediv__ = _explode
    __floordiv__ = __rfloordiv__ = __mod__ = __rmod__ = _explode
    __pow__ = __rpow__ = __neg__ = __pos__ = __abs__ = _explode
    __lt__ = __le__ = __gt__ = __ge__ = _explode
    __float__ = __int__ = __index__ = __round__ = _explode
    __bool__ = _explode

    def __repr__(self) -> str:  # safe: used by the validator's report
        return f"<UNMEASURED {self.field}>"


class UnmeasuredParameterError(RuntimeError):
    def __init__(self, field: str, note: str = "") -> None:
        msg = (
            f"GATE 0 BLOCK: '{field}' has not been measured.\n"
            f"  Geometry generation is refused until it is a real number.\n"
            f"  Measure it: docs/GATE0_MEASUREMENT_PROTOCOL.md\n"
            f"  Then edit exactly one line: params/gate0.py"
        )
        if note:
            msg += f"\n  What this field is: {note}"
        super().__init__(msg)


def UNMEASURED(field: str, note: str = "") -> Unmeasured:
    return Unmeasured(field, note)


# ---------------------------------------------------------------------------
# 1. POLE — the rented tent pole. Do not mar it.
# ---------------------------------------------------------------------------
# Six diameters: 3 heights x 2 axes, so ovality and coating buildup are
# captured rather than averaged away. Heights are measured from the intended
# clamp band centre: LO = 100 mm below, MID = at the band, HI = 100 mm above.
# Axis A is across the weld seam; axis B is 90 deg to it.

POLE_OD_LO_A = UNMEASURED("POLE_OD_LO_A", "pole OD 100 mm below clamp band, across weld seam")
POLE_OD_LO_B = UNMEASURED("POLE_OD_LO_B", "pole OD 100 mm below clamp band, 90 deg to seam")
POLE_OD_MID_A = UNMEASURED("POLE_OD_MID_A", "pole OD at clamp band centre, across weld seam")
POLE_OD_MID_B = UNMEASURED("POLE_OD_MID_B", "pole OD at clamp band centre, 90 deg to seam")
POLE_OD_HI_A = UNMEASURED("POLE_OD_HI_A", "pole OD 100 mm above clamp band, across weld seam")
POLE_OD_HI_B = UNMEASURED("POLE_OD_HI_B", "pole OD 100 mm above clamp band, 90 deg to seam")

# Weld seam proud height above the local surface, 0.0 if flush/absent.
# The TPU liner gets a relief groove for this; without the number the liner
# either bridges the seam (point-loads the coating) or over-reliefs (loses grip).
POLE_SEAM_PROUD = UNMEASURED("POLE_SEAM_PROUD", "how far the weld seam stands proud of the tube surface")

POLE_WALL_T = UNMEASURED("POLE_WALL_T", "pole wall thickness — governs allowable clamp pressure before denting")
POLE_MATERIAL = UNMEASURED(
    "POLE_MATERIAL",
    "one of: 'steel-powdercoat', 'steel-galv', 'aluminium-anodised', 'aluminium-bare'",
)

# ---------------------------------------------------------------------------
# 2. SONOS MOVE 2 — rear handle recess. The anti-tip hook engages this only.
# ---------------------------------------------------------------------------
# Loaded in shear, so its true depth and lip radius set the hook's engagement
# and its root fillet. Guessing these is how the hook either misses or
# scars the moulding.

HANDLE_RECESS_W = UNMEASURED("HANDLE_RECESS_W", "clear width of rear handle recess, widest point")
HANDLE_RECESS_D = UNMEASURED("HANDLE_RECESS_D", "how deep the recess cuts into the rear face")
HANDLE_LIP_R = UNMEASURED("HANDLE_LIP_R", "radius of the moulded lip the hook bears against")
HANDLE_LIP_H_ABOVE_BASE = UNMEASURED(
    "HANDLE_LIP_H_ABOVE_BASE",
    "height of the load-bearing underside of the lip above the speaker's base plane",
)

# ---------------------------------------------------------------------------
# 3. FACTORY CHARGING BASE — Module A carries it unmodified.
# ---------------------------------------------------------------------------
# It is rated indoor only, so the drip canopy is dimensioned from these.

BASE_FOOTPRINT_X = UNMEASURED("BASE_FOOTPRINT_X", "charging base outer footprint, left-right")
BASE_FOOTPRINT_Y = UNMEASURED("BASE_FOOTPRINT_Y", "charging base outer footprint, front-back")
BASE_HEIGHT = UNMEASURED("BASE_HEIGHT", "charging base overall height, tray face to contact face")
BASE_PAD_OFFSET_X = UNMEASURED("BASE_PAD_OFFSET_X", "contact pad centre offset from base footprint centre, X")
BASE_PAD_OFFSET_Y = UNMEASURED("BASE_PAD_OFFSET_Y", "contact pad centre offset from base footprint centre, Y")
BASE_CABLE_EXIT = UNMEASURED(
    "BASE_CABLE_EXIT",
    "one of: 'aft', 'port', 'starboard', 'under' — sets which way the drip loop runs",
)

# ---------------------------------------------------------------------------
# 4. CENTRE OF MASS — with the base installed. Sets the boom moment.
# ---------------------------------------------------------------------------
# The single most consequential number here: it multiplies against the boom
# length to size the clamp's resisting couple. String-hang it in two
# orientations, photograph, intersect. Offsets are from the speaker's base
# plane centre, +Y aft (toward the pole), +Z up.

COM_OFFSET_Y = UNMEASURED("COM_OFFSET_Y", "CoM horizontal offset from base centre, +aft toward pole")
COM_OFFSET_Z = UNMEASURED("COM_OFFSET_Z", "CoM height above the speaker's base plane")

# ---------------------------------------------------------------------------
# VERIFIED — from published specs, not measurement. Safe to trust.
# ---------------------------------------------------------------------------
SPEAKER_W = 160.0          # mm, across
SPEAKER_D = 127.0          # mm, front-back
SPEAKER_H = 241.0          # mm, tall
SPEAKER_MASS = 3000.0      # g
BASE_MASS = 150.0          # g
SUSPENDED_MASS = SPEAKER_MASS + BASE_MASS   # 3150 g — the load everything sizes against

MOUNT_HEIGHT_AGL = 2100.0  # mm, speaker underside above ground

PITCH_LIMIT_DOWN = 20.0    # deg, Sonos-permitted
PITCH_LIMIT_UP = 5.0       # deg, Sonos-permitted
# Sonos prohibits inverted use. No pitch index position may exceed the pair
# above; the index plate is generated from them, not from taste.

PRINTED_MASS_BUDGET = 400.0  # g, all printed parts combined

# ---------------------------------------------------------------------------
# GATE ENFORCEMENT
# ---------------------------------------------------------------------------
_GATE0_FIELDS = [
    "POLE_OD_LO_A", "POLE_OD_LO_B", "POLE_OD_MID_A", "POLE_OD_MID_B",
    "POLE_OD_HI_A", "POLE_OD_HI_B", "POLE_SEAM_PROUD",
    "POLE_WALL_T", "POLE_MATERIAL",
    "HANDLE_RECESS_W", "HANDLE_RECESS_D", "HANDLE_LIP_R", "HANDLE_LIP_H_ABOVE_BASE",
    "BASE_FOOTPRINT_X", "BASE_FOOTPRINT_Y", "BASE_HEIGHT",
    "BASE_PAD_OFFSET_X", "BASE_PAD_OFFSET_Y", "BASE_CABLE_EXIT",
    "COM_OFFSET_Y", "COM_OFFSET_Z",
]


def missing() -> list[str]:
    """Return the Gate 0 fields still unmeasured."""
    g = globals()
    return [f for f in _GATE0_FIELDS if isinstance(g.get(f), Unmeasured)]


def require_gate0() -> None:
    """Call at the top of every part generator. Refuses to proceed if blocked."""
    m = missing()
    if m:
        raise UnmeasuredParameterError(
            m[0], f"{len(m)} of {len(_GATE0_FIELDS)} Gate 0 fields unmeasured: {', '.join(m)}"
        )
