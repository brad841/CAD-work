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
from parts import _base  # noqa: E402

NAME = "bayonet_coupon_female"
MATERIAL = "PETG"

# Twist direction. Positive = counter-clockwise seen from above; the installer
# reaches up and rotates the cradle toward themselves.
TWIST_SIGN = +1.0
MOUTH_CHAMFER = 0.6


def build() -> Part:
    bore_r = B.collar_bore_d() / 2.0
    od_r = B.collar_od() / 2.0
    lug_r = bore_r + B.LUG_RADIAL + C.BAYONET_LUG_RADIAL

    solid = Cylinder(
        radius=od_r, height=B.COLLAR_H,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ) - Cylinder(
        radius=bore_r, height=B.COLLAR_H * 3,
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    )

    z_floor = B.groove_bottom_z()
    slot_arc = B.slot_arc_deg()
    travel = B.travel_arc_deg()

    for ang in B.lug_angles():
        # Axial entry slot: from the groove floor up through the top face.
        entry = _base.sector(
            r_outer=lug_r, r_inner=bore_r - 0.5,
            height=B.COLLAR_H - z_floor + 1.0,
            centre_deg=ang, arc_deg=slot_arc,
        )
        solid = solid - (Pos(0, 0, z_floor) * entry)

        # Circumferential groove: sweeps from the entry slot through the twist
        # plus overtravel. Centred so one flank stays coincident with the entry
        # slot and the sweep runs only in the twist direction.
        groove_arc = slot_arc + travel
        groove_centre = ang + TWIST_SIGN * travel / 2.0
        groove = _base.sector(
            r_outer=lug_r, r_inner=bore_r - 0.5,
            height=B.groove_height(),
            centre_deg=groove_centre, arc_deg=groove_arc,
        )
        solid = solid - (Pos(0, 0, z_floor) * groove)

        # Detent spring pocket, radial, at the end of travel. The collar carries
        # the spring and ball; the spigot's lug carries the seat. Blind pocket —
        # it must not break through to the outside, or it becomes a water path.
        det_ang = ang + TWIST_SIGN * B.TWIST_DEG
        pocket = Cylinder(
            radius=B.DETENT_D / 2.0, height=B.DETENT_POCKET_DEPTH,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            rotation=(0, -90, 0),
        )
        pocket = Rot(0, 0, det_ang) * (
            Pos(lug_r, 0, z_floor + B.groove_height() / 2.0) * pocket
        )
        solid = solid - pocket

    # Mouth chamfer on the slot entries so the lugs find the slots by feel.
    top_edges = [e for e in solid.edges()
                 if abs(e.center().Z - B.COLLAR_H) < 0.01]
    if not top_edges:
        raise _base.SolidRejected(f"{NAME}: no top-face edges to chamfer")
    try:
        solid = solid.chamfer(length=MOUTH_CHAMFER, length2=None,
                              edge_list=top_edges)
    except Exception:  # noqa: BLE001
        # Retry on the bore rim alone. Stated, not silently dropped — a collar
        # with no lead-in is harder to mate blind and that is worth knowing.
        rim = [e for e in top_edges
               if abs((e.center().X ** 2 + e.center().Y ** 2) ** 0.5) < 1.0]
        if rim:
            solid = solid.chamfer(length=MOUTH_CHAMFER, length2=None, edge_list=rim)
            print("  note: slot-mouth chamfer limited to the bore rim")
        else:
            print("  note: mouth chamfer skipped entirely")

    return solid


def wall_after_pocket() -> float:
    """Material left between the detent pocket floor and the outside surface.

    A blind pocket that nearly breaks through is a leak and a weak spot, so this
    is checked rather than assumed.
    """
    bore_r = B.collar_bore_d() / 2.0
    lug_r = bore_r + B.LUG_RADIAL + C.BAYONET_LUG_RADIAL
    return B.collar_od() / 2.0 - (lug_r + B.DETENT_POCKET_DEPTH)


if __name__ == "__main__":
    print(f"collar bore {B.collar_bore_d():.2f} mm, OD {B.collar_od():.2f} mm, "
          f"slot {B.slot_arc_deg():.1f} deg, travel {B.travel_arc_deg():.1f} deg")
    w = wall_after_pocket()
    print(f"wall behind detent pocket: {w:.2f} mm")
    if w < 2.0:
        print("  !! under 2.0 mm — the pocket is close to breaking through")
    raise SystemExit(_base.cli(build, NAME, MATERIAL))
