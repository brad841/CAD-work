"""
BAYONET COUPON, FEMALE — the collar end, cut short.

Mate to bayonet_coupon_male. Together they discharge the second half of the
physical gate: drop the spigot in, twist 15 deg, feel the detent. If it binds, or
if the lock has play you can feel at arm's length, the fix is a number in
clearances.py and a reprint of two small parts — not a rework of the cradle.

Slot geometry is an L: an axial entry slot down to the lock datum, then a
circumferential groove sweeping the twist plus overtravel. The groove's FLOOR is
the load-bearing face — the lug bears down on it and that is how the suspended
moment crosses the joint. Its floor is therefore solid material all the way to
the collar wall, never undercut.

Print: bayonet axis normal to the plate. The groove floor then comes out as an
in-plane top surface rather than a bridge, and the load crosses layers in
compression instead of pulling them apart.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Cylinder, Part, Pos, Rot  # noqa: E402

from params import bayonet as B  # noqa: E402
from params import clearances as C  # noqa: E402
from parts import _base, _bayonet  # noqa: E402

NAME = "bayonet_coupon_female"
MATERIAL = "PETG"

# Twist direction. Positive = counter-clockwise seen from above; the installer
# reaches up and rotates the cradle toward themselves.
TWIST_SIGN = _bayonet.TWIST_SIGN
MOUTH_CHAMFER = 0.6


def build() -> Part:
    """The production collar ring, unmodified, with a mouth chamfer.

    Body geometry comes from parts/_bayonet.collar_ring() — the same code the
    production collar uses — so a coupon that fits proves the real part fits.
    """
    solid = _bayonet.collar_ring()

    top_edges = [e for e in solid.edges()
                 if abs(e.center().Z - B.COLLAR_H) < 0.01]
    if not top_edges:
        raise _base.SolidRejected(f"{NAME}: no top-face edges to chamfer")
    try:
        solid = solid.chamfer(length=MOUTH_CHAMFER, length2=None,
                              edge_list=top_edges)
    except Exception:  # noqa: BLE001
        rim = [e for e in top_edges
               if abs((e.center().X ** 2 + e.center().Y ** 2) ** 0.5) < 1.0]
        if rim:
            solid = solid.chamfer(length=MOUTH_CHAMFER, length2=None, edge_list=rim)
            print("  note: slot-mouth chamfer limited to the bore rim")
        else:
            print("  note: mouth chamfer skipped entirely")

    return solid


def wall_after_pocket() -> float:
    return _bayonet.wall_behind_pocket()


if __name__ == "__main__":
    print(f"collar bore {B.collar_bore_d():.2f} mm, OD {B.collar_od():.2f} mm, "
          f"slot {B.slot_arc_deg():.1f} deg, travel {B.travel_arc_deg():.1f} deg")
    w = wall_after_pocket()
    print(f"wall behind detent pocket: {w:.2f} mm")
    if w < 2.0:
        print("  !! under 2.0 mm — the pocket is close to breaking through")
    raise SystemExit(_base.cli(build, NAME, MATERIAL))
