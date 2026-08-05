"""
BAYONET COLLAR — the dock. Bolts to the fixed shell's pad; receives the cradle.

The collar ring itself is parts/_bayonet.collar_ring(), the same code the coupon
prints, so a coupon that fits proves this fits. What this module adds is the
flange that bolts it to the clamp, and the release tab.

Load path: the cradle's lugs bear down on the groove floor, the floor carries into
the collar wall, the wall into the flange, the flange into four M5 heat-set inserts
in the fixed shell's pad. Four bolts in a rectangle, so the boom's moment is
resisted as a couple between bolt pairs rather than as bolt bending.

The bayonet axis is VERTICAL — parallel to the pole. That is what lets the cradle
be dropped in from above with one hand and then twisted, rather than offered up
horizontally and held while you find a thread.

Print: bayonet axis normal to the plate. The groove floor then comes out as an
in-plane top surface, so the suspended load crosses layers in compression instead
of pulling them apart, and the slots need no bridging.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Box, Cylinder, Part, Pos  # noqa: E402

from params import bayonet as B  # noqa: E402
from params import clamp as L  # noqa: E402
from params import clearances as C  # noqa: E402
from parts import _base, _bayonet  # noqa: E402

NAME = "bayonet_collar"
MATERIAL = "PETG"

FLANGE_T = B.COLLAR_FLANGE_T
# Span between the ring's outer surface and the flange's inner face. The gusset
# lives in it, so it must be positive — computing the gusset from an offset that
# put the flange INSIDE the ring produced a negative box dimension and an OCP
# Standard_DomainError rather than anything diagnosable.
EMBED = B.COLLAR_FLANGE_EMBED
M5_CLEAR = 5.4          # through-hole for the M5 bolt shank, not a heat-set bore
RELEASE_TAB_W = 16.0
RELEASE_TAB_H = 9.0
RELEASE_TAB_REACH = 13.0
MOUTH_CHAMFER = 0.6


def ring_outer_y() -> float:
    return B.collar_od() / 2.0


def flange_inner_y() -> float:
    return ring_outer_y() - EMBED


def flange_offset() -> float:
    """Bayonet axis to the flange's MATING face. Shared with params.bayonet."""
    return B.flange_offset()


def build() -> Part:
    solid = _bayonet.collar_ring()

    # Flange, in the plane of the pad (normal along +Y in local coords). The pad
    # on the shell faces outward at BOOM_DEG; the cradle assembly script places
    # this part, so locally the flange sits at +Y.
    flange = Box(L.PAD_W, FLANGE_T, min(L.PAD_H, B.COLLAR_H + 18.0),
                 align=(Align.CENTER, Align.MIN, Align.CENTER))
    flange = Pos(0, flange_inner_y(), B.COLLAR_H / 2.0) * flange
    solid = solid + flange

    # Gusset tying flange to collar. Without it the flange is a cantilever plate
    # and the boom's moment tries to peel it off the ring. Rooted 4 mm inside the
    # ring wall so it is genuinely fused, not just touching.
    # Side ribs from the flange around the ring's flanks. With the flange tangent
    # there is no span to gusset, so the stiffening runs sideways instead: the
    # flange's moment is resisted by these rather than by the tangent line alone.
    for sx in (-1.0, 1.0):
        rib = Box(FLANGE_T, ring_outer_y() * 0.9, B.COLLAR_H * 0.7,
                  align=(Align.CENTER, Align.MIN, Align.MIN))
        solid = solid + (Pos(sx * (ring_outer_y() - FLANGE_T / 2.0 - 1.0),
                             0.0, B.COLLAR_H * 0.15) * rib)

    # Four M5 through-holes matching the pad's boss rectangle exactly.
    for dx in (-L.PAD_BOLT_DX / 2.0, L.PAD_BOLT_DX / 2.0):
        for dz in (-L.PAD_BOLT_DZ / 2.0, L.PAD_BOLT_DZ / 2.0):
            hole = Cylinder(radius=M5_CLEAR / 2.0, height=FLANGE_T * 4,
                            align=(Align.CENTER, Align.CENTER, Align.CENTER),
                            rotation=(90, 0, 0))
            solid = solid - (Pos(dx, flange_inner_y() + FLANGE_T / 2.0,
                                 B.COLLAR_H / 2.0 + dz) * hole)

    # Release tab: a finger purchase on the side opposite the flange, so the
    # deliberate second motion has something to act on. Chamfered — it is a place
    # a hand goes.
    tab = Box(RELEASE_TAB_W, RELEASE_TAB_REACH, RELEASE_TAB_H,
              align=(Align.CENTER, Align.MAX, Align.MIN))
    tab = Pos(0, -B.collar_od() / 2.0 + 3.0, B.COLLAR_H - RELEASE_TAB_H) * tab
    solid = solid + tab

    top_edges = [e for e in solid.edges()
                 if abs(e.center().Z - B.COLLAR_H) < 0.01]
    if top_edges:
        try:
            solid = solid.chamfer(length=MOUTH_CHAMFER, length2=None,
                                  edge_list=top_edges)
        except Exception:  # noqa: BLE001
            # Sweeping every top edge also catches the slot mouths and the release
            # tab, where OCC refuses. The bore rim alone is the edge that actually
            # matters for finding the joint blind, so fall back to it rather than
            # dropping the lead-in altogether.
            rim = [e for e in top_edges
                   if abs((e.center().X ** 2 + e.center().Y ** 2) ** 0.5
                          - B.collar_bore_d() / 2.0) < 1.5]
            if rim:
                solid = solid.chamfer(length=MOUTH_CHAMFER, length2=None,
                                      edge_list=rim)
            else:
                raise _base.SolidRejected(
                    f"{NAME}: no chamferable bore rim — the mouth would have no "
                    f"lead-in, and this joint is mated blind at arm's length")

    return solid


if __name__ == "__main__":
    print(f"collar bore {B.collar_bore_d():.2f} mm, OD {B.collar_od():.2f} mm")
    print(f"flange {L.PAD_W:.0f} x {min(L.PAD_H, B.COLLAR_H+18):.0f} mm, "
          f"4 x M5 on {L.PAD_BOLT_DX:.0f} x {L.PAD_BOLT_DZ:.0f} mm centres")
    print(f"wall behind detent pocket {_bayonet.wall_behind_pocket():.2f} mm")
    print(f"lug bearing area {B.lug_shear_area_mm2():.0f} mm^2")
    raise SystemExit(_base.cli(build, NAME, MATERIAL))
