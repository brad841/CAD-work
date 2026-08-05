#!/usr/bin/env python3
"""
Gate 0 validator. Run before anything else.

Exit 0  — Gate 0 is closed, every measurement present, derived values sane.
           Geometry generation is permitted.
Exit 1  — Gate 0 is open. Prints exactly what is still missing and how to get it.
Exit 2  — Gate 0 is closed but a derived value is out of range, meaning a
           measurement is present but implausible. This catches unit slips
           (inches typed where millimetres belong) rather than trusting them.

This script exists so the gate is enforced by the build, not by discipline.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from params import clearances as C  # noqa: E402
from params import derived as D  # noqa: E402
from params import gate0 as G  # noqa: E402


def main() -> int:
    missing = G.missing()
    total = len(G._GATE0_FIELDS)

    print("=" * 68)
    print("GATE 0 VALIDATOR — Sonos Move 2 pole mount")
    print("=" * 68)

    if missing:
        print(f"\nSTATUS: BLOCKED — {len(missing)} of {total} measurements missing.\n")
        print("Geometry generation is refused. Missing fields:\n")
        for f in missing:
            note = getattr(G, f).note
            print(f"  [ ] {f}")
            if note:
                print(f"        {note}")
        print("\nHow to produce these numbers:")
        print("  docs/GATE0_MEASUREMENT_PROTOCOL.md")
        print("\nWhere to put them (this is the only file you edit):")
        print("  params/gate0.py")
        print()
        return 1

    print(f"\nSTATUS: measurements complete ({total}/{total}). Checking plausibility.\n")

    d = D.compute()
    problems: list[str] = []

    # Unit-slip and sanity traps. A 2.5 in pole is ~63.5 mm; anything near 2.5
    # means inches were typed into a millimetre field.
    if not (50.0 <= d.pole_od_nominal <= 80.0):
        problems.append(
            f"pole_od_nominal = {d.pole_od_nominal:.2f} mm. A 2.5 in pole should be "
            f"~62-65 mm. Check for an inch value typed into a millimetre field."
        )
    if d.pole_ovality > 3.0:
        problems.append(
            f"pole_ovality = {d.pole_ovality:.2f} mm. That is a lot. Re-measure; if "
            f"real, the liner preload (LINER_TO_POLE) needs revisiting before any "
            f"geometry is trusted."
        )
    if not (0.8 <= float(G.POLE_WALL_T) <= 4.0):
        problems.append(
            f"POLE_WALL_T = {float(G.POLE_WALL_T):.2f} mm is outside the plausible "
            f"range for tent pole tube."
        )
    if not (30.0 <= float(G.COM_OFFSET_Z) <= 200.0):
        problems.append(
            f"COM_OFFSET_Z = {float(G.COM_OFFSET_Z):.1f} mm. For a 241 mm tall "
            f"speaker the CoM should sit well inside that height."
        )
    if float(G.HANDLE_RECESS_D) < 5.0:
        problems.append(
            f"HANDLE_RECESS_D = {float(G.HANDLE_RECESS_D):.1f} mm is too shallow for "
            f"the anti-tip hook to engage in shear. Re-measure to the deepest point."
        )
    if d.bayonet_stack_loose > 0.8:
        problems.append(
            f"Worst-case loose bayonet stack = {d.bayonet_stack_loose:.2f} mm. Above "
            f"0.8 mm the docked speaker will visibly nod. Tighten clearances.py."
        )

    print("  Derived load path")
    print(f"    suspended load             {d.load_n:.1f} N ({G.SUSPENDED_MASS/1000:.2f} kg)")
    print(f"    boom length to CoM         {d.boom_length:.1f} mm")
    print(f"    overturning moment         {d.overturning_moment_nmm/1000:.1f} N*m")
    print(f"    clamp couple force         {d.clamp_couple_n:.0f} N")
    print(f"    clamp band height          {d.clamp_band_height:.1f} mm")
    print("  Pole envelope")
    print(f"    OD min / nominal / max     {d.pole_od_min:.2f} / {d.pole_od_nominal:.2f} / {d.pole_od_max:.2f} mm")
    print(f"    ovality                    {d.pole_ovality:.2f} mm")
    print(f"    shell bore                 {d.shell_bore_d:.2f} mm")
    print("  Bayonet stack, worst case")
    print(f"    loose                      {d.bayonet_stack_loose:+.2f} mm")
    print(f"    tight                      {d.bayonet_stack_tight:+.2f} mm")
    print("  Pitch index positions")
    print(f"    {', '.join(f'{p:+.0f}' for p in d.pitch_positions_deg)} deg "
          f"(Sonos limit: {-G.PITCH_LIMIT_DOWN:+.0f} to {G.PITCH_LIMIT_UP:+.0f})")

    print("\n  Clearances still owed a coupon print:")
    for name in C.VERIFY_BEFORE_COMMIT:
        print(f"    {name} = {getattr(C, name):+.2f} mm")

    if problems:
        print(f"\nSTATUS: FAILED PLAUSIBILITY — {len(problems)} issue(s).\n")
        for p in problems:
            print(f"  !! {p}")
        print()
        return 2

    print("\nSTATUS: PASS. Gate 0 closed. Geometry generation permitted.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
