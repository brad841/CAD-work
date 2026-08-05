"""
CLAMP BACKER — the other half of the split clamp. A curved block, nothing more.

This is the entire second part: a matching collar arc with two through-holes and
two flanges that sandwich between the bracket's. No features, no orientation
subtlety beyond printing it the same way up as the bracket.

Print: pole axis normal to the plate, same as the bracket's collar. The bore is
then a vertical hole with nothing to bridge, and hoop compression runs in-plane.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Box, Cylinder, Part, Pos  # noqa: E402

from params import bracket as P  # noqa: E402
from parts import _base  # noqa: E402
from parts.pole_bracket import WRAP_DEG  # noqa: E402

NAME = "clamp_backer"
MATERIAL = "PETG"

# Fills the arc the bracket does not cover, less a little at each end so the two
# halves close on the POLE rather than butting against each other. If they touch
# first, the clamp is rigid at whatever diameter that happens to be and the
# preload goes nowhere.
END_RELIEF_DEG = 5.0


def build() -> Part:
    bore_r = P.bore_d() / 2.0
    od_r = P.collar_od() / 2.0
    arc = 360.0 - WRAP_DEG - 2.0 * END_RELIEF_DEG

    # sector() is limited to arcs under 180 deg, so build the back half as two
    # mirrored quadrant-ish pieces meeting on the centreline.
    # Overlap the two halves by OVERLAP_DEG. Butting them exactly at 90 deg is a
    # zero-thickness contact, which OCC keeps as two separate bodies.
    OVERLAP_DEG = 4.0
    half = arc / 2.0 + OVERLAP_DEG
    solid = _base.sector(r_outer=od_r, r_inner=bore_r, height=P.BAND_H,
                         centre_deg=90.0 - arc / 4.0, arc_deg=half)
    solid = solid + _base.sector(
        r_outer=od_r, r_inner=bore_r, height=P.BAND_H,
        centre_deg=90.0 + arc / 4.0, arc_deg=half)

    # Bolt pads, facing the bracket's across the split gap. Clearance holes —
    # the threads live in the bracket's inserts.
    od_r_ = od_r
    pad_x = od_r_ - 2.0
    pad_h = P.BAND_H * P.FLANGE_H_FRAC
    pad_z = (P.BAND_H - pad_h) / 2.0
    for sx in (-1.0, 1.0):
        pad = Box(P.FLANGE_W, P.FLANGE_BOLT_T, pad_h,
                  align=(Align.CENTER, Align.MIN, Align.MIN))
        solid = solid + (Pos(sx * pad_x, P.SPLIT_Y + P.SPLIT_GAP, pad_z) * pad)
        solid = solid - (Pos(sx * pad_x, P.SPLIT_Y + P.SPLIT_GAP + P.FLANGE_BOLT_T / 2.0,
                             P.BAND_H / 2.0) * Cylinder(
            radius=P.BOLT_CLEAR_D / 2.0, height=P.FLANGE_BOLT_T * 4,
            align=(Align.CENTER, Align.CENTER, Align.CENTER), rotation=(90, 0, 0)))

    return solid


if __name__ == "__main__":
    print(f"back arc {360.0 - WRAP_DEG - 2*END_RELIEF_DEG:.0f} deg, "
          f"{END_RELIEF_DEG:.0f} deg relief each end so the halves close on the "
          f"POLE, not on each other")
    raise SystemExit(_base.cli(build, NAME, MATERIAL))
