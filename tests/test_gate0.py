#!/usr/bin/env python3
"""
Tests for the gate, the bounds, and the derived load path.

The gate changed shape when the pole became unconfirmable: it now has to police
three kinds of number rather than one. So these tests check not just that the
tripwire fires, but that every conservative bound in use actually carries a
safety argument, and that the checks which are supposed to be able to fail
still can.

Run:  .venv/bin/python tests/test_gate0.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from params import clearances as C  # noqa: E402
from params import derived as D  # noqa: E402
from params import gate0 as G  # noqa: E402
from params import material as M  # noqa: E402

failures: list[str] = []
passed = 0


def check(label: str, cond: bool, detail: str = "") -> None:
    global passed
    if cond:
        passed += 1
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}" + (f" — {detail}" if detail else ""))
        failures.append(label)


print("Tripwire — Unmeasured refuses to be a number")
u = G.UNMEASURED("TEST_FIELD", "a test field")
for label, op in [
    ("addition", lambda: u + 1),
    ("reverse addition", lambda: 1 + u),
    ("multiplication", lambda: u * 2),
    ("division", lambda: u / 2),
    ("comparison", lambda: u > 1),
    ("float cast", lambda: float(u)),
    ("truthiness", lambda: bool(u)),
]:
    try:
        op()
        check(f"refuses {label}", False, "it returned a value")
    except G.UnmeasuredParameterError:
        check(f"refuses {label}", True)
check("repr stays safe for reporting", "UNMEASURED" in repr(u))

print("\nGate scoping — core open, Module A closed")
check("core scope is clear", G.missing("core") == [], str(G.missing("core")))
check("Module A is gated on 6 fields", len(G.missing("module_a")) == 6,
      str(G.missing("module_a")))
try:
    G.require("core")
    check("require('core') passes", True)
except G.UnmeasuredParameterError as e:
    check("require('core') passes", False, str(e))
try:
    G.require("module_a")
    check("require('module_a') blocks", False, "it allowed the call")
except G.UnmeasuredParameterError:
    check("require('module_a') blocks", True)

# Module A's fields must genuinely block on contact, not just be listed.
try:
    _ = G.BASE_FOOTPRINT_X * 2
    check("base footprint blocks arithmetic", False, "it computed")
except G.UnmeasuredParameterError:
    check("base footprint blocks arithmetic", True)

print("\nBounds — every one must carry its safety argument")
bounds = G.bounds_in_use()
check("bounds are registered", len(bounds) >= 8, f"{len(bounds)} found")
for b in bounds:
    check(f"{b.name} states why it is safe", bool(b.worse_if.strip()))
check("every bound names what it replaces",
      all(b.replaces.strip() for b in bounds),
      str([b.name for b in bounds if not b.replaces.strip()]))
# A bound with no stated cost is a bound nobody has thought about.
check("every load-path bound states its cost",
      all(b.cost.strip() for b in bounds),
      str([b.name for b in bounds if not b.cost.strip()]))

print("\nPole as a range — must be valid at BOTH ends")
d = D.compute(M.CHOSEN)
check("design range is the 2.5 in practical spread",
      abs(d.pole_od_min - 62.0) < 1e-9 and abs(d.pole_od_max - 65.0) < 1e-9,
      f"{d.pole_od_min}-{d.pole_od_max}")
check("shell bore clears the LARGEST pole plus liner both sides",
      d.shell_bore_d >= d.pole_od_max + 2 * d.liner_thickness,
      f"bore {d.shell_bore_d:.2f} vs {d.pole_od_max + 2*d.liner_thickness:.2f}")
check("shim set covers the small end of the range", d.shim_range_covered,
      f"needs {d.shim_stack_needed_min:.2f}, has {G.SHIM_STACK_MAX:.2f}")
check("no shim needed at the large end", d.shim_stack_needed_max == 0.0)
check("shim increments can actually build the needed stack",
      any(abs(sum(combo) - d.shim_stack_needed_min) < 1e-9
          for combo in [(1.5,), (1.0, 0.5), (0.5, 0.5, 0.5)]),
      f"needs {d.shim_stack_needed_min:.2f} from {G.SHIM_THICKNESSES}")

print("\nPETG sizing — the cost of the material choice")
check("PETG is the chosen material", M.CHOSEN.name == "PETG")
check("wall scale exceeds 1.0 vs ASA", d.wall_scale > 1.0, f"{d.wall_scale:.3f}")
check("shell wall clears the 2.4 mm floor", d.shell_wall_t >= M.MIN_WALL_LOADED_MM,
      f"{d.shell_wall_t:.2f}")
check("boom wall clears the 2.4 mm floor", d.boom_wall_t >= M.MIN_WALL_LOADED_MM,
      f"{d.boom_wall_t:.2f}")
check("PETG walls are thicker than ASA walls would be",
      D.compute(M.ASA).shell_wall_t < d.shell_wall_t,
      f"ASA {D.compute(M.ASA).shell_wall_t:.2f} vs PETG {d.shell_wall_t:.2f}")

print("\nLoad path")
check("load is 30.9 N for 3.15 kg", abs(d.load_n - 30.89) < 0.05, f"{d.load_n:.2f}")
check("boom length is plausible", 80.0 < d.boom_length < 220.0, f"{d.boom_length:.1f}")
check("overturning moment is non-trivial", d.overturning_moment_nmm > 2000.0,
      f"{d.overturning_moment_nmm:.0f}")
# The bug this replaced: sizing pressure off the couple understates it ~10x and
# makes the pole-marring check unfailable.
check("preload is friction-derived, not couple-derived",
      d.required_preload_n > d.clamp_couple_n * 3,
      f"preload {d.required_preload_n:.0f} N vs couple {d.clamp_couple_n:.0f} N")
check("preload carries the 5x anti-slip margin",
      abs(d.required_preload_n - 5.0 * d.load_n / C.LINER_FRICTION_COEFF) < 0.1,
      f"{d.required_preload_n:.1f}")
check("pole pressure computed at the small end of the range",
      abs(d.pole_contact_area_mm2
          - 2.0 * 0.40 * 3.14159265 * d.pole_od_min * d.clamp_band_height) < 1.0)
check("pole pressure is under the powder-coat limit",
      d.pole_contact_pressure_mpa < 0.60, f"{d.pole_contact_pressure_mpa:.3f} MPa")

print("\nPitch and anti-tip — level is never the governing case")
check("no pitch position exceeds the Sonos limits",
      all(-20.0 <= p <= 5.0 for p in d.pitch_positions_deg),
      str(d.pitch_positions_deg))
check("no inverted position exists",
      all(abs(p) < 90.0 for p in d.pitch_positions_deg))
check("tip moment is non-zero", d.worst_tip_moment_nmm > 0.0,
      f"{d.worst_tip_moment_nmm:.1f}")
check("worst case is the pitch limit, not level", d.worst_pitch_deg == -20.0,
      f"{d.worst_pitch_deg}")
check("hook shear is non-zero and modest", 5.0 < d.worst_hook_shear_n < 20.0,
      f"{d.worst_hook_shear_n:.1f} N")

print("\nHandle hook — designed around the missing measurement")
check("hook is narrower than the bounded recess width",
      G.HOOK_WIDTH < G.HANDLE_RECESS_W_MIN,
      f"{G.HOOK_WIDTH} vs {G.HANDLE_RECESS_W_MIN}")
check("hook nose is compliant, so lip radius need not be known",
      G.HOOK_NOSE_MATERIAL == "TPU 95A")
check("hook height adjustment spans a real range",
      G.HOOK_HEIGHT_ADJUST_MAX - G.HOOK_HEIGHT_ADJUST_MIN >= 50.0,
      f"{G.HOOK_HEIGHT_ADJUST_MAX - G.HOOK_HEIGHT_ADJUST_MIN} mm")
check("adjustment range brackets a 241 mm speaker's handle region",
      G.HOOK_HEIGHT_ADJUST_MIN < 0.75 * G.SPEAKER_H < G.HOOK_HEIGHT_ADJUST_MAX)

print("\nOne-value propagation")
before = D.compute(M.CHOSEN)
G.POLE_OD_DESIGN_MAX = 68.0
after = D.compute(M.CHOSEN)
check("changing the design max moves the shell bore",
      after.shell_bore_d > before.shell_bore_d,
      f"{before.shell_bore_d:.2f} -> {after.shell_bore_d:.2f}")
check("changing the design max moves the boom length",
      after.boom_length > before.boom_length,
      f"{before.boom_length:.1f} -> {after.boom_length:.1f}")
check("widening the range increases the shim demand",
      after.shim_stack_needed_min > before.shim_stack_needed_min)
G.POLE_OD_DESIGN_MAX = 65.0
check("teardown restores the design range",
      D.compute(M.CHOSEN).shell_bore_d == before.shell_bore_d)

print("\nMaterial set")
check("PLA is absent", not any("PLA" in n for n in dir(M) if n.isupper()))
check("interlayer allowable below in-plane for every material",
      all(m.allowable_interlayer_mpa() < m.allowable_inplane_mpa()
          for m in (M.PETG, M.ASA, M.PC_BLEND, M.TPU_95A)))
check("rigid materials clear the 55 C design temp",
      all(m.glass_transition_c > M.DESIGN_TEMP_C
          for m in (M.PETG, M.ASA, M.PC_BLEND)))
check("boom arm is specified flat, never standing",
      "Never standing up" in M.PART_SPEC["boom_arm"]["orientation"])
check("clamp shells put hoop tension in-plane",
      "normal to the plate" in M.PART_SPEC["clamp_shell_fixed"]["orientation"])
check("sustained margin is 5x", M.SUSTAINED_MARGIN_REQUIRED == 5.0)
check("minimum loaded wall is 2.4 mm", M.MIN_WALL_LOADED_MM == 2.4)
check("every part declares material, orientation and reason",
      all({"material", "orientation", "why"} <= set(v)
          for v in M.PART_SPEC.values()))
check("shim and hook nose exist as parts",
      "pole_shim" in M.PART_SPEC and "hook_nose" in M.PART_SPEC)
check("Module B retainer exists as a part", "usbc_retainer" in M.PART_SPEC)

print("\nValidator end to end")
r = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_params.py")],
                   capture_output=True, text=True)
check("validator exits 0 with core clear", r.returncode == 0, f"exit {r.returncode}")
check("validator reports Module A still gated", "MODULE A: gated" in r.stdout)
check("validator prints the bounds report", "CONSERVATIVE BOUNDS IN USE" in r.stdout)
check("validator states bounds are not measurements",
      "None of these is a measurement" in r.stdout)
check("validator reports the friction preload", "required friction preload" in r.stdout)

print()
if failures:
    print(f"FAILED — {len(failures)} check(s): {', '.join(failures)}")
    raise SystemExit(1)
print(f"All {passed} checks passed.")
