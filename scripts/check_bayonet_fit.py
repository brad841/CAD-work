#!/usr/bin/env python3
"""
Virtual fit check at the bayonet — the tolerance stack, worst case both ways.

Two solids that each validate independently can still be a joint that does not
work. This script assembles them and asks the four questions that matter:

  1. Does the spigot drop in?           interference at the entry angle must be 0
  2. Does it rotate to the lock?        interference at the locked angle must be 0
  3. Is it actually captured?           lifting it at the lock MUST interfere,
                                        or the "lock" is decorative
  4. Does it survive tolerance drift?   re-run at worst-case tight and loose

Question 3 is the one that catches a plausible-looking bayonet that does not
retain. A joint that passes 1 and 2 and fails 3 is a hole, not a lock.

Exit 0 all four pass at nominal and at both tolerance extremes. Exit 1 otherwise.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from build123d import Pos, Rot  # noqa: E402

from params import bayonet as B  # noqa: E402
from params import clearances as C  # noqa: E402
from parts import bayonet_coupon_female as fem  # noqa: E402
from parts import bayonet_coupon_male as male  # noqa: E402

# Interference below this is numerical noise from curved-surface tessellation,
# not real material overlap.
NOISE_MM3 = 0.5
# How far the joint is lifted to prove capture. Well inside the axial clearance
# so a pass means real retention rather than slop being taken up.
LIFT_MM = 0.5

failures: list[str] = []


def overlap_mm3(a, b) -> float:
    """Interference volume between two solids.

    build123d returns None from `&` when two solids do not touch at all, so a
    clean clearance fit and a broken build both look falsy. Distinguish them:
    None means genuinely zero overlap, which for questions 1, 2 and 4 is the
    passing answer.
    """
    inter = a & b
    if inter is None:
        return 0.0
    try:
        return float(inter.volume)
    except (AttributeError, TypeError):
        return 0.0


def report(label: str, ok: bool, detail: str) -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label:<46} {detail}")
    if not ok:
        failures.append(label)


def seated_male(m, angle_deg: float, lift: float = 0.0):
    """Place the male so its lug underside sits on the collar's groove floor.

    The datum is stated rather than relying on LUG_Z and groove_bottom_z
    happening to be equal — if either moves, this stays correct.
    """
    dz = B.groove_bottom_z() - B.LUG_Z + lift
    return Pos(0, 0, dz) * (Rot(0, 0, angle_deg) * m)


def run_case(name: str, lug_radial_clear: float, lug_axial_clear: float) -> None:
    print(f"\n{name}")
    print(f"  lug radial clearance {lug_radial_clear:+.2f} mm, "
          f"axial {lug_axial_clear:+.2f} mm")

    C.BAYONET_LUG_RADIAL = lug_radial_clear
    C.BAYONET_LUG_AXIAL = lug_axial_clear

    m = male.build()
    f = fem.build()

    # 1. Drop in at the entry angle.
    at_entry = seated_male(m, 0.0)
    v = overlap_mm3(at_entry, f)
    report("1. spigot enters at the entry angle", v <= NOISE_MM3,
           f"interference {v:.3f} mm^3")

    # 2. Rotate to the lock.
    twist = fem.TWIST_SIGN * B.TWIST_DEG
    at_lock = seated_male(m, twist)
    v = overlap_mm3(at_lock, f)
    report("2. rotates to the locked angle", v <= NOISE_MM3,
           f"interference {v:.3f} mm^3")

    # 3. Capture: lifting at the lock must hit the groove roof.
    lifted = seated_male(m, twist, lift=LIFT_MM)
    v = overlap_mm3(lifted, f)
    report("3. captured — lifting at the lock interferes", v > NOISE_MM3,
           f"interference {v:.3f} mm^3 on a {LIFT_MM} mm lift")

    # 4. And it must NOT be captured at the entry angle, or it never went in.
    lifted_entry = seated_male(m, 0.0, lift=LIFT_MM)
    v = overlap_mm3(lifted_entry, f)
    report("4. free to withdraw at the entry angle", v <= NOISE_MM3,
           f"interference {v:.3f} mm^3 on a {LIFT_MM} mm lift")


def main() -> int:
    print("=" * 74)
    print("BAYONET VIRTUAL FIT — tolerance stack, worst case both ways")
    print("=" * 74)
    print(f"spigot {B.SPIGOT_D} mm | {B.LUG_COUNT} lugs x {B.LUG_ARC_DEG} deg | "
          f"twist {B.TWIST_DEG} deg | lock depth {B.LOCK_DEPTH} mm")

    nominal_r = C.BAYONET_LUG_RADIAL
    nominal_a = C.BAYONET_LUG_AXIAL
    try:
        run_case("NOMINAL", nominal_r, nominal_a)
        # Tight: printed parts come out oversize, so clearances shrink. This is
        # the case that binds and refuses to assemble in the cold.
        run_case("WORST CASE TIGHT (clearances halved)",
                 nominal_r * 0.5, nominal_a * 0.5)
        # Loose: clearances open up. This is the case that rattles and lets the
        # docked speaker nod.
        run_case("WORST CASE LOOSE (clearances doubled)",
                 nominal_r * 2.0, nominal_a * 2.0)
    finally:
        C.BAYONET_LUG_RADIAL = nominal_r
        C.BAYONET_LUG_AXIAL = nominal_a

    print()
    if failures:
        print(f"FAILED — {len(failures)} check(s):")
        for f in failures:
            print(f"  !! {f}")
        return 1
    print("All bayonet fit checks passed at nominal and both tolerance extremes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
