#!/usr/bin/env python3
"""
Tests that the gate actually gates.

The point of Gate 0 is that it cannot be bypassed by accident. These tests
prove the tripwire is live rather than decorative: that an unmeasured value
refuses arithmetic, that the validator reports blocked, and that the derived
layer computes correctly once real numbers are present.

The plausible-values block below is TEST FIXTURE DATA ONLY. It exists to
exercise the derived arithmetic and is deliberately never imported by any part
generator. Nothing here is a measurement and nothing here clears the gate.

Run:  .venv/bin/python tests/test_gate0.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from params import derived as D  # noqa: E402
from params import gate0 as G  # noqa: E402
from params import material as M  # noqa: E402

failures: list[str] = []


def check(label: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}" + (f" — {detail}" if detail else ""))
        failures.append(label)


print("Gate 0 tripwire")

# An unmeasured value must refuse every arithmetic and comparison path.
u = G.UNMEASURED("TEST_FIELD", "a test field")
for op_label, op in [
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
        check(f"unmeasured refuses {op_label}", False, "it returned a value")
    except G.UnmeasuredParameterError:
        check(f"unmeasured refuses {op_label}", True)

# repr must stay safe — the validator needs to print these while blocked.
try:
    check("unmeasured repr is safe", "UNMEASURED" in repr(u))
except Exception as e:  # noqa: BLE001
    check("unmeasured repr is safe", False, str(e))

print("\nGate 0 enforcement")
check("gate reports all 21 fields missing", len(G.missing()) == 21,
      f"got {len(G.missing())}")

try:
    G.require_gate0()
    check("require_gate0 blocks while open", False, "it allowed the call")
except G.UnmeasuredParameterError:
    check("require_gate0 blocks while open", True)

try:
    D.compute()
    check("derived.compute blocks while open", False, "it allowed the call")
except G.UnmeasuredParameterError:
    check("derived.compute blocks while open", True)

r = subprocess.run(
    [sys.executable, str(ROOT / "scripts" / "validate_params.py")],
    capture_output=True, text=True,
)
check("validator exits 1 while blocked", r.returncode == 1, f"exit {r.returncode}")
check("validator names a missing field", "POLE_OD_MID_A" in r.stdout)
check("validator points at the protocol", "GATE0_MEASUREMENT_PROTOCOL" in r.stdout)

# --- Derived arithmetic, exercised with fixture data ------------------------
# Injected into the module only for the duration of this test, then removed.
print("\nDerived arithmetic (fixture data, not measurements)")

FIXTURE = {
    "POLE_OD_LO_A": 63.40, "POLE_OD_LO_B": 63.05,
    "POLE_OD_MID_A": 63.35, "POLE_OD_MID_B": 62.98,
    "POLE_OD_HI_A": 63.28, "POLE_OD_HI_B": 62.90,
    "POLE_SEAM_PROUD": 0.30,
    "POLE_WALL_T": 1.80, "POLE_MATERIAL": "steel-powdercoat",
    "HANDLE_RECESS_W": 78.0, "HANDLE_RECESS_D": 14.0,
    "HANDLE_LIP_R": 3.0, "HANDLE_LIP_H_ABOVE_BASE": 176.0,
    "BASE_FOOTPRINT_X": 122.0, "BASE_FOOTPRINT_Y": 118.0, "BASE_HEIGHT": 21.0,
    "BASE_PAD_OFFSET_X": 0.0, "BASE_PAD_OFFSET_Y": 8.0, "BASE_CABLE_EXIT": "aft",
    "COM_OFFSET_Y": 4.0, "COM_OFFSET_Z": 108.0,
}

originals = {k: getattr(G, k) for k in FIXTURE}
try:
    for k, v in FIXTURE.items():
        setattr(G, k, v)

    check("gate closes with all fields present", G.missing() == [], str(G.missing()))
    d = D.compute()

    check("load is 30.9 N for 3.15 kg", abs(d.load_n - 30.89) < 0.05, f"{d.load_n:.2f}")
    check("ovality derives from the six readings",
          abs(d.pole_ovality - 0.50) < 1e-6, f"{d.pole_ovality:.3f}")
    check("shell bore clears the largest section",
          d.shell_bore_d > d.pole_od_max, f"{d.shell_bore_d:.2f} vs {d.pole_od_max:.2f}")
    check("boom length is positive and plausible",
          40.0 < d.boom_length < 250.0, f"{d.boom_length:.1f}")
    check("overturning moment is non-trivial",
          d.overturning_moment_nmm > 1000.0, f"{d.overturning_moment_nmm:.0f}")
    check("clamp couple exceeds the raw load (it is a lever)",
          d.clamp_couple_n > d.load_n, f"{d.clamp_couple_n:.0f} vs {d.load_n:.1f}")

    # Sonos limits must clip the index plate, not taste.
    check("no pitch position exceeds the Sonos limits",
          all(-20.0 <= p <= 5.0 for p in d.pitch_positions_deg),
          str(d.pitch_positions_deg))
    check("pitch index has usable positions", len(d.pitch_positions_deg) >= 4,
          str(d.pitch_positions_deg))
    check("no inverted position exists",
          all(abs(p) < 90.0 for p in d.pitch_positions_deg))

    # One-value propagation: the whole point of the parametric discipline.
    before = D.compute().shell_bore_d
    G.POLE_OD_MID_A = 68.00  # a bigger pole, one edit
    after = D.compute().shell_bore_d
    check("changing one measured OD moves the shell bore",
          after > before, f"{before:.2f} -> {after:.2f}")
    G.POLE_OD_MID_A = FIXTURE["POLE_OD_MID_A"]

    # Pitch must move the CoM, or the gauntlet would only ever run at level.
    y0, z0 = D.com_at_pitch(0.0)
    y20, z20 = D.com_at_pitch(-20.0)
    check("pitch rotates the CoM", abs(y20 - y0) > 1.0, f"{y0:.1f} -> {y20:.1f}")
finally:
    for k, v in originals.items():
        setattr(G, k, v)

check("gate re-opens after fixture teardown", len(G.missing()) == 21,
      f"{len(G.missing())} missing")

# --- Material allowables ---------------------------------------------------
print("\nMaterial allowables")
check("PLA is absent from the material set",
      not any("PLA" in n for n in dir(M) if n.isupper()))
check("interlayer allowable is below in-plane for every material",
      all(m.allowable_interlayer_mpa() < m.allowable_inplane_mpa()
          for m in (M.PETG, M.ASA, M.PC_BLEND, M.TPU_95A)))
check("every material's Tg clears the 55 C design temp, except TPU by design",
      all(m.glass_transition_c > M.DESIGN_TEMP_C for m in (M.PETG, M.ASA, M.PC_BLEND)))
check("boom arm is specified flat, never standing",
      "Never standing up" in M.PART_SPEC["boom_arm"]["orientation"])
check("clamp shells put hoop tension in-plane",
      "normal to the plate" in M.PART_SPEC["clamp_shell_fixed"]["orientation"])
check("sustained margin requirement is 5x",
      M.SUSTAINED_MARGIN_REQUIRED == 5.0)
check("minimum loaded wall is 2.4 mm", M.MIN_WALL_LOADED_MM == 2.4)

print()
if failures:
    print(f"FAILED — {len(failures)} check(s): {', '.join(failures)}")
    raise SystemExit(1)
print("All checks passed.")
