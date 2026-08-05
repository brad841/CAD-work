#!/usr/bin/env python3
"""
Gate validator.

Exit 0  — core mount is clear to generate. Module A may still be gated; that is
           reported, not fatal.
Exit 1  — a blocking field is open. Names it.
Exit 2  — cleared, but a derived value is out of range or a safety check failed.

The bounds report is not decoration. Every conservative substitute in use is
printed with what it costs, so nobody reads a bound as a measurement six weeks
from now.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from params import clearances as C  # noqa: E402
from params import derived as D  # noqa: E402
from params import gate0 as G  # noqa: E402
from params import material as M  # noqa: E402

# Powder coat marks above roughly this contact pressure. Priority 2 is "does not
# mar the rented pole", so this is a hard check, not a guideline.
POLE_PRESSURE_LIMIT_MPA = 0.60


def main() -> int:
    print("=" * 72)
    print("GATE VALIDATOR — Sonos Move 2 pole mount")
    print("=" * 72)

    core_missing = G.missing("core")
    if core_missing:
        print(f"\nSTATUS: BLOCKED — {len(core_missing)} core field(s) open.\n")
        for f in core_missing:
            print(f"  [ ] {f} — {getattr(G, f).note}")
        return 1

    print("\nCORE: clear to generate.")

    mod_a_missing = G.missing("module_a")
    if mod_a_missing:
        print(f"MODULE A: gated — {len(mod_a_missing)} field(s) need a caliper.")
        for f in mod_a_missing:
            print(f"  [ ] {f} — {getattr(G, f).note}")
        print("  These have no safe direction: a canopy that misses the real base")
        print("  footprint drips on 15 V electronics Sonos rates indoor only.")
        print("  Module B needs none of them and proceeds now.")
    else:
        print("MODULE A: clear to generate.")

    d = D.compute(M.CHOSEN)
    problems: list[str] = []

    print(f"\nMATERIAL: {M.CHOSEN.name}")
    print(f"  allowable in-plane         {M.CHOSEN.allowable_inplane_mpa():.2f} MPa")
    print(f"  allowable interlayer       {M.CHOSEN.allowable_interlayer_mpa():.2f} MPa")
    print(f"  sustained margin           {M.SUSTAINED_MARGIN_REQUIRED:.0f}x at {M.DESIGN_TEMP_C:.0f} C")
    print(f"  wall scale vs ASA          {d.wall_scale:.3f}x")
    print(f"  -> shell wall              {d.shell_wall_t:.2f} mm")
    print(f"  -> boom wall               {d.boom_wall_t:.2f} mm")

    print("\nPOLE — designed as a range, shimmed to fit")
    print(f"  design range               {d.pole_od_min:.1f} - {d.pole_od_max:.1f} mm "
          f"({d.pole_od_min/25.4:.2f} - {d.pole_od_max/25.4:.2f} in)")
    print(f"  shell bore                 {d.shell_bore_d:.2f} mm")
    print(f"  liner thickness            {d.liner_thickness:.2f} mm")
    print(f"  shim needed at min OD      {d.shim_stack_needed_min:.2f} mm radial")
    print(f"  shim set available         {G.SHIM_STACK_MAX:.2f} mm "
          f"({', '.join(f'{t}' for t in G.SHIM_THICKNESSES)})")

    if not d.shim_range_covered:
        problems.append(
            f"Shim set cannot cover the design range: needs "
            f"{d.shim_stack_needed_min:.2f} mm, set provides {G.SHIM_STACK_MAX:.2f} mm."
        )

    print("\nLOAD PATH — at the bounded adverse CoM")
    print(f"  suspended load             {d.load_n:.1f} N ({G.SUSPENDED_MASS/1000:.2f} kg)")
    print(f"  boom length to CoM         {d.boom_length:.1f} mm")
    print(f"  overturning moment         {d.overturning_moment_nmm/1000:.2f} N*m")
    print(f"  clamp band height          {d.clamp_band_height:.1f} mm")
    print(f"  clamp couple force         {d.clamp_couple_n:.0f} N (direct bearing, no friction needed)")
    print(f"  required friction preload  {d.required_preload_n:.0f} N (5x anti-slip, mu={C.LINER_FRICTION_COEFF})")
    print(f"  pole contact area          {d.pole_contact_area_mm2:.0f} mm^2 (at small end of range)")
    print(f"  pole contact pressure      {d.pole_contact_pressure_mpa:.3f} MPa "
          f"(limit {POLE_PRESSURE_LIMIT_MPA:.2f})")

    if d.pole_contact_pressure_mpa > POLE_PRESSURE_LIMIT_MPA:
        problems.append(
            f"Pole contact pressure {d.pole_contact_pressure_mpa:.3f} MPa exceeds "
            f"the {POLE_PRESSURE_LIMIT_MPA:.2f} MPa powder-coat limit. The rented "
            f"pole would mark. Raise clamp_band_height or widen liner wrap."
        )

    print("\nPITCH — clipped to what Sonos permits")
    print(f"  positions                  {', '.join(f'{p:+.0f}' for p in d.pitch_positions_deg)} deg")
    print(f"  Sonos limit                {-G.PITCH_LIMIT_DOWN:+.0f} to {G.PITCH_LIMIT_UP:+.0f} deg")
    print(f"  worst tip moment           {d.worst_tip_moment_nmm/1000:.2f} N*m at {d.worst_pitch_deg:+.0f} deg")
    print(f"  worst hook shear           {d.worst_hook_shear_n:.1f} N at {d.worst_pitch_deg:+.0f} deg")

    if any(p < -G.PITCH_LIMIT_DOWN or p > G.PITCH_LIMIT_UP for p in d.pitch_positions_deg):
        problems.append("A pitch index position exceeds the Sonos-permitted range.")
    if d.worst_tip_moment_nmm <= 0.0:
        problems.append(
            "Worst tip moment computed as zero. Either the pitch set is empty or "
            "the formula is broken — a mount that hangs a 3.15 kg speaker at 20 deg "
            "nose-down cannot have zero anti-tip demand. Do not trust a pass here."
        )

    print("\nBAYONET — worst case both ways")
    print(f"  loose                      {d.bayonet_stack_loose:+.2f} mm")
    print(f"  tight                      {d.bayonet_stack_tight:+.2f} mm")
    if d.bayonet_stack_loose > 0.8:
        problems.append(
            f"Worst-case loose bayonet stack {d.bayonet_stack_loose:.2f} mm > 0.8 mm; "
            f"the docked speaker would visibly nod."
        )

    # --- The bounds report ------------------------------------------------
    bounds = G.bounds_in_use()
    print(f"\nCONSERVATIVE BOUNDS IN USE — {len(bounds)}. None of these is a measurement.")
    for b in bounds:
        print(f"\n  {b.name} = {b.value}")
        if b.replaces:
            print(f"    stands in for : {b.replaces}")
        print(f"    safe because  : {b.worse_if}")
        if b.cost:
            print(f"    costs us      : {b.cost}")

    print("\nCLEARANCES OWED A COUPON PRINT")
    for name in C.VERIFY_BEFORE_COMMIT:
        print(f"  {name} = {getattr(C, name):+.2f} mm")

    if problems:
        print(f"\nSTATUS: FAILED — {len(problems)} issue(s).\n")
        for p in problems:
            print(f"  !! {p}")
        print()
        return 2

    print("\nSTATUS: PASS. Core mount and Module B clear to generate.")
    if mod_a_missing:
        print("        Module A remains gated on 6 base measurements.")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
