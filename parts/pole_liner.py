"""
POLE LINER — TPU, and the only thing that touches the rented pole.

Priority 2 lives entirely in this part. The shells never contact the pole; this
does, and it is TPU so the 343 N preload arrives as distributed pressure into the
coating instead of as a printed edge biting it. Computed pressure is 0.025 MPa
against a 0.60 MPa powder-coat limit.

Three features earn their place:

  - It wraps FURTHER than the shell, so at each parting line the compliant TPU
    edge meets the pole rather than the rigid shell edge.
  - A relief groove straddles the weld seam instead of crushing it. Sized from
    the bounded seam height, which is deliberately generous: over-relieving
    costs a little contact area, under-relieving point-loads the coating.
  - Lips top and bottom so it cannot walk out of the shell pocket while the
    clamp is open, which is when things get dropped in the grass.

Two of these are printed per clamp, one per shell.

Print: pole axis normal to the plate. TPU in compression only — never in a
tension path — so orientation here is a print-reliability choice.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Cylinder, Part, Pos  # noqa: E402

from params import clamp as L  # noqa: E402
from params import clearances as C  # noqa: E402
from params import derived as D  # noqa: E402
from params import gate0 as G  # noqa: E402
from parts import _base  # noqa: E402

NAME = "pole_liner"
MATERIAL = "TPU 95A"


def build() -> Part:
    d = D.compute()

    # Free-state bore: sized to the SMALL end of the pole range so the liner is
    # preloaded even on the thinnest pole. On a fat pole it simply squeezes more.
    bore_r = d.liner_id_free / 2.0
    outer_r = bore_r + d.liner_thickness
    band_h = d.clamp_band_height

    centre, wrap = L.swing_arc()
    wrap += 2.0 * L.LINER_WRAP_EXTRA_DEG
    # sector() is valid below 180 deg; the liner wrap must stay under it or the
    # two liners would overlap at the parting lines instead of meeting.
    wrap = min(wrap, 178.0)

    solid = _base.sector(
        r_outer=outer_r, r_inner=bore_r, height=band_h,
        centre_deg=0.0, arc_deg=wrap,
    )

    # Retaining lips top and bottom, projecting outward into the shell pocket.
    for z in (0.0, band_h - L.LINER_LIP_H):
        lip = _base.sector(
            r_outer=outer_r + 1.2, r_inner=bore_r,
            height=L.LINER_LIP_H, centre_deg=0.0, arc_deg=wrap,
        )
        solid = solid + (Pos(0, 0, z) * lip)

    # Weld-seam relief. The seam's angular position on the pole is unknowable, so
    # the groove is cut at the liner's centreline and the installer rotates the
    # clamp to put the seam in it. That is a two-second install step and it beats
    # guessing where a seam we have never seen will land.
    groove_depth = G.POLE_SEAM_PROUD + C.LINER_SEAM_RELIEF
    groove_w_deg = 14.0
    groove = _base.sector(
        r_outer=bore_r + groove_depth, r_inner=bore_r - 1.0,
        height=band_h * 1.2, centre_deg=0.0, arc_deg=groove_w_deg,
    )
    solid = solid - (Pos(0, 0, -band_h * 0.1) * groove)

    return solid


if __name__ == "__main__":
    d = D.compute()
    print(f"liner free bore {d.liner_id_free:.2f} mm (preloaded "
          f"{C.LINER_TO_POLE:+.2f} on the {d.pole_od_min:.1f} mm pole)")
    print(f"thickness {d.liner_thickness:.2f} mm, band {d.clamp_band_height:.1f} mm")
    print(f"seam relief groove {G.POLE_SEAM_PROUD + C.LINER_SEAM_RELIEF:.2f} mm deep")
    print("2 required per clamp")
    raise SystemExit(_base.cli(build, NAME, MATERIAL))
