"""
CRADLE BOOM — spigot, arm, and the pitch index fork. The whole suspended load.

Runs from the bayonet spigot forward to the tray. Because the collar bolts flat to
the clamp, its axis already sits 73 mm off the pole, and the tray sits OVER that
axis rather than beyond it — so this arm only has to reach 40 mm, not 130. A short
boom is the cheapest strength there is.

The tip forks into two pitch plates that straddle a single lug on the tray. Double
shear on the hinge pin, and the index pin passes through both plates and the lug,
so the pitch lock is a shear path rather than a friction joint.

Discrete index holes, not friction. A friction pitch joint creeps: over an
overnight in a hot tent it would sag, and the Sonos 20 deg limit would be silently
exceeded. Holes cannot creep past a position that does not exist, which makes the
limit structural instead of advisory. The hole angles come from
derived.pitch_positions_deg, which is itself clipped to the Sonos range — so there
is no way to drill a prohibited position without changing the limit.

Print: LONG AXIS FLAT ON THE PLATE, never standing up. Axial tension and bending
are then both in-plane. Standing this part up would run the entire suspended load
across layer boundaries, and PETG's interlayer allowable is roughly 60% of its
in-plane. This is the most orientation-critical part in the assembly.
"""

from __future__ import annotations

import sys
from math import cos, radians, sin
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Box, Cylinder, Part, Pos, Rot  # noqa: E402

from params import bayonet as B  # noqa: E402
from params import clearances as C  # noqa: E402
from params import cradle as R  # noqa: E402
from params import derived as D  # noqa: E402
from parts import _base, _bayonet  # noqa: E402

NAME = "cradle_boom"
MATERIAL = "PETG"

SPIGOT_H = B.LUG_Z + B.LUG_AXIAL_H + 8.0
PLATE_GAP = 16.0          # clear space between the fork plates for the tray lug
FORK_PLATE_T = 6.0


