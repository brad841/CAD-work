"""
POLE BRACKET — the whole thing, in one printed part.

Collar half + twin arm webs + saddle + backstop, fused. Its mate is
`clamp_backer`, which is a plain curved block. Two parts, two M5 bolts, two
heat-set inserts.

PRINT ORIENTATION: saddle face DOWN on the bed. This is not a preference, it is
what makes the part support-free:

  - The saddle floor is the first layer — flat, well-stuck, and it becomes the
    show face the speaker sits on.
  - The collar is then a vertical tube: its bore is a vertical hole, so there is
    nothing to bridge across 66 mm.
  - The arm webs, the lip and the backstop are all vertical walls.
  - Bending from the cantilevered speaker runs in-plane, parallel to the layers,
    so the interlayer strength never governs.
  - The only horizontal holes are the two 5.4 mm bolt bores, which bridge fine.

Print it any other way and the load crosses layer boundaries. Saddle down.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from math import atan2, degrees  # noqa: E402

from build123d import (  # noqa: E402
    Align, Box, Cylinder, Part, Polygon, Pos, Rot, extrude,
)

from params import bracket as P  # noqa: E402
from parts import _base  # noqa: E402

NAME = "pole_bracket"
MATERIAL = "PETG"

# Collar wrap. The split is at the BACK (away from the speaker), so the bolts are
# reached from behind the pole and the arm side is unbroken material.
WRAP_DEG = 168.0


def build() -> Part:
    bore_r = P.bore_d() / 2.0
    od_r = P.collar_od() / 2.0
    saddle_y = P.saddle_centre_y()
    sw, sd = P.saddle_w(), P.saddle_d()

    # ---- Saddle floor: an open rim, not a plate -------------------------
    solid = Box(sw, sd, P.SADDLE_T,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
    solid = Pos(0, saddle_y, 0) * solid

    # Cut the middle out. A charging base of any size sits in this and the cable
    # falls through, which is why the base footprint never had to be measured.
    open_w = sw - 2.0 * (P.LIP_T + P.RIM_W)
    open_d = sd - 2.0 * (P.LIP_T + P.RIM_W)
    step = open_d / (P.CROSS_RIB_COUNT + 1)
    for i in range(P.CROSS_RIB_COUNT + 1):
        cy = -open_d / 2.0 + step / 2.0 + i * step
        win = Box(open_w, step - P.CROSS_RIB_W, P.SADDLE_T * 3,
                  align=(Align.CENTER, Align.CENTER, Align.CENTER))
        solid = solid - (Pos(0, saddle_y + cy, P.SADDLE_T / 2.0) * win)

    # ---- Retention lip: front and both sides, aft left open -------------
    front = Box(sw, P.LIP_T, P.LIP_H + P.SADDLE_T,
                align=(Align.CENTER, Align.MIN, Align.MIN))
    solid = solid + (Pos(0, saddle_y - sd / 2.0, 0) * front)
    for sx in (-1.0, 1.0):
        side = Box(P.LIP_T, sd, P.LIP_H + P.SADDLE_T,
                   align=(Align.CENTER, Align.CENTER, Align.MIN))
        solid = solid + (Pos(sx * (sw / 2.0 - P.LIP_T / 2.0), saddle_y, 0) * side)

    # ---- Collar half ----------------------------------------------------
    collar = _base.sector(r_outer=od_r, r_inner=bore_r, height=P.BAND_H,
                          centre_deg=270.0, arc_deg=WRAP_DEG)
    solid = solid + collar

    # ---- Clamp pads: one per side, at the collar's two ends ------------
    # Each pad carries a heat-set insert; the backer bolts into them from behind.
    # The pads sit just outboard of the bore, so they never touch the pole.
    pad_x = od_r - 2.0
    pad_h = P.BAND_H * P.FLANGE_H_FRAC
    pad_z = (P.BAND_H - pad_h) / 2.0
    ins_d = P.INSERT_D + P.INSERT_INTERFERENCE
    for sx in (-1.0, 1.0):
        pad = Box(P.FLANGE_W, P.FLANGE_INSERT_T, pad_h,
                  align=(Align.CENTER, Align.MAX, Align.MIN))
        solid = solid + (Pos(sx * pad_x, P.SPLIT_Y, pad_z) * pad)
        # Insert bore, into the pad along -Y from the mating face.
        solid = solid - (Pos(sx * pad_x, P.SPLIT_Y - P.INSERT_DEPTH / 2.0,
                             P.BAND_H / 2.0) * Cylinder(
            radius=ins_d / 2.0, height=P.INSERT_DEPTH,
            align=(Align.CENTER, Align.CENTER, Align.CENTER), rotation=(90, 0, 0)))

    # ---- Arm: a splayed shell from the collar to the saddle -------------
    # Starts inside the collar bore (y = +2) so it is unambiguously fused to it,
    # and ends past the saddle's rear rim for the same reason. A trapezoid in
    # plan, extruded vertically, so every face is a vertical wall.
    y_root = 2.0
    y_tip = saddle_y + sd / 2.0 - P.RIM_W
    outer = Polygon((-P.ARM_W_COLLAR / 2.0, y_root), (P.ARM_W_COLLAR / 2.0, y_root),
                    (P.ARM_W_SADDLE / 2.0, y_tip), (-P.ARM_W_SADDLE / 2.0, y_tip),
                    align=None)
    arm = extrude(outer, amount=P.BAND_H)
    solid = solid + arm

    # Hollow it from above, leaving the shell walls and the saddle floor as the
    # bottom. Open at the top, which is what keeps it support-free.
    inner = Polygon(
        (-(P.ARM_W_COLLAR / 2.0 - P.WEB_T), y_root - P.WEB_T),
        (P.ARM_W_COLLAR / 2.0 - P.WEB_T, y_root - P.WEB_T),
        (P.ARM_W_SADDLE / 2.0 - P.WEB_T, y_tip + P.WEB_T),
        (-(P.ARM_W_SADDLE / 2.0 - P.WEB_T), y_tip + P.WEB_T),
        align=None)
    pocket = Pos(0, 0, P.SADDLE_T) * extrude(inner, amount=P.BAND_H)
    solid = solid - pocket

    # Taper the arm's top down toward the saddle. Cut with a single sloped plane;
    # because it only shortens walls, the print stays support-free.
    drop = P.BAND_H - P.ARM_H_TIP
    span = abs(y_tip - y_root)
    ang = -degrees(atan2(drop, span))
    cutter = Box(P.ARM_W_SADDLE * 3, span * 3, P.BAND_H * 3,
                 align=(Align.CENTER, Align.CENTER, Align.MIN))
    solid = solid - (Pos(0, y_root, P.BAND_H) * (Rot(ang, 0, 0) * cutter))

    # ---- Backstop wall behind the speaker -------------------------------
    bs = Box(P.BACKSTOP_W, P.BACKSTOP_T, P.BACKSTOP_H,
             align=(Align.CENTER, Align.MAX, Align.MIN))
    solid = solid + (Pos(0, saddle_y + sd / 2.0, 0) * bs)
    # Small forward return at the top — an anti-roll catch, not a hook, so it
    # needs no handle-recess dimensions. Sloped underside keeps it printable.
    ret = Box(P.BACKSTOP_W, P.BACKSTOP_LIP, P.BACKSTOP_T,
              align=(Align.CENTER, Align.MAX, Align.MAX))
    solid = solid + (Pos(0, saddle_y + sd / 2.0 - P.BACKSTOP_T,
                         P.BACKSTOP_H) * ret)

    return solid


if __name__ == "__main__":
    print(f"ONE part. Grips {P.grip_min():.1f}-{P.grip_max():.1f} mm pole with "
          f"{P.TAPE_T:.0f} mm tape — no gauge, no shims")
    print(f"saddle {P.saddle_w():.1f} x {P.saddle_d():.1f} mm, centre "
          f"{abs(P.saddle_centre_y()):.1f} mm forward of the pole axis")
    print(f"load {P.load_n():.1f} N, moment {P.moment_nmm()/1000:.2f} N*m")
    print(f"hardware: 2 x M5 heat-set insert, 2 x M5 x 30 socket cap")
    print("PRINT SADDLE FACE DOWN — no supports")
    raise SystemExit(_base.cli(build, NAME, MATERIAL))
