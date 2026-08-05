"""
LEVER LINK — STEEL, not printed. Laser-cut profile.

This part is the reason the clamp holds: 172 N of tension, continuously, for as
long as the mount is up. It is the only member in the whole assembly under
genuinely sustained high tension, and that is exactly the load case PETG is worst
at.

Why it is not printed, with the numbers:

    PETG 8 x 10 mm strap   80 mm^2   2.15 MPa   1.5x over the derated allowable
    pin bearing on M5      4.6 MPa   ALREADY OVER the 3.15 MPa sustained limit
    steel 3 x 8 mm         24 mm^2   7.15 MPa   21x, and 7.5 g

A printed link would have to grow to roughly 88 mm^2 just to reach the 5x creep
margin, and its pin bearing would still be marginal. Steel is smaller, lighter,
21x stronger, and it is what the brief means by the lever reading as hardware
rather than as a printed strap.

The STEP this generates is the CUTTING PROFILE — a flat 3 mm plate outline with
two bores. Send it to a laser cutter or a waterjet, or file it out of 3 mm mild
steel flat bar by hand: it is two holes and a rounded rectangle.

Deburr both bores. A sharp bore edge on a steel link will chew the M5 clevis pin's
bearing surface and, worse, the PETG boss it pivots against.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Box, Cylinder, Part, Pos  # noqa: E402

from params import clearances as C  # noqa: E402
from params import derived as D  # noqa: E402
from params import lever as V  # noqa: E402
from parts import _base  # noqa: E402

NAME = "lever_link"
MATERIAL = "steel"

# Mild steel, sustained. 250 MPa yield with a generous knockdown for a hand-cut
# part with unknown edge quality — nowhere near governing here either way.
STEEL_ALLOWABLE_MPA = 150.0


def build() -> Part:
    length = V.link_length()
    bore = V.LINK_PIN_D + C.LEVER_PIN_TO_BORE

    # Two pin bosses joined by the strap. Thickness is the plate thickness, so
    # the whole part is a constant-thickness profile — which is what makes it
    # laser-cuttable rather than machined.
    solid = Cylinder(radius=V.LINK_END_R, height=V.LINK_T,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
    solid = solid + (Pos(length, 0, 0) * Cylinder(
        radius=V.LINK_END_R, height=V.LINK_T,
        align=(Align.CENTER, Align.CENTER, Align.MIN)))
    solid = solid + Box(length, V.LINK_W, V.LINK_T,
                        align=(Align.MIN, Align.CENTER, Align.MIN))

    for x in (0.0, length):
        solid = solid - (Pos(x, 0, V.LINK_T / 2.0) * Cylinder(
            radius=bore / 2.0, height=V.LINK_T * 3,
            align=(Align.CENTER, Align.CENTER, Align.CENTER)))

    return solid


def section_mm2() -> float:
    return V.LINK_W * V.LINK_T


def stress_mpa() -> float:
    return D.compute().link_tension_n / section_mm2()


def margin() -> float:
    return STEEL_ALLOWABLE_MPA / stress_mpa()


if __name__ == "__main__":
    d = D.compute()
    print(f"STEEL, 3 mm plate — laser-cut profile, not printed")
    print(f"pin centres {V.link_length():.2f} mm, overall "
          f"{V.link_length() + 2*V.LINK_END_R:.2f} mm")
    print(f"tension {d.link_tension_n:.0f} N through {section_mm2():.1f} mm^2 "
          f"= {stress_mpa():.2f} MPa, margin {margin():.0f}x")
    print(f"bore {V.LINK_PIN_D + C.LEVER_PIN_TO_BORE:.2f} mm for an M{V.LINK_PIN_D:.0f} clevis pin")
    raise SystemExit(_base.cli(build, NAME, MATERIAL))
