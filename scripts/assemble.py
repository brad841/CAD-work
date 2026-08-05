#!/usr/bin/env python3
"""
Place every part in its assembled position and export the merged STEP.

Also the assembly interference check: parts that each validate can still collide,
and the only way to know is to put them where they actually go and look.

The placement here is the single source of truth for where things are relative to
one another, so the gauntlet and the view renderer both import it rather than
re-deriving positions and drifting.

Exit 0 if the assembly is clash-free, 1 otherwise.
"""

from __future__ import annotations

import sys
from math import cos, radians, sin
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from build123d import Compound, Pos, Rot, export_step  # noqa: E402

from params import bayonet as BY  # noqa: E402
from params import clamp as L  # noqa: E402
from params import cradle as R  # noqa: E402
from params import derived as D  # noqa: E402
from params import gate0 as G  # noqa: E402
from params import lever as V  # noqa: E402
from parts import _base, _clamp  # noqa: E402
from parts import bayonet_collar, clamp_shell_fixed, clamp_shell_swing  # noqa: E402
from parts import cradle_boom, hook_nose, lever_link, over_center_lever  # noqa: E402
from parts import pole_liner, rear_handle_hook, tray, usbc_retainer  # noqa: E402

# World frame: pole axis is Z at the origin, band bottom at z = 0.
# +Y aft (behind the pole), -Y forward (where the speaker goes).

NOISE_MM3 = 1.0


def placed() -> dict:
    """Every part in its assembled position, keyed by name."""
    d = D.compute()
    band_h = d.clamp_band_height
    out: dict = {}

    out["clamp_shell_fixed"] = clamp_shell_fixed.build()
    out["clamp_shell_swing"] = clamp_shell_swing.build()

    # Liners: one per shell, rotated onto each shell's centre. Built about +X, so
    # rotate by the shell centre angle.
    liner = pole_liner.build()
    out["pole_liner_fixed"] = Rot(0, 0, L.FIXED_CENTRE_DEG) * liner
    out["pole_liner_swing"] = Rot(0, 0, L.SWING_CENTRE_DEG) * liner

    # Lever: pivots on the SWING shell's ears. Its crank points at the catch, so
    # the arm points 180 deg from that — derived, not eyeballed, because getting it
    # wrong is what put the arm inside the collar.
    import math
    lx, ly = _clamp.at_angle(_clamp.lever_axis_radius(), L.LEVER_PIVOT_DEG)
    cx, cy = _clamp.at_angle(_clamp.lever_axis_radius(), L.CATCH_DEG)
    crank_dir = math.degrees(math.atan2(cy - ly, cx - lx))
    arm_dir = crank_dir + 180.0

    lever = over_center_lever.build()
    lever = Rot(0, 0, arm_dir) * lever
    out["over_center_lever"] = Pos(lx, ly, band_h / 2.0 - V.BLADE_W / 2.0) * lever

    # Link: shown at DEAD CENTRE — crank pin on the pivot-catch line. The locked
    # position is 7 deg past this; dead centre is the geometrically exact place to
    # draw a straight two-pin link, and it is also the worst case for clearance.
    link = lever_link.build()
    out["lever_link"] = Pos(
        lx + V.CRANK_R * math.cos(math.radians(crank_dir)),
        ly + V.CRANK_R * math.sin(math.radians(crank_dir)),
        band_h / 2.0 - V.LINK_T / 2.0) * (Rot(0, 0, crank_dir) * link)

    # Collar: bolts to the fixed shell's pad at BOOM_DEG, flange facing the pad.
    collar = bayonet_collar.build()
    collar = Rot(0, 0, L.BOOM_DEG + 90.0) * collar
    out["bayonet_collar"] = Pos(
        0, -d.collar_axis_offset, band_h / 2.0 - BY.COLLAR_H / 2.0) * collar

    # Cradle: spigot down into the collar. The boom's spigot is modelled pointing
    # UP out of the arm, so flip it and drop it in to the lock datum.
    # NOT flipped. The spigot enters the collar from ABOVE, so the arm has to sit
    # ABOVE the collar. Flipping the part put the spigot pointing down but left the
    # arm hanging below the collar — which would require the spigot to pass through
    # the collar to reach it. The build already has the spigot below the arm, which
    # is exactly the top-entry arrangement.
    boom = cradle_boom.build()
    collar_z0 = band_h / 2.0 - BY.COLLAR_H / 2.0
    groove_floor_z = collar_z0 + BY.groove_bottom_z()
    boom_z = groove_floor_z - BY.LUG_Z          # puts the lugs on the groove floor
    out["cradle_boom"] = Pos(0, -d.collar_axis_offset, boom_z) * boom

    # Tray: on the boom's fork, forward of and above the collar axis.
    tr = tray.build()
    tray_y = -(d.collar_axis_offset + d.boom_reach)
    fork_z = boom_z + cradle_boom.SPIGOT_H + R.BOOM_H_TIP / 2.0
    tray_z = fork_z + R.LUG_HINGE_DROP      # aligns the two hinge bores
    out["tray"] = Pos(0, tray_y, tray_z) * tr

    # Hook: clamps to the tray's aft mount, rising behind the speaker.
    hk = rear_handle_hook.build()
    hook_y = tray_y + R.tray_d() / 2.0 + R.HOOK_POST_T / 2.0 + 2.0
    out["rear_handle_hook"] = Pos(0, hook_y, tray_z) * hk

    nose = hook_nose.build()
    out["hook_nose"] = Pos(
        0, hook_y - R.HOOK_POST_T / 2.0 - R.HOOK_NOSE_REACH / 2.0,
        tray_z + R.hook_post_h() - R.HOOK_NOSE_H) * nose

    # Module B retainer: on the tray's aft mount, beside the hook.
    # Retainer sits at the speaker's rear face, plug pointing forward into the
    # USB-C port, offset sideways so it does not fight the hook post.
    ret = usbc_retainer.build()
    out["usbc_retainer"] = Pos(
        R.HOOK_POST_W / 2.0 + 20.0,
        tray_y + G.SPEAKER_D / 2.0 + 5.0,
        tray_z + 4.0) * ret

    return out


