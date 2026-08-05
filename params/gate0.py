"""
GATE 0 — DESIGN ENVELOPE.

Revised after the pole turned out to be unconfirmable and the Move 2's
undocumented dimensions turned out to be genuinely unpublished. The gate is no
longer "measure 21 things or stop." It now distinguishes three kinds of number,
and only one of them blocks:

  MEASURED(x)   A real number someone put a caliper on. Trusted.

  BOUNDED(x)    Not measured. A deliberately conservative substitute, chosen so
                that being wrong makes the mount STRONGER or FITS LOOSER, never
                the reverse. Arithmetic is allowed, because a safe bound is a
                legitimate engineering input — but every one is tracked and the
                validator prints it, so no bound ever quietly becomes a fact.

  UNMEASURED(x) Blocks. Reserved for numbers where no conservative direction
                exists, so guessing cannot be made safe.

The conservative direction is recorded per bound in the `worse_if` field. That
field is the whole argument for why the bound is legitimate: it names what would
happen if reality differs, and every one resolves toward safe.

Units: millimetres, grams, degrees.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Value kinds
# ---------------------------------------------------------------------------
class UnmeasuredParameterError(RuntimeError):
    def __init__(self, name: str, note: str = "") -> None:
        msg = (
            f"GATE BLOCK: '{name}' has no value and no safe bound.\n"
            f"  Geometry generation is refused.\n"
            f"  Measure it: docs/GATE0_MEASUREMENT_PROTOCOL.md"
        )
        if note:
            msg += f"\n  What it is: {note}"
        super().__init__(msg)


class Unmeasured:
    """A number that refuses to be a number. Blocks geometry on contact."""

    __slots__ = ("name", "note")

    def __init__(self, name: str, note: str = "") -> None:
        self.name = name
        self.note = note

    def _explode(self, *_a, **_k):
        raise UnmeasuredParameterError(self.name, self.note)

    __add__ = __radd__ = __sub__ = __rsub__ = _explode
    __mul__ = __rmul__ = __truediv__ = __rtruediv__ = _explode
    __floordiv__ = __rfloordiv__ = __mod__ = __rmod__ = _explode
    __pow__ = __rpow__ = __neg__ = __pos__ = __abs__ = _explode
    __lt__ = __le__ = __gt__ = __ge__ = _explode
    __float__ = __int__ = __index__ = __round__ = _explode
    __bool__ = _explode

    def __repr__(self) -> str:
        return f"<UNMEASURED {self.name}>"


@dataclass(frozen=True)
class Bound:
    """A conservative stand-in for a measurement, with its safety argument."""

    name: str
    value: float
    worse_if: str          # what reality differing would cost — must resolve safe
    replaces: str = ""     # the measurement this stands in for
    cost: str = ""         # what the conservatism costs us, honestly stated


# Registry of every bound in use, so the validator can print the full list.
BOUNDS: dict[str, Bound] = {}
MEASURED_FIELDS: list[str] = []


def UNMEASURED(name: str, note: str = "") -> Unmeasured:
    return Unmeasured(name, note)


def MEASURED(name: str, value: float) -> float:
    MEASURED_FIELDS.append(name)
    return value


def BOUNDED(name: str, value: float, worse_if: str, replaces: str = "",
            cost: str = "") -> float:
    """Register a conservative bound and return its numeric value."""
    BOUNDS[name] = Bound(name, value, worse_if, replaces, cost)
    return value


# ===========================================================================
# 1. POLE — unconfirmable. Designed as a RANGE, taken up by shims.
# ===========================================================================
# The pole is rented and cannot be measured before the build. A 2.5 in nominal
# tent pole runs 2.44-2.56 in in practice, so the clamp is designed to close on
# the LARGEST end of that range and shim down to the smallest. Shimming is the
# right mechanism here: a shim only ever adds material between shell and pole,
# so a wrong guess about the pole makes the stack thicker, never looser.
#
# There is no single "pole OD" variable any more, on purpose. Changing the
# design range means editing these two numbers and nothing else.
POLE_OD_DESIGN_MIN = 62.0   # 2.44 in
POLE_OD_DESIGN_MAX = 65.0   # 2.56 in

# Shim system. Printed plates that bring a small pole up to the shell bore.
SHIM_THICKNESSES = (0.5, 1.0, 1.5)   # mm radial, stackable to 3.0 mm
SHIM_STACK_MAX = 3.0                  # covers the full design range, both ends

POLE_SEAM_PROUD = BOUNDED(
    "POLE_SEAM_PROUD", 0.8,
    worse_if="If the real seam is smaller or flush, the liner's relief groove is "
             "merely deeper than needed and grip is carried by the rest of the "
             "circumference. If we guessed small and the seam were large, the "
             "liner would bridge and point-load the pole coating.",
    replaces="measured weld seam proud height",
    cost="Slightly less liner contact area, so clamp pressure rises a few percent.",
)

POLE_WALL_T = BOUNDED(
    "POLE_WALL_T", 1.2,
    worse_if="Assuming a THIN wall caps the allowable clamp pressure low, which "
             "is what protects the rented pole from denting. A thicker real wall "
             "just means we were gentler than we had to be.",
    replaces="measured pole wall thickness (explicitly waived as non-structural)",
    cost="A taller clamp band than strictly needed, to spread the same couple "
         "over more area. Costs mass and height, buys pole safety.",
)

POLE_MATERIAL = BOUNDED(
    "POLE_MATERIAL", 0.0,   # categorical; numeric slot unused
    worse_if="Treated as the most delicate plausible finish (powder coat over "
             "thin steel). The TPU liner and the pressure cap are sized for the "
             "finish that scratches easiest.",
    replaces="pole material and finish",
    cost="None structurally. Liner is TPU regardless.",
)
POLE_FINISH_ASSUMED = "steel-powdercoat"

# ===========================================================================
# 2. MOVE 2 REAR HANDLE — unpublished. Designed COMPLIANT AND ADJUSTABLE.
# ===========================================================================
# Searched: Sonos product and support pages, the Move 2 user guide, retailer
# spec tables, GrabCAD, STLFinder, Printables, MakerWorld, Thingiverse,
# Creality Cloud, FCC (model RM044), iFixit, and a dozen reviews. The recess
# geometry is nowhere. Reviews establish only that it is a tapered recess with
# a hollow top and room for four fingers, and that the Move 1 equivalent is
# about 60 mm deep.
#
# So the hook stops depending on the recess. It is narrower than any plausible
# four-finger recess, its nose is TPU so it conforms to whatever lip radius is
# actually there, and its height is set by the installer on a slotted M5
# adjustment rather than by a modelled number. Engagement becomes something you
# feel and lock, not something we predict.

HANDLE_RECESS_W_MIN = BOUNDED(
    "HANDLE_RECESS_W_MIN", 60.0,
    worse_if="A four-finger recess cannot be narrower than ~70 mm; assuming 60 mm "
             "sizes the hook to fit something narrower than the recess can be. A "
             "wider real recess only leaves margin either side of the hook.",
    replaces="measured recess clear width",
    cost="Hook is narrower than it could be, so bearing stress on the lip is "
         "higher than optimal. Sized for it — see HOOK_WIDTH.",
)

HANDLE_RECESS_D_MIN = BOUNDED(
    "HANDLE_RECESS_D_MIN", 8.0,
    worse_if="Assuming a SHALLOW recess means the hook is designed to work with "
             "minimal engagement depth. A deeper real recess gives more "
             "engagement than we counted on, never less.",
    replaces="measured recess depth",
    cost="Hook must reach further and the anti-tip path is shorter, so the "
         "tether's role as independent backup matters more.",
)

HANDLE_LIP_R_MAX = BOUNDED(
    "HANDLE_LIP_R_MAX", 6.0,
    worse_if="Assuming a LARGE lip radius means assuming the worst shear shoulder "
             "— the most rounded, least positive surface to bear against. A "
             "crisper real lip engages better than designed.",
    replaces="measured lip radius",
    cost="The TPU nose does the conforming, which is why this bound is cheap.",
)

# Not a bound — a designed adjustment range. The hook slides and locks.
HOOK_HEIGHT_ADJUST_MIN = 140.0
HOOK_HEIGHT_ADJUST_MAX = 205.0
HOOK_WIDTH = 36.0            # comfortably inside HANDLE_RECESS_W_MIN
HOOK_NOSE_MATERIAL = "TPU 95A"

# ===========================================================================
# 3. CENTRE OF MASS — unpublished. BOUNDED to the adverse corner.
# ===========================================================================
# No teardown, no CAD, no published figure. But CoM is one of the few
# quantities where a bound is genuinely as good as a measurement, because it is
# physically confined: the CoM of a rigid body lies inside its own envelope.
# So we place it at the corner of that envelope that produces the LARGEST
# overturning moment and the LARGEST tip moment, and design to that.
#
# Reality will be kinder than this in every case. That is the definition of a
# safe bound, and it is why this is not a guess.

COM_OFFSET_Y = BOUNDED(
    "COM_OFFSET_Y", -20.0,
    worse_if="Negative is FORWARD, away from the pole — the long-lever direction. "
             "Reality puts the CoM nearer the centre, which shortens the lever "
             "and lowers every stress downstream.",
    replaces="string-hang CoM measurement, horizontal",
    cost="Boom, clamp band and shells all sized for a moment ~20-30% above the "
         "likely truth. Mass, not risk.",
)

COM_OFFSET_Z = BOUNDED(
    "COM_OFFSET_Z", 135.0,
    worse_if="Above the 95-125 mm expected for a speaker with driver and battery "
             "low down. A HIGH assumed CoM maximises the tip moment at pitch, so "
             "the anti-tip hook and pitch index are sized for worse than real.",
    replaces="string-hang CoM measurement, vertical",
    cost="Anti-tip path over-built. Acceptable — it is priority 1.",
)

# ===========================================================================
# 4. CHARGING BASE — unpublished. Gated SEPARATELY, blocks Module A only.
# ===========================================================================
# These have no conservative direction. A canopy that does not match the real
# base footprint does not fail safe: it drips on 15 V electronics that Sonos
# rates indoor only. So these stay UNMEASURED and they block Module A.
#
# They do not block anything else. Module B — the right-angle USB-C plug
# retainer — needs none of them, which is exactly why the brief says build B
# first. The core mount proceeds now; Module A waits for a caliper.

BASE_FOOTPRINT_X = UNMEASURED("BASE_FOOTPRINT_X", "charging base footprint, left-right")
BASE_FOOTPRINT_Y = UNMEASURED("BASE_FOOTPRINT_Y", "charging base footprint, front-back")
BASE_HEIGHT = UNMEASURED("BASE_HEIGHT", "base height, tray face to contact face")
BASE_PAD_OFFSET_X = UNMEASURED("BASE_PAD_OFFSET_X", "contact pad offset from footprint centre, X")
BASE_PAD_OFFSET_Y = UNMEASURED("BASE_PAD_OFFSET_Y", "contact pad offset from footprint centre, Y")
BASE_CABLE_EXIT = UNMEASURED("BASE_CABLE_EXIT", "'aft' | 'port' | 'starboard' | 'under'")

_MODULE_A_FIELDS = [
    "BASE_FOOTPRINT_X", "BASE_FOOTPRINT_Y", "BASE_HEIGHT",
    "BASE_PAD_OFFSET_X", "BASE_PAD_OFFSET_Y", "BASE_CABLE_EXIT",
]

# ===========================================================================
# VERIFIED — published specs. Not measurements, not bounds.
# ===========================================================================
SPEAKER_W = MEASURED("SPEAKER_W", 160.0)
SPEAKER_D = MEASURED("SPEAKER_D", 127.0)
SPEAKER_H = MEASURED("SPEAKER_H", 241.0)
SPEAKER_MASS = MEASURED("SPEAKER_MASS", 3000.0)
BASE_MASS = MEASURED("BASE_MASS", 150.0)
SUSPENDED_MASS = SPEAKER_MASS + BASE_MASS      # 3150 g

MOUNT_HEIGHT_AGL = 2100.0
PITCH_LIMIT_DOWN = 20.0
PITCH_LIMIT_UP = 5.0
PRINTED_MASS_BUDGET = 400.0

# Confirmed against Sonos support during the spec sweep: the base is rated
# INDOOR ONLY. This is why the Module A canopy is a primary requirement.
BASE_INDOOR_ONLY = True


# ---------------------------------------------------------------------------
# Gate enforcement, by scope
# ---------------------------------------------------------------------------
def missing(scope: str = "core") -> list[str]:
    """Fields still blocking. scope 'core' | 'module_a' | 'all'."""
    g = globals()
    fields = {
        "core": [],
        "module_a": _MODULE_A_FIELDS,
        "all": _MODULE_A_FIELDS,
    }[scope]
    return [f for f in fields if isinstance(g.get(f), Unmeasured)]


def require(scope: str = "core") -> None:
    m = missing(scope)
    if m:
        raise UnmeasuredParameterError(
            m[0], f"{len(m)} field(s) block scope '{scope}': {', '.join(m)}"
        )


def bounds_in_use() -> list[Bound]:
    return sorted(BOUNDS.values(), key=lambda b: b.name)