def build() -> Part:
    d = D.compute()
    reach = max(d.boom_reach, 28.0)

    # --- Spigot, pointing up out of the boom's underside ------------------
    solid = _bayonet.spigot(SPIGOT_H)
    solid = _bayonet.chamfer_lug_tops(solid, 0.4)

    # --- Arm, running forward in -Y ---------------------------------------
    root_z = SPIGOT_H
    arm = Box(R.BOOM_W_TIP, reach + B.SPIGOT_D / 2.0, R.BOOM_H_ROOT,
              align=(Align.CENTER, Align.MAX, Align.MIN))
    arm = Pos(0, B.SPIGOT_D / 2.0, root_z) * arm
    solid = solid + arm

    # Slope the arm's top down toward the tip: the moment falls off linearly from
    # the root, so the depth should too. Cut with a rotated box rather than lofted,
    # which keeps the whole part two booleans instead of a fragile surface blend.
    drop = R.BOOM_H_ROOT - R.BOOM_H_TIP
    ang = -1.0 * (drop / reach)
    cutter = Box(R.BOOM_W_TIP * 3, reach * 3, R.BOOM_H_ROOT * 3,
                 align=(Align.CENTER, Align.CENTER, Align.MIN))
    cutter = Rot(ang * 57.2958 * -1.0, 0, 0) * cutter
    solid = solid - (Pos(0, -reach, root_z + R.BOOM_H_ROOT) * cutter)

    # Root gusset: the arm meets the spigot where bending is highest, and a square
    # junction there is a stress riser straight across the layer lines.
    gus = Box(R.BOOM_W_ROOT, R.BOOM_H_ROOT, R.BOOM_H_ROOT,
              align=(Align.CENTER, Align.MAX, Align.MIN))
    solid = solid + (Pos(0, B.SPIGOT_D / 2.0, root_z) * gus)
    # Hollow it: a solid 44 x 26 x 26 block at the root is ~30 g and only its
    # outer skin is carrying the corner.
    gh = Box(R.BOOM_W_ROOT - 2.0 * d.boom_wall_t, R.BOOM_H_ROOT,
             R.BOOM_H_ROOT - 2.0 * d.boom_wall_t,
             align=(Align.CENTER, Align.MAX, Align.MIN))
    solid = solid - (Pos(0, B.SPIGOT_D / 2.0 - d.boom_wall_t,
                         root_z + d.boom_wall_t) * gh)

    # Hollow the arm from underneath, leaving top and bottom flanges and side
    # walls. A beam carries bending in its flanges; the material on the neutral
    # axis is mass, not strength. Wall from derived.boom_wall_t so the PETG
    # thickness multiplier reaches it.
    wt = d.boom_wall_t
    pocket = Box(R.BOOM_W_TIP - 2.0 * wt, reach - wt, R.BOOM_H_ROOT - 2.0 * wt,
                 align=(Align.CENTER, Align.MAX, Align.MIN))
    solid = solid - (Pos(0, B.SPIGOT_D / 2.0 - wt, root_z + wt) * pocket)

    # --- Pitch index fork at the tip --------------------------------------
    hinge_y = -reach
    hinge_z = root_z + R.BOOM_H_TIP / 2.0
    hinge_bore = R.PITCH_HINGE_PIN_D + C.PITCH_PIN_TO_PLATE_HOLE
    index_bore = R.PITCH_PIN_D + C.PITCH_PIN_TO_PLATE_HOLE

    for side in (-1.0, +1.0):
        x = side * (PLATE_GAP / 2.0 + FORK_PLATE_T / 2.0)
        plate = Cylinder(radius=R.PITCH_PLATE_R * 0.55, height=FORK_PLATE_T,
                         align=(Align.CENTER, Align.CENTER, Align.CENTER),
                         rotation=(0, 90, 0))
        plate = Pos(x, hinge_y, hinge_z) * plate
        solid = solid + plate

        # Web the plate back into the arm so the hinge load does not arrive
        # through a tangent line.
        web = Box(FORK_PLATE_T, R.PITCH_PLATE_R * 0.6, R.BOOM_H_TIP,
                  align=(Align.CENTER, Align.MIN, Align.CENTER))
        solid = solid + (Pos(x, hinge_y, hinge_z) * web)

    # Hinge bore through both plates.
    solid = solid - (Pos(0, hinge_y, hinge_z) * Cylinder(
        radius=hinge_bore / 2.0, height=PLATE_GAP + 4 * FORK_PLATE_T + 10.0,
        align=(Align.CENTER, Align.CENTER, Align.CENTER), rotation=(0, 90, 0)))

    # Index holes, one per PERMITTED pitch position. Nothing outside the Sonos
    # range can be drilled because nothing outside it is in the list.
    for p in d.pitch_positions_deg:
        a = radians(p - 90.0)
        iy = hinge_y + R.PITCH_PLATE_R * 0.42 * cos(a)
        iz = hinge_z + R.PITCH_PLATE_R * 0.42 * sin(a)
        solid = solid - (Pos(0, iy, iz) * Cylinder(
            radius=index_bore / 2.0,
            height=PLATE_GAP + 4 * FORK_PLATE_T + 10.0,
            align=(Align.CENTER, Align.CENTER, Align.CENTER), rotation=(0, 90, 0)))

    # --- Tether lug -------------------------------------------------------
    # The tether has to catch the speaker WITH THE CLAMP FULLY OPEN. That rules out
    # anchoring both ends to the clamp: if the shells release and slide off the
    # pole, a clamp-to-cradle tether goes down with them.
    #
    # So the cable's upper end loops the POLE ITSELF, above the clamp, and its
    # lower end shackles here — on the cradle, which is the thing that must not
    # fall. The lug on the clamp shell is a captive keeper for the slack, not the
    # load path. See docs/TETHER_SPEC.md.
    lug = Cylinder(radius=7.0, height=9.0,
                   align=(Align.CENTER, Align.CENTER, Align.MIN))
    lug -= Cylinder(radius=3.0, height=27.0,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                    rotation=(0, 90, 0))
    solid = solid + (Pos(0, B.SPIGOT_D / 2.0 + 4.0,
                         root_z + R.BOOM_H_ROOT - 9.0) * lug)

    return solid


if __name__ == "__main__":
    d = D.compute()
    print(f"spigot {B.SPIGOT_D:.0f} mm, reach {d.boom_reach:.1f} mm "
          f"(collar axis already {d.collar_axis_offset:.1f} mm off the pole)")
    print(f"carries {d.load_n:.1f} N at {d.boom_length:.1f} mm from the pole axis "
          f"= {d.overturning_moment_nmm/1000:.2f} N*m")
    print(f"pitch holes: {', '.join(f'{p:+.0f}' for p in d.pitch_positions_deg)} deg")
    print("PRINT LONG AXIS FLAT — never standing up")
    raise SystemExit(_base.cli(build, NAME, MATERIAL))
