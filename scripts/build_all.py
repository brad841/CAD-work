#!/usr/bin/env python3
"""
Build every part, validate each, report mass against the budget.

One module per part, each regenerable in isolation — this driver only collects
them. A part that fails validation fails the build; there is no "mostly built"
state, because a merged assembly is only as watertight as its worst member.

Exit 0 every part built and validated. Exit 1 otherwise.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from params import gate0 as G  # noqa: E402
from parts import _base  # noqa: E402

# Ordered by how they get built and tested, not alphabetically. Coupons first —
# they are the physical gate and nothing downstream is worth printing until
# they fit the actual pole.
PART_MODULES = [
    "pole_gauge_coupon",
    "bayonet_coupon_male",
    "bayonet_coupon_female",
    "pole_liner",
    "clamp_shell_fixed",
    "clamp_shell_swing",
]

# Parts generated as a set from one module, with a per-variant argument.
PART_SETS = [
    ("pole_shim", [0.5, 1.0, 1.5]),
]

# How many of each go into one finished mount. Mass budget is per MOUNT, so a
# part needed twice must be counted twice — reporting one liner when the clamp
# needs two would understate the build by 36 g.
QTY = {
    "pole_liner": 2,
}


def main() -> int:
    print("=" * 74)
    print("BUILD ALL")
    print("=" * 74)

    reports = []
    failed: list[str] = []

    for mod_name in PART_MODULES:
        try:
            mod = importlib.import_module(f"parts.{mod_name}")
            report = _base.export(mod.build(), mod.NAME, mod.MATERIAL)
            reports.append(report)
            print(f"  ok    {report.line()}")
        except Exception as e:  # noqa: BLE001
            print(f"  FAIL  {mod_name}: {e}")
            failed.append(mod_name)

    for mod_name, variants in PART_SETS:
        try:
            mod = importlib.import_module(f"parts.{mod_name}")
            for v in variants:
                name = f"{mod.NAME}_{str(v).replace('.', 'p')}mm"
                report = _base.export(mod.build(v), name, mod.MATERIAL)
                reports.append(report)
                print(f"  ok    {report.line()}")
        except Exception as e:  # noqa: BLE001
            print(f"  FAIL  {mod_name}: {e}")
            failed.append(mod_name)

    print("-" * 74)
    total = sum(r.mass_g * QTY.get(r.name, 1) for r in reports)
    for name, n in QTY.items():
        if any(r.name == name for r in reports):
            print(f"  note  {name} counted x{n} — that many per mount")
    print(f"  {'TOTAL':<24} {'':<9} {total:>7.1f} g")

    # Coupons are consumables — they are printed, fitted and thrown away, so
    # they do not count against the mount's mass budget. Reported separately
    # rather than quietly excluded.
    coupon_mass = sum(r.mass_g * QTY.get(r.name, 1)
                      for r in reports if "coupon" in r.name)
    mount_mass = total - coupon_mass
    print(f"  {'of which coupons':<24} {'':<9} {coupon_mass:>7.1f} g  (consumable)")
    print(f"  {'mount parts':<24} {'':<9} {mount_mass:>7.1f} g  "
          f"of {G.PRINTED_MASS_BUDGET:.0f} g budget")

    if mount_mass > G.PRINTED_MASS_BUDGET:
        print(f"  !! over budget by {mount_mass - G.PRINTED_MASS_BUDGET:.1f} g")
        failed.append("mass budget")

    print()
    if failed:
        print(f"FAILED — {', '.join(failed)}")
        return 1
    print(f"{len(reports)} part(s) built and validated. "
          f"STEP + STL in out/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
