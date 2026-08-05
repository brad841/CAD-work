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
from parts import _base, _bayonet  # noqa: E402

NAME = "bayonet_coupon_male"
MATERIAL = "PETG"

# Enough stub above the lugs to grip and twist by hand, no more.
GRIP_H = 12.0
LEAD_IN = 0.4          # verified buildable; 0.8 is rejected by OCC here


def build() -> Part:
    """The production spigot, cut short above the lugs.

    Body geometry comes from parts/_bayonet.spigot() — shared with the real
    cradle boom — so this coupon tests the production joint, not a lookalike.
    """
    total_h = B.LUG_Z + B.LUG_AXIAL_H + GRIP_H
    solid = _bayonet.spigot(total_h)
    return _bayonet.chamfer_lug_tops(solid, LEAD_IN)


if __name__ == "__main__":
    print(f"spigot {B.SPIGOT_D} mm, {B.LUG_COUNT} lugs x {B.LUG_ARC_DEG} deg, "
          f"twist {B.TWIST_DEG} deg, lug shear area {B.lug_shear_area_mm2():.0f} mm^2")
    raise SystemExit(_base.cli(build, NAME, MATERIAL))
