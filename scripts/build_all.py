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
    "over_center_lever",
    "lever_link",
    "bayonet_collar",
    "cradle_boom",
    "tray",
    "rear_handle_hook",
    "hook_nose",
    "usbc_retainer",
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

# Shims are pick-what-fits from the printed set, not all three at once. Counted
# separately so the budget is not inflated by two shims that will never be used.
SHIM_PREFIX = "pole_shim"

# Not printed. Steel hardware whose STEP is a cutting profile, so it does not
# count against a PRINTED mass budget — but it is reported so the total mass of
# the thing hanging on the pole is still visible.
NOT_PRINTED = {"lever_link"}


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
    steel_mass = sum(r.mass_g for r in reports if r.name in NOT_PRINTED)
    shims = [r for r in reports if r.name.startswith(SHIM_PREFIX)]
    shim_all = sum(r.mass_g for r in shims)
    shim_worst = max((r.mass_g for r in shims), default=0.0) * 1.0
    mount_mass = total - coupon_mass - steel_mass - shim_all + shim_worst
    print(f"  {'of which coupons':<24} {'':<9} {coupon_mass:>7.1f} g  (consumable)")
    print(f"  {'of which steel (not printed)':<24} {'':<9} {steel_mass:>7.1f} g")
    print(f"  {'shims: worst single stack':<24} {'':<9} {shim_worst:>7.1f} g  "
          f"(of {shim_all:.1f} g printed as a set)")
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
