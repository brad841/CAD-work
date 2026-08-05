"""
HOOK NOSE — TPU. The compliant face that meets the moulded handle lip.

Small, cheap, and the reason the hook works without knowing the lip radius. TPU
conforms to whatever radius is actually there, spreads the shear over the contact
patch instead of concentrating it on a printed edge, and will not scuff the
moulding the way a rigid PETG nose would.

Loaded in compression and shear only. Never in tension — if this part is being
pulled, something upstream has already failed and the tether is what matters.

Press-fits into the hook bracket's pocket with the named liner-style interference.
No adhesive: it has to be replaceable when it eventually takes a set.

Print: profile flat on the plate.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Box, Part, Pos  # noqa: E402

from params import clearances as C  # noqa: E402
from params import cradle as R  # noqa: E402
from parts import _base  # noqa: E402
from parts.rear_handle_hook import NOSE_POCKET_DEPTH  # noqa: E402

NAME = "hook_nose"
MATERIAL = "TPU 95A"

BEAD_R = 1.6      # proud bead that actually touches the lip


def build() -> Part:
    # Matches the hook's pocket, with a slight interference so it stays put.
    w = R.HOOK_POST_W - 6.0 + abs(C.LINER_TO_SHELL_POCKET)
    d = R.HOOK_NOSE_REACH - 3.0 + abs(C.LINER_TO_SHELL_POCKET)

    solid = Box(w, d, NOSE_POCKET_DEPTH,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
    # Contact bead standing proud of the pocket face.
    bead = Box(w, d * 0.55, BEAD_R,
               align=(Align.CENTER, Align.MIN, Align.MIN))
    solid = solid + (Pos(0, -d / 2.0, NOSE_POCKET_DEPTH) * bead)
    return solid


if __name__ == "__main__":
    print(f"TPU nose {R.HOOK_POST_W-6:.0f} x {R.HOOK_NOSE_REACH-3:.0f} mm, "
          f"{abs(C.LINER_TO_SHELL_POCKET):.2f} mm press-fit, no adhesive")
    print(f"conforms to the lip radius, which is unpublished")
    raise SystemExit(_base.cli(build, NAME, MATERIAL))
