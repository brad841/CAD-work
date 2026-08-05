"""
REAR HANDLE HOOK — anti-tip, in SHEAR, and adjustable because the recess is unmeasured.

This is the part that exists entirely because the Move 2's handle recess geometry is
not published anywhere. Rather than model a hook to numbers we never got, the hook
stops depending on them:

  - 26 mm wide, comfortably inside any four-finger recess (bounded at 60 mm min).
  - Its nose is a separate TPU part, so it conforms to whatever lip radius is
    actually moulded instead of matching a radius we guessed.
  - Its HEIGHT is set by the installer on a slotted M5 clamp over a 140-205 mm
    range. Engagement becomes something you feel and lock, not something predicted.

Load: 10.6 N of shear at the -20 deg pitch limit, plus whatever a knock adds. Small
— but it is the only thing between a nose-down speaker and walking off the tray, so
it is sized for the knock, not the steady state.

The slot is a SLOT, not a row of holes: a hole ladder would quantise the height to
whatever step we chose, and the whole point is that the right height is unknown.

Print: hook profile flat on the plate. The shear across the nose throat then runs
in-plane rather than across layer boundaries.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Box, Cylinder, Part, Pos  # noqa: E402

from params import cradle as R  # noqa: E402
from params import derived as D  # noqa: E402
from params import gate0 as G  # noqa: E402
from parts import _base  # noqa: E402

NAME = "rear_handle_hook"
MATERIAL = "PETG"

NOSE_POCKET_DEPTH = 3.0     # recess the TPU nose sits in


def build() -> Part:
    post_h = R.hook_post_h()

    # Upright post.
    solid = Box(R.HOOK_POST_W, R.HOOK_POST_T, post_h,
                align=(Align.CENTER, Align.CENTER, Align.MIN))

    # Adjustment slot. Spans the full bounded range of possible lip heights, so
    # any real recess can be reached.
    slot_lo = G.HOOK_HEIGHT_ADJUST_MIN - 12.0
    slot_hi = G.HOOK_HEIGHT_ADJUST_MAX - 12.0
    slot_len = slot_hi - slot_lo
    slot = Box(R.HOOK_SLOT_W, R.HOOK_POST_T * 4, slot_len,
               align=(Align.CENTER, Align.CENTER, Align.MIN))
    solid = solid - (Pos(0, 0, slot_lo) * slot)
    # Round the slot ends so it is not a crack starter at either extreme.
    for z in (slot_lo, slot_lo + slot_len):
        solid = solid - (Pos(0, 0, z) * Cylinder(
            radius=R.HOOK_SLOT_W / 2.0, height=R.HOOK_POST_T * 4,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
            rotation=(90, 0, 0)))

    # Lighten the post to an I-section either side of the slot. A 223 mm solid bar
    # is ~51 g for a member carrying 42 N of knock shear at 96x margin; the flanges
    # do the work and the rest is mass.
    for sy in (-1.0, 1.0):
        flute = Box(R.HOOK_POST_W - 12.0, 2.2, slot_len * 0.92,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))
        solid = solid - (Pos(0, sy * (R.HOOK_POST_T / 2.0 - 1.0),
                             slot_lo + slot_len * 0.04) * flute)

    # Nose bracket at the top, projecting forward (-Y) into the recess.
    nose = Box(R.HOOK_POST_W, R.HOOK_NOSE_REACH, R.HOOK_NOSE_H,
               align=(Align.CENTER, Align.MAX, Align.MAX))
    solid = solid + (Pos(0, -R.HOOK_POST_T / 2.0, post_h) * nose)

    # Gusset under the nose: this is the shear corner, and a square inside corner
    # here is a stress riser exactly where the load turns.
    gus = Box(R.HOOK_POST_W, R.HOOK_NOSE_REACH * 0.8, R.HOOK_NOSE_REACH * 0.8,
              align=(Align.CENTER, Align.MAX, Align.MAX))
    solid = solid + (Pos(0, -R.HOOK_POST_T / 2.0,
                         post_h - R.HOOK_NOSE_H) * gus)

    # Pocket for the TPU nose, on the underside of the bracket — the face that
    # bears up against the moulded lip.
    pocket = Box(R.HOOK_POST_W - 6.0, R.HOOK_NOSE_REACH - 3.0,
                 NOSE_POCKET_DEPTH * 2,
                 align=(Align.CENTER, Align.MAX, Align.CENTER))
    solid = solid - (Pos(0, -R.HOOK_POST_T / 2.0 - 1.5,
                         post_h - R.HOOK_NOSE_H) * pocket)

    return solid


if __name__ == "__main__":
    d = D.compute()
    print(f"post {R.HOOK_POST_W:.0f} x {R.HOOK_POST_T:.0f} mm, "
          f"{R.hook_post_h():.0f} mm tall")
    print(f"adjustable {G.HOOK_HEIGHT_ADJUST_MIN:.0f}-{G.HOOK_HEIGHT_ADJUST_MAX:.0f} mm "
          f"above the tray — the recess height is unpublished")
    print(f"hook {G.HOOK_WIDTH:.0f} mm nominal vs a bounded {G.HANDLE_RECESS_W_MIN:.0f} mm "
          f"minimum recess width")
    print(f"carries {d.worst_hook_shear_n:.1f} N shear at {d.worst_pitch_deg:+.0f} deg")
    raise SystemExit(_base.cli(build, NAME, MATERIAL))
