"""
POLE GAUGE COUPON — the first thing to print, and the cheapest.

The pole cannot be measured before the build, so this part measures it for you at
install time. It is a 180 deg half-shell whose bore steps in 0.5 mm increments
across the design range plus a margin either side. Slide it down the pole; it
stops at the first step smaller than the pole. The last step that cleared is the
pole's OD, and that reading picks the shim stack.

Reading it without text: the outer face is scribed like a ruler. Every step
boundary gets a groove around the arc, and every fifth is cut wider and deeper.
Count grooves up from the bottom (largest bore) to find which step you are on.
Text on a curved FDM surface at this size is unreliable, and a miscounted gauge
is worse than no gauge, so the scale is geometric and unambiguous.

This coupon also discharges half the physical gate: it is a direct check on
SHELL_BORE_TO_POLE_OPEN and on how the printer's real dimensional accuracy lands
against the nominal bore. If every step is tight by the same amount, that is the
printer, and the fix is a scale correction rather than a design change.

Print: axis normal to the plate, no supports. Same orientation as the clamp
shells, on purpose — this coupon is only honest if it is printed the way the
shells will be.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Axis, Box, Cylinder, Part, Plane, Pos  # noqa: E402

from params import gate0 as G  # noqa: E402
from parts import _base  # noqa: E402

NAME = "pole_gauge_coupon"
MATERIAL = "PETG"

# Bore steps span the design range with 1.5 mm of margin either side, so the
# gauge still reads a pole that falls outside what we planned for.
STEP_INCREMENT = 0.5
MARGIN = 1.5
STEP_HEIGHT = 6.0
# The gauge carries no load — it only has to hold its bore while pressed onto a
# pole by hand. 3 mm is plenty and keeps it cheap enough that reprinting it after
# a scale correction is not a decision.
WALL = 3.0
SWEEP_DEG = 180.0

# Ruler scribed around the outer arc: one groove per step boundary, every fifth
# wider and deeper so the eye can count in fives.
TICK_W = 0.8
TICK_DEPTH = 0.8
WITNESS_EVERY = 5
WITNESS_W = 1.6
WITNESS_DEPTH = 1.4


def step_diameters() -> list[float]:
    """Bore steps, smallest first. Derived from the design range, not typed."""
    lo = G.POLE_OD_DESIGN_MIN - MARGIN
    hi = G.POLE_OD_DESIGN_MAX + MARGIN
    n = int(round((hi - lo) / STEP_INCREMENT)) + 1
    return [lo + i * STEP_INCREMENT for i in range(n)]


def build() -> Part:
    dias = step_diameters()
    outer_d = max(dias) + 2.0 * WALL
    total_h = len(dias) * STEP_HEIGHT

    # Stack of coaxial annuli, smallest bore at the top so the gauge is pushed
    # down onto the pole and stops where it stops.
    solid = None
    for i, d in enumerate(reversed(dias)):
        z0 = i * STEP_HEIGHT
        ring = Cylinder(
            radius=outer_d / 2.0, height=STEP_HEIGHT,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        ) - Cylinder(
            radius=d / 2.0, height=STEP_HEIGHT,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        ring = Pos(0, 0, z0) * ring
        solid = ring if solid is None else solid + ring

    # Cut to a half shell so it self-aligns on the pole and cannot trap itself.
    if SWEEP_DEG < 360.0:
        keep = Box(
            outer_d * 2, outer_d, total_h * 2,
            align=(Align.CENTER, Align.MIN, Align.MIN),
        )
        solid = solid & keep

    # Ruler: a groove at every step boundary, cut as a shallow annular relief so
    # it reads all the way around the 180 deg arc rather than only at one spot.
    # Boundary n is between step n and step n+1, counted up from the bottom
    # (largest bore), which is the end you hold.
    for n in range(1, len(dias)):
        z = n * STEP_HEIGHT
        witness = (n % WITNESS_EVERY) == 0
        w = WITNESS_W if witness else TICK_W
        depth = WITNESS_DEPTH if witness else TICK_DEPTH
        groove = Cylinder(
            radius=outer_d / 2.0 + 1.0, height=w,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
        ) - Cylinder(
            radius=outer_d / 2.0 - depth, height=w * 2,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
        )
        solid = solid - (Pos(0, 0, z) * groove)

    # Chamfer the leading (top, smallest) bore so it does not catch on the pole.
    solid = solid.chamfer(
        length=1.0, length2=None,
        edge_list=[e for e in solid.edges().group_by(Axis.Z)[-1]],
    )
    return solid


if __name__ == "__main__":
    dias = step_diameters()
    print(f"gauge steps: {len(dias)} from {min(dias):.1f} to {max(dias):.1f} mm "
          f"in {STEP_INCREMENT} mm increments")
    raise SystemExit(_base.cli(build, NAME, MATERIAL))
