"""
Shared bayonet geometry — the collar body, used by both the coupon and the
production collar.

Extracted so the coupon and the real part cannot diverge. If the coupon fits your
printer and your hand, the production collar carries exactly the same slots,
because it is the same code with a different outer body bolted to it.
"""

from __future__ import annotations

from build123d import Align, Cylinder, Part, Pos, Rot

from params import bayonet as B
from params import clearances as C
from parts import _base

# Twist direction. Positive = counter-clockwise from above; the installer reaches
# up and rotates the cradle toward themselves.
TWIST_SIGN = +1.0


def collar_ring(height: float | None = None) -> Part:
    """The bored ring with L-slots and blind detent pockets.

    The groove FLOOR is the load-bearing face — the lug bears down on it and that
    is how the suspended moment crosses the joint. It is solid material out to the
    collar wall, never undercut.
    """
    h = B.COLLAR_H if height is None else height
    bore_r = B.collar_bore_d() / 2.0
    od_r = B.collar_od() / 2.0
    lug_r = bore_r + B.LUG_RADIAL + C.BAYONET_LUG_RADIAL

    solid = Cylinder(radius=od_r, height=h,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
    solid -= Cylinder(radius=bore_r, height=h * 3,
                      align=(Align.CENTER, Align.CENTER, Align.CENTER))

    z_floor = h - B.LOCK_DEPTH
    slot_arc = B.slot_arc_deg()
    travel = B.travel_arc_deg()

    for ang in B.lug_angles():
        # Axial entry slot, from the groove floor up through the top face.
        entry = _base.sector(
            r_outer=lug_r, r_inner=bore_r - 0.5,
            height=h - z_floor + 1.0,
            centre_deg=ang, arc_deg=slot_arc,
        )
        solid = solid - (Pos(0, 0, z_floor) * entry)

        # Circumferential groove: entry slot plus twist plus overtravel, swept
        # only in the twist direction.
        groove = _base.sector(
            r_outer=lug_r, r_inner=bore_r - 0.5,
            height=B.groove_height(),
            centre_deg=ang + TWIST_SIGN * travel / 2.0,
            arc_deg=slot_arc + travel,
        )
        solid = solid - (Pos(0, 0, z_floor) * groove)

        # Blind detent pocket at the end of travel. It must NOT break through to
        # the outside or it becomes a water path into the joint.
        det_ang = ang + TWIST_SIGN * B.TWIST_DEG
        pocket = Cylinder(
            radius=B.DETENT_D / 2.0, height=B.DETENT_POCKET_DEPTH,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            rotation=(0, -90, 0),
        )
        solid = solid - (Rot(0, 0, det_ang) * (
            Pos(lug_r, 0, z_floor + B.groove_height() / 2.0) * pocket
        ))

    return solid


def wall_behind_pocket() -> float:
    """Material left between detent pocket floor and the outer surface."""
    bore_r = B.collar_bore_d() / 2.0
    lug_r = bore_r + B.LUG_RADIAL + C.BAYONET_LUG_RADIAL
    return B.collar_od() / 2.0 - (lug_r + B.DETENT_POCKET_DEPTH)


def spigot(total_h: float, wall: float | None = None) -> Part:
    """The male spigot with its lugs and detent seats."""
    w = B.SPIGOT_WALL if wall is None else wall
    solid = Cylinder(radius=B.SPIGOT_D / 2.0, height=total_h,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
    solid -= Cylinder(radius=B.SPIGOT_D / 2.0 - w, height=total_h,
                      align=(Align.CENTER, Align.CENTER, Align.MIN))

    for ang in B.lug_angles():
        lug = _base.sector(
            r_outer=B.SPIGOT_D / 2.0 + B.LUG_RADIAL,
            r_inner=B.SPIGOT_D / 2.0 - w,
            height=B.LUG_AXIAL_H, centre_deg=ang, arc_deg=B.LUG_ARC_DEG,
        )
        solid = solid + (Pos(0, 0, B.LUG_Z) * lug)

    for ang in B.lug_angles():
        pocket = Cylinder(
            radius=B.DETENT_D / 2.0, height=B.DETENT_POCKET_DEPTH,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            rotation=(0, 90, 0),
        )
        solid = solid - (Rot(0, 0, ang + B.LUG_ARC_DEG / 2.0 - 6.0) * (
            Pos(B.SPIGOT_D / 2.0 + B.LUG_RADIAL - B.DETENT_POCKET_DEPTH, 0,
                B.LUG_Z + B.LUG_AXIAL_H / 2.0) * pocket
        ))

    return solid


def chamfer_lug_tops(solid: Part, lead_in: float = 0.4) -> Part:
    """Lead-in on the lugs' outer top edges only.

    Restricted to those edges because sweeping up every edge at that height also
    catches the sector's inner arcs and the detent rim, where OCC rejects the
    operation outright.
    """
    z_top = B.LUG_Z + B.LUG_AXIAL_H
    r_out = B.SPIGOT_D / 2.0 + B.LUG_RADIAL
    edges = [
        e for e in solid.edges()
        if abs(e.center().Z - z_top) < 0.01
        and abs(max((v.X ** 2 + v.Y ** 2) ** 0.5 for v in e.vertices()) - r_out) < 0.05
    ]
    if not edges:
        raise _base.SolidRejected("lug top edges not found — lugs missing")
    return solid.chamfer(length=lead_in, length2=None, edge_list=edges)
