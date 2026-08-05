#!/usr/bin/env python3
"""
Checks for the simple two-part bracket. Replaces the seven scripts the
over-centre design needed.

Structure, fit and printability in one pass. Exit 0 pass, 1 fail.
"""
from __future__ import annotations

import sys
from math import pi
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from build123d import Align, Cylinder, Pos  # noqa: E402

from params import bracket as P  # noqa: E402
from params import material as M  # noqa: E402
from parts import _base, clamp_backer, pole_bracket  # noqa: E402

MU = 0.45              # rubber tape on a powder-coated pole, pessimistic
SAFETY = 5.0           # sustained margin required
fails: list[str] = []


def chk(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label:<50} {detail}")
    if not ok:
        fails.append(label)


def main() -> int:
    print("=" * 74)
    print("BRACKET CHECK — 2 printed parts, 2 bolts, 2 inserts")
    print("=" * 74)

    br = pole_bracket.build()
    bk = clamp_backer.build()
    for part, name in ((br, "pole_bracket"), (bk, "clamp_backer")):
        try:
            _base.validate(part, name)
            chk(f"{name} is a single sound solid", True)
        except _base.SolidRejected as e:
            chk(f"{name} is a single sound solid", False, str(e))
    if fails:
        return 1

    allow = M.PETG.allowable_inplane_mpa()
    inter = M.PETG.allowable_interlayer_mpa()
    load, moment = P.load_n(), P.moment_nmm()
    print(f"\n  load {load:.1f} N | moment {moment/1000:.2f} N*m | "
          f"PETG sustained allowable {allow:.2f} MPa in-plane\n")

    # --- Grip range must actually cover the pole -----------------------------
    chk("clamp closes onto the whole pole range",
        P.grip_min() <= P.POLE_D_MIN and P.grip_max() >= P.POLE_D_MAX,
        f"grips {P.grip_min():.1f}-{P.grip_max():.1f} for a "
        f"{P.POLE_D_MIN:.0f}-{P.POLE_D_MAX:.0f} mm pole")

    # --- Anti-slip: two bolts must generate enough normal force --------------
    need_normal = SAFETY * load / MU
    per_bolt = need_normal / 2.0
    chk("bolt tension needed is modest for M5",
        per_bolt < 1500.0, f"{per_bolt:.0f} N per bolt (M5 handles ~5 kN)")

    # --- Bearing under the washer -------------------------------------------
    wash_area = pi * (P.WASHER_OD ** 2 - P.BOLT_CLEAR_D ** 2) / 4.0
    chk("washer bearing under the sustained allowable",
        per_bolt / wash_area < allow,
        f"{per_bolt / wash_area:.2f} MPa on {wash_area:.0f} mm^2 "
        f"({P.WASHER_OD:.0f} mm washer)")

    # --- Heat-set insert pull-out -------------------------------------------
    ins_area = pi * P.INSERT_D * P.INSERT_DEPTH
    chk("insert pull-out under the interlayer allowable",
        per_bolt / ins_area < inter,
        f"{per_bolt / ins_area:.2f} MPa vs {inter:.2f} MPa on {ins_area:.0f} mm^2")

    # --- Arm bending at the collar ------------------------------------------
    w, h, t = P.ARM_W_COLLAR, P.BAND_H, P.WEB_T
    z_mod = (w * h ** 2 - (w - 2 * t) * (h - 2 * t) ** 2) / 6.0
    chk("arm bending at the collar", moment / z_mod < allow,
        f"{moment / z_mod:.2f} MPa, Z={z_mod:.0f} mm^3, "
        f"margin {allow / (moment / z_mod):.1f}x on the derated allowable")

    # --- Pole contact pressure — priority 2 ---------------------------------
    area = 2.0 * (0.42 * pi * P.POLE_D_MIN) * P.BAND_H
    chk("pole contact pressure under the powder-coat limit",
        need_normal / area < 0.60, f"{need_normal / area:.3f} MPa vs 0.60")

    # --- Assembled fit ------------------------------------------------------
    ov = br & bk
    vol = 0.0 if ov is None else (ov.volume if ov.solids() else 0.0)
    chk("halves do not interfere when open", vol <= 1.0,
        f"{vol:.2f} mm^3 at the open gap")

    gap_closed = P.SPLIT_GAP - (P.grip_max() - P.POLE_D_MIN) / 2.0
    chk("gap still open on the smallest pole", gap_closed > 0.5,
        f"{gap_closed:.2f} mm left at {P.POLE_D_MIN:.0f} mm")

    # --- Printability -------------------------------------------------------
    for name, t_ in (("collar wall", P.COLLAR_WALL), ("arm shell", P.WEB_T),
                     ("saddle floor", P.SADDLE_T), ("backstop", P.BACKSTOP_T),
                     ("insert pad floor", P.FLANGE_INSERT_T - P.INSERT_DEPTH)):
        chk(f"{name} >= {M.MIN_WALL_LOADED_MM} mm", t_ >= M.MIN_WALL_LOADED_MM,
            f"{t_:.2f} mm")

    bb = br.bounding_box()
    chk("bracket fits a 256 mm bed", max(bb.size.X, bb.size.Y) <= 250.0,
        f"{bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm")

    print()
    if fails:
        print(f"FAILED — {len(fails)}: {', '.join(fails)}")
        return 1
    print("All bracket checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
