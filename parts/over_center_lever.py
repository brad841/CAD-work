"""
OVER-CENTRE LEVER — the visible jewelry, and a TRANSIENT member.

Pivots on the fixed shell's ears. A crank behind the pivot carries the steel link
to the swing shell's catch pin. Closing swings the crank through dead centre and
7 deg past it, so link tension then pulls the lever hard against its closed stop:
the load holds the lever shut, and opening it requires first INCREASING tension.
Nothing threaded, nothing to vibrate loose.

Load duration matters here and is why this part is not sized like the link. The
lever is loaded only while you close it — once over centre it rests on its stop
and carries almost nothing. So short-term yield governs, not creep: 60 N at the
tip gives 7.6 MPa against a 22.5 MPa transient allowable (2x on yield). The link,
by contrast, holds 172 N forever, which is why it is steel.

The blade is slotted down its centreline so the steel link runs INSIDE it. That
keeps the mechanism symmetric about the blade's midplane, so the pivot pin sees
pure double shear and no couple. It also hides the link when closed, which is
what makes the closed clamp read as one object rather than a linkage.

Print: blade flat on the plate, pivot axis vertical. Bending is then in-plane,
and the face against the glass becomes the show face.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Box, Cylinder, Part, Pos, Rot  # noqa: E402

from params import clamp as L  # noqa: E402
from params import clearances as C  # noqa: E402
from params import derived as D  # noqa: E402
from params import lever as V  # noqa: E402
from parts import _base  # noqa: E402

NAME = "over_center_lever"
MATERIAL = "PETG"


def build() -> Part:
    w = V.BLADE_W
    pivot_bore = L.LEVER_PIVOT_D + C.LEVER_PIN_TO_BORE
    crank_bore = V.LINK_PIN_D + C.LEVER_PIN_TO_BORE

    # Pivot boss at the origin.
    solid = Cylinder(radius=V.PIVOT_BOSS_R, height=w,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))

    # Arm out to the tip, waisted for the eye and for mass.
    arm = Box(V.ARM_LEN, V.BLADE_WAIST, w,
              align=(Align.MIN, Align.CENTER, Align.MIN))
    solid = solid + arm
    solid = solid + (Pos(V.ARM_LEN, 0, 0) * Cylinder(
        radius=V.TIP_R, height=w, align=(Align.CENTER, Align.CENTER, Align.MIN)))

    # Crank boss behind the pivot. Directly opposite the arm, so the crank pin
    # sweeps through the pivot-catch line as the arm comes down.
    solid = solid + (Pos(-V.CRANK_R, 0, 0) * Cylinder(
        radius=V.LINK_END_R, height=w, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    # Fair the crank boss into the pivot boss.
    solid = solid + (Pos(-V.CRANK_R, 0, 0) * Box(
        V.CRANK_R, V.LINK_END_R * 1.6, w,
        align=(Align.MIN, Align.CENTER, Align.MIN)))

    # Thumb scallop on the arm's outer edge — concave, so the hand knows which
    # way to pull without looking. Chamfers where a hand goes (rubric item 6).
    scallop = Cylinder(radius=V.GRIP_SCALLOP_R, height=w * 3,
                       align=(Align.CENTER, Align.CENTER, Align.CENTER))
    solid = solid - (Pos(V.ARM_LEN * 0.62,
                         V.BLADE_WAIST / 2.0 + V.GRIP_SCALLOP_R - 2.2, w / 2.0)
                     * scallop)

    # Central slot for the steel link, open toward the crank end.
    slot = Box(V.LINK_SLOT_DEPTH, V.LINK_SLOT_W, w * 3,
               align=(Align.MAX, Align.CENTER, Align.CENTER))
    solid = solid - (Pos(V.PIVOT_BOSS_R * 0.4, 0, w / 2.0) * slot)

    # Bores last, so the slot cannot leave a sliver in either.
    solid = solid - Cylinder(radius=pivot_bore / 2.0, height=w * 3,
                             align=(Align.CENTER, Align.CENTER, Align.CENTER))
    solid = solid - (Pos(-V.CRANK_R, 0, w / 2.0) * Cylinder(
        radius=crank_bore / 2.0, height=w * 3,
        align=(Align.CENTER, Align.CENTER, Align.CENTER)))

    # Hand chamfer on the two large faces of the arm and tip.
    try:
        faces_z = [e for e in solid.edges()
                   if abs(e.center().Z) < 0.01 or abs(e.center().Z - w) < 0.01]
        outer = [e for e in faces_z if e.center().X > V.ARM_LEN * 0.25]
        if outer:
            solid = solid.chamfer(length=V.HAND_CHAMFER, length2=None,
                                  edge_list=outer)
    except Exception:  # noqa: BLE001
        print("  note: hand chamfer skipped (edge selection rejected)")

    return solid


if __name__ == "__main__":
    d = D.compute()
    print(f"arm {V.ARM_LEN:.0f} mm on a {V.CRANK_R:.0f} mm crank = "
          f"{V.mechanical_advantage():.1f}x advantage")
    print(f"hand force for {d.link_tension_n:.0f} N link tension: "
          f"{V.hand_force_for_preload(d.link_tension_n):.0f} N")
    print(f"capacity at a 60 N hand: {V.link_tension_capacity(60.0):.0f} N "
          f"(need {d.link_tension_n:.0f} N)")
    print(f"pivot-to-catch {V.pivot_to_catch():.2f} mm, "
          f"link {V.link_length():.2f} mm, {V.OVER_TRAVEL_DEG:.0f} deg past centre")
    raise SystemExit(_base.cli(build, NAME, MATERIAL))
