"""
USB-C RETAINER — MODULE B. Built first, on purpose.

The brief's Module B: a right-angle USB-C plug retainer with strain relief that
breaks the water track BEFORE the plug. It needs none of the six charging-base
measurements, which is exactly why it comes first — Module A cannot be built at
all until someone puts a caliper on the base, and this can.

How it sheds water, which is the whole job:

  - The plug is captured with its cable exit pointing DOWN.
  - Below the capture, the cable is forced around a drip loop. Surface water
    running along the jacket reaches the bottom of that loop and falls off there,
    because gravity beats the jacket's surface tension at the low point.
  - So the water track is broken BELOW the connector. Nothing can track upward
    into the plug without climbing.

That ordering is the requirement. A retainer that clamps the cable above the plug
turns the jacket into a wick pointing straight at the contacts.

Carries no suspended load — only cable sway. So this is a stiffness and
water-shedding part, not a structural one.

Print: plug axis flat on the plate, capture jaws vertical, so the snap fingers'
bending stays in-plane.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Box, Cylinder, Part, Pos  # noqa: E402

from params import clearances as C  # noqa: E402
from params import cradle as R  # noqa: E402
from parts import _base  # noqa: E402

NAME = "usbc_retainer"
MATERIAL = "PETG"

WALL = 3.0
MOUNT_BOLT_D = 5.4
CABLE_D = 4.6
HORN_ROOT = 4.0     # how far the drip horn reaches up into the body


def build() -> Part:
    body_w = R.USBC_BODY_W + 2.0 * WALL
    body_h = R.USBC_BODY_H + WALL
    body_t = R.USBC_BODY_T + 2.0 * WALL

    solid = Box(body_w, body_t, body_h,
                align=(Align.CENTER, Align.CENTER, Align.MIN))

    # Plug cavity, open at the top so the plug drops in and down.
    cav = Box(R.USBC_BODY_W + C.USBC_PLUG_TO_RETAINER,
              R.USBC_BODY_T + C.USBC_PLUG_TO_RETAINER,
              R.USBC_BODY_H + 2.0,
              align=(Align.CENTER, Align.CENTER, Align.MIN))
    solid = solid - (Pos(0, 0, WALL) * cav)

    # Connector shell slot in the front face — the plug's tongue passes through
    # to the speaker's port.
    shell = Box(R.USBC_SHELL_W + C.USBC_PLUG_TO_RETAINER,
                WALL * 4,
                R.USBC_SHELL_T + C.USBC_PLUG_TO_RETAINER,
                align=(Align.CENTER, Align.CENTER, Align.CENTER))
    solid = solid - (Pos(0, -body_t / 2.0, WALL + R.USBC_SHELL_T) * shell)

    # Cable exit, DOWNWARD out of the bottom.
    exit_d = CABLE_D + C.CABLE_CHANNEL_TO_CABLE
    solid = solid - Cylinder(radius=exit_d / 2.0, height=WALL * 6,
                             align=(Align.CENTER, Align.CENTER, Align.CENTER))

    # Drip loop horn: the cable wraps this, so its low point sits BELOW the plug
    # and water leaves there instead of tracking up the jacket.
    horn = Cylinder(radius=R.DRIP_LOOP_R, height=exit_d + 2.0 * WALL,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                    rotation=(0, 90, 0))
    horn -= Cylinder(radius=R.DRIP_LOOP_R - WALL, height=exit_d + 2.0 * WALL + 2,
                     align=(Align.CENTER, Align.CENTER, Align.CENTER),
                     rotation=(0, 90, 0))
    # Keep only the lower half — a full ring would trap the cable permanently.
    keeper = Box(R.DRIP_LOOP_R * 3, R.DRIP_LOOP_R * 3, R.DRIP_LOOP_R * 3,
                 align=(Align.CENTER, Align.CENTER, Align.MAX))
    horn = horn & keeper
    # Overlap the body by HORN_ROOT so the horn is fused, not tangent. Placing it
    # fully below the body left it as a separate solid: a half-ring touching a
    # face on a single plane is a zero-thickness contact, which OCC keeps as two
    # bodies and validation correctly rejects.
    if horn is not None:
        solid = solid + (Pos(0, 0, HORN_ROOT) * horn)

    # Mounting ear, bolts to the tray's aft mount.
    ear = Box(body_w, WALL + 2.0, body_h * 0.6,
              align=(Align.CENTER, Align.MIN, Align.MIN))
    solid = solid + (Pos(0, body_t / 2.0, 0) * ear)
    solid = solid - (Pos(0, body_t / 2.0 + (WALL + 2.0) / 2.0, body_h * 0.3)
                     * Cylinder(radius=MOUNT_BOLT_D / 2.0, height=(WALL + 2.0) * 4,
                                align=(Align.CENTER, Align.CENTER, Align.CENTER),
                                rotation=(90, 0, 0)))
    return solid


if __name__ == "__main__":
    print("MODULE B — needs none of the six charging-base measurements")
    print(f"plug cavity {R.USBC_BODY_W:.0f} x {R.USBC_BODY_T:.0f} x {R.USBC_BODY_H:.0f} mm "
          f"({C.USBC_PLUG_TO_RETAINER:+.2f} mm clearance)")
    print(f"cable exits DOWN, drip loop r{R.DRIP_LOOP_R:.0f} mm breaks the water "
          f"track BELOW the plug")
    raise SystemExit(_base.cli(build, NAME, MATERIAL))
