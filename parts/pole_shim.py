"""
POLE SHIM — how an unconfirmable pole becomes a fit.

The clamp closes on the LARGEST pole in the design range. Anything smaller gets
shims between shell and liner until the band closes properly. A shim only ever
adds material inward, so a wrong guess about the pole makes the stack thicker
rather than the grip looser — which is the whole reason this design tolerates not
knowing the pole.

Printed as a set: 0.5, 1.0 and 1.5 mm radial, stacking to 3.0 mm, which covers
the full 62.0-65.0 mm range from either end. The pole gauge coupon tells you
which stack to use.

Run with a thickness argument to generate one:
    python parts/pole_shim.py 1.0
Run bare to generate the whole set.

Print: curved face flat on the plate. Pure compression, so orientation is a
print-quality choice rather than a strength one — but print them with the arc
lying down or a 0.5 mm shim will curl off the bed.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Part  # noqa: E402

from params import clamp as L  # noqa: E402
from params import derived as D  # noqa: E402
from params import gate0 as G  # noqa: E402
from parts import _base  # noqa: E402

NAME = "pole_shim"
MATERIAL = "PETG"

# A tab makes a thin arc possible to place and, more importantly, to remove with
# cold fingers. Sticking out radially would foul the shell, so it runs axially.
TAB_H = 6.0
TAB_W = 14.0


def build(thickness: float = 1.0) -> Part:
    d = D.compute()

    # The shim sits against the shell bore and pushes the liner inward, so its
    # outer face is the shell bore and it grows inward by `thickness`.
    outer_r = d.shell_bore_d / 2.0
    inner_r = outer_r - thickness
    height = d.clamp_band_height * L.SHIM_HEIGHT_FRACTION

    solid = _base.sector(
        r_outer=outer_r, r_inner=inner_r, height=height,
        centre_deg=0.0, arc_deg=L.SHIM_WRAP_DEG,
    )

    # Pull tab, axial so it cannot interfere with the clamp closing.
    tab = _base.sector(
        r_outer=outer_r, r_inner=inner_r, height=TAB_H,
        centre_deg=0.0, arc_deg=TAB_W,
    )
    from build123d import Pos  # local: only needed here
    solid = solid + (Pos(0, 0, height) * tab)

    return solid


def build_named(thickness: float):
    def _b() -> Part:
        return build(thickness)
    return _b


if __name__ == "__main__":
    d = D.compute()
    if len(sys.argv) > 1:
        t = float(sys.argv[1])
        thicknesses = [t]
    else:
        thicknesses = list(G.SHIM_THICKNESSES)

    print(f"shell bore {d.shell_bore_d:.2f} mm, shim wrap {L.SHIM_WRAP_DEG:.0f} deg, "
          f"height {d.clamp_band_height * L.SHIM_HEIGHT_FRACTION:.1f} mm")
    print(f"stack to {G.SHIM_STACK_MAX:.1f} mm covers "
          f"{d.pole_od_min:.1f}-{d.pole_od_max:.1f} mm")

    rc = 0
    for t in thicknesses:
        name = f"{NAME}_{str(t).replace('.', 'p')}mm"
        rc |= _base.cli(build_named(t), name, MATERIAL)
    raise SystemExit(rc)
