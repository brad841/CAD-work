"""
TRAY — where the speaker actually sits. Gravity does the work.

The speaker stands UPRIGHT on this and compresses into the charging contacts under
its own 3 kg. The body is never clamped and never gripped: the lip only locates it,
and the rear-handle hook only stops it walking forward when pitched nose-down.

Aft edge is deliberately OPEN. Two reasons, both about water and cable: the
charging cable leaves downward without a bend that traps water, and the speaker can
be slid in from behind against the hook rather than dropped in past a lip.

Drain slots are not lightening holes that happen to drain — they are drains that
happen to lighten. A solid tray under an IP56 speaker holds a puddle, and standing
water is precisely what finds its way into a charging base Sonos rates indoor only.
They run fore-aft so water leaves at the open aft edge rather than pooling at a lip.

Anti-slip pad recesses are shallow pockets, not proud bosses: a pad that stands
above the tray floor becomes the only contact and concentrates 3 kg onto four
small spots.

Print: tray face DOWN on the plate. The show surface comes off the glass, tray
bending stays in-plane, and the lip prints as a wall rather than an overhang.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Box, Cylinder, Part, Pos  # noqa: E402

from params import clearances as C  # noqa: E402
from params import cradle as R  # noqa: E402
from params import derived as D  # noqa: E402
from params import gate0 as G  # noqa: E402
from parts import _base  # noqa: E402

NAME = "tray"
MATERIAL = "PETG"

LUG_W = 15.0              # sits in the boom fork's PLATE_GAP
LUG_H = 34.0
LUG_T = 15.0
HOOK_MOUNT_W = 30.0
HOOK_BOLT_D = 5.4         # M5 clear, clamps the hook post at chosen height


def build() -> Part:
    d = D.compute()
    w = R.tray_w()
    depth = R.tray_d()

    # Floor.
    solid = Box(w, depth, R.TRAY_T,
                align=(Align.CENTER, Align.CENTER, Align.MIN))

    # Lip: front and both sides. Aft is open on purpose.
    front = Box(w, R.TRAY_LIP_T, R.TRAY_LIP_H + R.TRAY_T,
                align=(Align.CENTER, Align.MIN, Align.MIN))
    solid = solid + (Pos(0, -depth / 2.0, 0) * front)
    for sx in (-1.0, 1.0):
        side = Box(R.TRAY_LIP_T, depth, R.TRAY_LIP_H + R.TRAY_T,
                   align=(Align.CENTER, Align.CENTER, Align.MIN))
        solid = solid + (Pos(sx * (w / 2.0 - R.TRAY_LIP_T / 2.0), 0, 0) * side)

    # Rib grid: windows cut out of the floor, leaving ribs under the load paths.
    # These are drains first and lightening second — a solid floor under an IP56
    # speaker holds a puddle, and standing water is what reaches a charging base
    # that Sonos rates indoor only.
    inner_w = w - 2.0 * R.TRAY_LIP_T - R.RIB_W
    inner_d = depth - R.TRAY_LIP_T - R.RIB_W
    win_w = (inner_w - (R.WINDOW_COLS - 1) * R.RIB_W) / R.WINDOW_COLS
    win_d = (inner_d - (R.WINDOW_ROWS - 1) * R.RIB_W) / R.WINDOW_ROWS
    for i in range(R.WINDOW_COLS):
        for j in range(R.WINDOW_ROWS):
            cx = -inner_w / 2.0 + win_w / 2.0 + i * (win_w + R.RIB_W)
            cy = -inner_d / 2.0 + win_d / 2.0 + j * (win_d + R.RIB_W)
            win = Box(win_w, win_d, R.TRAY_T * 3,
                      align=(Align.CENTER, Align.CENTER, Align.CENTER))
            solid = solid - (Pos(cx, cy, R.TRAY_T / 2.0) * win)

    # Anti-slip pad recesses, near the corners where the speaker actually bears.
    # Pads sit just inside the perimeter rail, where there is continuous material
    # rather than a window.
    px = w / 2.0 - R.TRAY_LIP_T - R.PAD_RECESS_D / 2.0 - 1.0
    py = depth / 2.0 - R.TRAY_LIP_T - R.PAD_RECESS_D / 2.0 - 1.0
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            pocket = Cylinder(radius=R.PAD_RECESS_D / 2.0,
                              height=R.PAD_RECESS_DEPTH * 2,
                              align=(Align.CENTER, Align.CENTER, Align.CENTER))
            solid = solid - (Pos(sx * px, sy * py, R.TRAY_T) * pocket)

    # --- Pitch hinge lug, under the tray, aft ------------------------------
    hinge_bore = R.PITCH_HINGE_PIN_D + C.PITCH_PIN_TO_PLATE_HOLE
    index_bore = R.PITCH_PIN_D + C.PITCH_PIN_TO_PLATE_HOLE
    # Lug at the tray CENTRE, not the aft edge: the boom fork arrives under the
    # middle of the tray, and a pivot near the load also keeps the index pin force
    # down.
    lug_y = 0.0
    lug = Box(LUG_W, LUG_T, LUG_H, align=(Align.CENTER, Align.CENTER, Align.MAX))
    solid = solid + (Pos(0, lug_y, 0) * lug)

    # Gussets tying the lug into the floor. The tray cantilevers forward off this
    # single lug, so ~2.2 N*m arrives here; a bare 15 mm lug root would be a
    # stress riser straight across the layer lines.
    for sy in (-1.0, 1.0):
        g = Box(LUG_W, 14.0, 12.0, align=(Align.CENTER, Align.CENTER, Align.MAX))
        solid = solid + (Pos(0, lug_y + sy * (LUG_T / 2.0 + 6.0), 0) * g)

    hinge_z = -R.LUG_HINGE_DROP
    for bore in (hinge_bore,):
        solid = solid - (Pos(0, lug_y, hinge_z) * Cylinder(
            radius=bore / 2.0, height=LUG_W * 3,
            align=(Align.CENTER, Align.CENTER, Align.CENTER), rotation=(0, 90, 0)))
    # Single index hole: the boom carries the arc, the tray carries one hole, and
    # the pin through both selects the angle.
    solid = solid - (Pos(0, lug_y, hinge_z - R.PITCH_PLATE_R * 0.42) * Cylinder(
        radius=index_bore / 2.0, height=LUG_W * 3,
        align=(Align.CENTER, Align.CENTER, Align.CENTER), rotation=(0, 90, 0)))

    # --- Hook post mounting, aft face -------------------------------------
    # A vertical pad with two M5 clear holes. The hook post clamps against this at
    # whatever height the real handle recess turns out to need.
    mount = Box(HOOK_MOUNT_W + 12.0, R.HOOK_POST_T + 4.0, R.TRAY_T + 16.0,
                align=(Align.CENTER, Align.MAX, Align.MIN))
    solid = solid + (Pos(0, depth / 2.0, 0) * mount)
    for dz in (5.0, 13.0):
        solid = solid - (Pos(0, depth / 2.0 - (R.HOOK_POST_T + 4.0) / 2.0, dz)
                         * Cylinder(radius=HOOK_BOLT_D / 2.0,
                                    height=(R.HOOK_POST_T + 4.0) * 4,
                                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                                    rotation=(90, 0, 0)))

    return solid


if __name__ == "__main__":
    print(f"tray {R.tray_w():.1f} x {R.tray_d():.1f} mm for a "
          f"{G.SPEAKER_W:.0f} x {G.SPEAKER_D:.0f} mm speaker "
          f"({C.TRAY_TO_SPEAKER_FOOTPRINT:+.1f} mm locating clearance)")
    print(f"lip {R.TRAY_LIP_H:.0f} mm on front and sides, aft OPEN for drainage")
    print(f"{R.DRAIN_COUNT} drain slots, {R.PAD_COUNT} anti-slip recesses")
    raise SystemExit(_base.cli(build, NAME, MATERIAL))
