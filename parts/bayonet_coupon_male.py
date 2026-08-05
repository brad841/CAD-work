"""
BAYONET COUPON, MALE — the spigot end, cut short.

Second half of the physical gate. Printed with its mating collar, this pair
proves the tolerance stack at the bayonet before any full-size part is committed:
whether it drops in, whether the 15 deg twist lands on the detent, and whether
the lock has slop you can feel at the speaker.

Cut short deliberately — everything above the lugs is boom, and the boom is not
what this coupon is testing.

Print: bayonet axis normal to the plate. Same as the real cradle spigot, so the
lug bearing faces come out as in-plane walls and the coupon is honest about what
the real part's layers will do.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Cylinder, Part, Pos, Rot  # noqa: E402

from params import bayonet as B  # noqa: E402
from parts import _base  # noqa: E402

NAME = "bayonet_coupon_male"
MATERIAL = "PETG"

# Enough stub above the lugs to grip and twist by hand, no more.
GRIP_H = 12.0
LEAD_IN = 0.4          # verified buildable; 0.8 is rejected by OCC here


def build() -> Part:
    total_h = B.LUG_Z + B.LUG_AXIAL_H + GRIP_H

    # Hollow spigot. Diameter carries the moment; the wall only has to hold the
    # lugs' root, so it runs thin.
    solid = Cylinder(
        radius=B.SPIGOT_D / 2.0, height=total_h,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ) - Cylinder(
        radius=B.SPIGOT_D / 2.0 - B.SPIGOT_WALL, height=total_h,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    # Lugs. Each is an annular sector standing proud of the spigot OD, centred on
    # its angle so the collar's slot can be cut from the same angle list.
    for ang in B.lug_angles():
        lug = _base.sector(
            r_outer=B.SPIGOT_D / 2.0 + B.LUG_RADIAL,
            r_inner=B.SPIGOT_D / 2.0 - B.SPIGOT_WALL,
            height=B.LUG_AXIAL_H,
            centre_deg=ang,
            arc_deg=B.LUG_ARC_DEG,
        )
        solid = solid + (Pos(0, 0, B.LUG_Z) * lug)

    # Detent ball pocket in the lug's trailing flank — this is the half that
    # carries the ball; the collar carries the spring.
    for ang in B.lug_angles():
        pocket = Cylinder(
            radius=B.DETENT_D / 2.0, height=B.DETENT_POCKET_DEPTH,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            rotation=(0, 90, 0),
        )
        pocket = Rot(0, 0, ang + B.LUG_ARC_DEG / 2.0 - 6.0) * (
            Pos(B.SPIGOT_D / 2.0 + B.LUG_RADIAL - B.DETENT_POCKET_DEPTH, 0,
                B.LUG_Z + B.LUG_AXIAL_H / 2.0) * pocket
        )
        solid = solid - pocket

    # Lead-in chamfer on the lug top faces so the joint finds itself one-handed
    # in the dark, which is the actual use case.
    #
    # Selection is restricted to the lugs' OUTER top edges — the ones that meet
    # the collar mouth. Sweeping up every edge at this height also catches the
    # sector's inner arcs and the detent pocket's rim, where the local geometry
    # is too tight for a chamfer and OCC rejects the whole operation.
    #
    # LEAD_IN is 0.4 rather than the 0.8 first tried: 0.8 fails here, and the
    # honest fix is a chamfer that builds, not a chamfer that is skipped.
    z_top = B.LUG_Z + B.LUG_AXIAL_H
    r_out = B.SPIGOT_D / 2.0 + B.LUG_RADIAL
    top_edges = [
        e for e in solid.edges()
        if abs(e.center().Z - z_top) < 0.01
        and abs(max((v.X ** 2 + v.Y ** 2) ** 0.5 for v in e.vertices()) - r_out) < 0.05
    ]
    if not top_edges:
        raise _base.SolidRejected(
            f"{NAME}: no lug top edges found — the lugs are missing or displaced"
        )
    solid = solid.chamfer(length=LEAD_IN, length2=None, edge_list=top_edges)

    return solid


if __name__ == "__main__":
    print(f"spigot {B.SPIGOT_D} mm, {B.LUG_COUNT} lugs x {B.LUG_ARC_DEG} deg, "
          f"twist {B.TWIST_DEG} deg, lug shear area {B.lug_shear_area_mm2():.0f} mm^2")
    raise SystemExit(_base.cli(build, NAME, MATERIAL))