def overlap_mm3(a, b) -> float:
    try:
        inter = a & b
    except ValueError:
        return 0.0
    if inter is None:
        return 0.0
    try:
        if not inter.solids():
            return 0.0
        return float(inter.volume)
    except (AttributeError, TypeError):
        return 0.0


# Pairs allowed to touch, with the reason. Everything else must be clear.
ALLOWED_CONTACT = {
    frozenset({"clamp_shell_fixed", "pole_liner_fixed"}): "liner sits in the shell pocket",
    frozenset({"clamp_shell_swing", "pole_liner_swing"}): "liner sits in the shell pocket",
    frozenset({"clamp_shell_swing", "over_center_lever"}): "lever pivots on the ears",
    frozenset({"over_center_lever", "lever_link"}): "link runs in the blade slot",
    frozenset({"clamp_shell_fixed", "lever_link"}): "link hooks the catch pin",
    frozenset({"clamp_shell_fixed", "bayonet_collar"}): "collar bolts to the pad",
    frozenset({"bayonet_collar", "cradle_boom"}): "bayonet lugs bear on the groove floor",
    frozenset({"cradle_boom", "tray"}): "pitch fork straddles the tray lug",
    frozenset({"tray", "rear_handle_hook"}): "hook clamps to the tray mount",
    frozenset({"rear_handle_hook", "hook_nose"}): "nose press-fits into the bracket",
    frozenset({"tray", "usbc_retainer"}): "retainer bolts to the tray mount",
}


def main() -> int:
    print("=" * 76)
    print("ASSEMBLY — placement, clash check, merged STEP")
    print("=" * 76)

    parts = placed()
    problems: list[str] = []

    for name, solid in parts.items():
        try:
            _base.validate(solid, name)
        except _base.SolidRejected as e:
            problems.append(str(e))

    names = list(parts)
    clashes = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            v = overlap_mm3(parts[a], parts[b])
            if v <= NOISE_MM3:
                continue
            key = frozenset({a, b})
            if key in ALLOWED_CONTACT:
                print(f"  contact  {a} / {b}: {v:8.1f} mm^3  ({ALLOWED_CONTACT[key]})")
            else:
                clashes.append((a, b, v))

    print()
    for a, b, v in clashes:
        print(f"  CLASH    {a} / {b}: {v:.1f} mm^3 — not an expected contact")
        problems.append(f"clash {a}/{b}")

    merged = Compound(children=list(parts.values()))
    _base.OUT.mkdir(exist_ok=True)
    step = _base.OUT / "assembly.step"
    export_step(merged, str(step))
    bb = merged.bounding_box()
    print(f"\n  merged assembly: {len(parts)} bodies, envelope "
          f"{bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm")
    print(f"  -> {step.relative_to(ROOT)}")

    if problems:
        print(f"\nFAILED — {len(problems)} problem(s)")
        for p in problems[:12]:
            print(f"  !! {p}")
        return 1
    print("\nAssembly is clash-free apart from the declared contacts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
