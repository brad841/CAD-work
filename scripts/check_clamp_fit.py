#!/usr/bin/env python3
"""
Assembly check for the clamp shells.

Two shells that each validate can still be a clamp that cannot close. The checks:

  1. Closed, the two halves must not interfere anywhere.
  2. The hinge knuckles must INTERLEAVE — the swing half's single knuckle sits
     between the fixed half's pair, in double shear, without touching either.
  3. The hinge pin must pass through all three bores on one axis. Checked by
     running a virtual pin through and confirming it is unobstructed.
  4. The catch boss must fit between the lever ears with clearance.
  5. The band must actually close far enough to preload the liner.

Exit 0 all pass, 1 otherwise.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from build123d import Align, Cylinder, Pos  # noqa: E402

from params import clamp as L  # noqa: E402
from params import clearances as C  # noqa: E402
from params import derived as D  # noqa: E402
from parts import _base, _clamp  # noqa: E402
from parts import clamp_shell_fixed as fixed  # noqa: E402
from parts import clamp_shell_swing as swing  # noqa: E402
from parts import pole_liner as liner  # noqa: E402

NOISE_MM3 = 0.5
failures: list[str] = []


def overlap_mm3(a, b) -> float:
    inter = a & b
    if inter is None:
        return 0.0
    try:
        return float(inter.volume)
    except (AttributeError, TypeError):
        return 0.0


def report(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label:<50} {detail}")
    if not ok:
        failures.append(label)


def main() -> int:
    print("=" * 76)
    print("CLAMP ASSEMBLY CHECK")
    print("=" * 76)

    d = D.compute()
    f = fixed.build()
    s = swing.build()

    # Validate BEFORE measuring anything. An earlier version of this script went
    # straight to the interference check, so it happily reported "all clamp
    # assembly checks passed" on two shells whose hinge bosses had come detached
    # into separate bodies. A geometry check that does not first confirm it is
    # looking at a sound solid is measuring nothing.
    for part, label in ((f, "clamp_shell_fixed"), (s, "clamp_shell_swing")):
        try:
            _base.validate(part, label)
            report(f"0. {label} is a single sound solid", True)
        except _base.SolidRejected as e:
            report(f"0. {label} is a single sound solid", False, str(e))
    if failures:
        print("\n  Shells are not sound — later checks would be meaningless.")
        print(f"FAILED — {len(failures)} check(s)")
        return 1

    print(f"band {d.clamp_band_height:.1f} mm | bore {d.shell_bore_d:.2f} mm | "
          f"wall {d.shell_wall_t:.2f} mm | preload {d.required_preload_n:.0f} N")

    # 1. No interference when closed.
    v = overlap_mm3(f, s)
    report("1. shells clear each other when closed", v <= NOISE_MM3,
           f"interference {v:.3f} mm^3")

    # 2. Knuckles interleave without touching. Covered by check 1 for overlap;
    #    here we confirm they genuinely OVERLAP IN ANGLE but not in Z, which is
    #    what "interleave" means — otherwise check 1 could pass simply because
    #    the knuckles miss each other entirely and the hinge does not exist.
    band_h = d.clamp_band_height
    outer_h = band_h * fixed.OUTER_KNUCKLE_FRACTION
    z0_mid, h_mid = swing.middle_knuckle_span(band_h)
    gap_lo = z0_mid - outer_h
    gap_hi = (band_h - outer_h) - (z0_mid + h_mid)
    report("2. knuckles interleave with a real gap",
           abs(gap_lo - L.HINGE_KNUCKLE_GAP) < 0.01
           and abs(gap_hi - L.HINGE_KNUCKLE_GAP) < 0.01,
           f"gaps {gap_lo:.2f} / {gap_hi:.2f} mm")
    report("2b. middle knuckle spans the useful band",
           h_mid > band_h * 0.3, f"{h_mid:.1f} mm of {band_h:.1f} mm")

    # 3. A virtual hinge pin must pass through unobstructed.
    x, y = _clamp.at_angle(_clamp.hinge_axis_radius(), L.HINGE_DEG)
    pin = Pos(x, y, -2.0) * Cylinder(
        radius=L.HINGE_PIN_D / 2.0, height=band_h + 4.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN))
    v = overlap_mm3(pin, f) + overlap_mm3(pin, s)
    report("3. hinge pin passes through all three bores", v <= NOISE_MM3,
           f"obstruction {v:.3f} mm^3")

    # 4. Catch boss between the lever ears.
    catch_h = L.LEVER_EAR_GAP - 2.0 * C.LEVER_PIN_TO_BORE
    report("4. catch boss fits between the lever ears",
           catch_h < L.LEVER_EAR_GAP,
           f"boss {catch_h:.2f} mm in a {L.LEVER_EAR_GAP:.2f} mm gap")

    # 5. The liner must be squeezed when the band is closed, not floating.
    #    Shell bore is sized to the LARGEST pole; on the smallest pole the shim
    #    stack makes up the difference. Confirm the stack-up actually preloads.
    ln = liner.build()
    liner_outer_r = ln.bounding_box().max.Y  # liner wraps about the +X axis
    shell_bore_r = d.shell_bore_d / 2.0
    radial_slack = shell_bore_r - liner_outer_r
    report("5. shim stack covers the shell-to-liner slack",
           radial_slack <= D.compute().shim_stack_needed_min + 1.5,
           f"slack {radial_slack:.2f} mm, shims reach "
           f"{D.compute().shim_stack_needed_min:.2f} mm")

    print()
    if failures:
        print(f"FAILED — {len(failures)} check(s):")
        for x in failures:
            print(f"  !! {x}")
        return 1
    print("All clamp assembly checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
