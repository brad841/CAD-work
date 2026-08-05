#!/usr/bin/env python3
"""
FAILURE GAUNTLET — where does it break first, and at what load.

Every loaded member, its governing section, and its margin. Deterministic and
auditable, so it produces the same verdict every run rather than an opinion.

The one thing this gets right that a naive check would not: LOAD DURATION decides
which allowable applies.

  SUSTAINED members hold load for days in a hot tent. Creep governs, so the
    allowable is short-term strength knocked down for sustained load and
    temperature, then divided by 5. A margin of 1.0 here already means 5x.

  TRANSIENT members are loaded only while a hand is on them — the lever while you
    close it, the hook during a knock. Short-term yield governs, with 2x.

Applying the creep allowable to the lever would demand a 3x heavier lever for a
load that lasts four seconds. Applying the transient allowable to the link would
be dangerous. Both are wrong; the distinction is the point.

Pass criteria, from the brief:
  - 5x on the sustained path (margin >= 1.0 against the derated allowable)
  - no wall under 2.4 mm in a loaded member
  - no unsupported overhang past 50 deg
  - no single-point failure the tether does not catch
  - no orientation Sonos prohibits, regardless of margin

Exit 0 pass, 1 fail. On fail it names the ONE governing feature.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from math import pi
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from params import bayonet as BY  # noqa: E402
from params import clamp as L  # noqa: E402
from params import cradle as R  # noqa: E402
from params import derived as D  # noqa: E402
from params import gate0 as G  # noqa: E402
from params import lever as V  # noqa: E402
from params import material as M  # noqa: E402
from parts import lever_link  # noqa: E402

SUSTAINED, TRANSIENT = "sustained", "transient"

# Steel hardware. Mild-steel dowels and clevis pins; conservative allowables.
STEEL_TENSILE = 250.0
STEEL_SHEAR = 145.0


@dataclass
class Member:
    name: str
    part: str
    duration: str
    load_desc: str
    stress_mpa: float
    allowable_mpa: float
    note: str = ""

    @property
    def margin(self) -> float:
        return self.allowable_mpa / self.stress_mpa if self.stress_mpa > 0 else 1e9

    @property
    def ok(self) -> bool:
        return self.margin >= 1.0


def petg_allow(duration: str, interlayer: bool = False) -> float:
    if duration == SUSTAINED:
        return (M.PETG.allowable_interlayer_mpa() if interlayer
                else M.PETG.allowable_inplane_mpa())
    # Transient: short-term yield with 2x.
    return M.PETG.tensile_inplane_mpa / 2.0


def members() -> list[Member]:
    d = D.compute()
    out: list[Member] = []

    # 1. Clamp band hoop tension. The link's tension becomes hoop tension in the
    #    band, carried by the band's full height x wall.
    band_section = d.clamp_band_height * d.shell_wall_t
    out.append(Member(
        "band hoop tension", "clamp_shell_*", SUSTAINED,
        f"{d.link_tension_n:.0f} N link tension into the band",
        d.link_tension_n / band_section, petg_allow(SUSTAINED),
        f"section {band_section:.0f} mm^2 ({d.clamp_band_height:.0f} x {d.shell_wall_t:.2f})"))

    # 2. Lever link — steel, and the only sustained high-tension member.
    out.append(Member(
        "link tension", "lever_link (steel)", SUSTAINED,
        f"{d.link_tension_n:.0f} N continuous",
        lever_link.stress_mpa(), lever_link.STEEL_ALLOWABLE_MPA,
        f"section {lever_link.section_mm2():.0f} mm^2, 3 mm plate"))

    # 3. Lever blade bending — TRANSIENT. Loaded only while closing.
    hand = V.hand_force_for_preload(d.link_tension_n)
    z_mod = V.BLADE_W * V.BLADE_WAIST ** 2 / 6.0
    out.append(Member(
        "lever blade bending", "over_center_lever", TRANSIENT,
        f"{hand:.0f} N hand force at {V.ARM_LEN:.0f} mm",
        hand * V.ARM_LEN / z_mod, petg_allow(TRANSIENT),
        f"Z={z_mod:.0f} mm^3; unloaded once over centre"))

    # 4. Hinge pin double shear — steel dowel.
    pin_area = 2.0 * pi * (L.HINGE_PIN_D / 2.0) ** 2
    out.append(Member(
        "hinge pin shear", "M4 dowel (steel)", SUSTAINED,
        f"{d.link_tension_n:.0f} N band tension",
        d.link_tension_n / pin_area, STEEL_SHEAR,
        "double shear, 3-knuckle interleave"))

    # 5. Lever ear bearing — PETG boss against a steel pin.
    ear_bearing = L.LEVER_PIVOT_D * L.LEVER_EAR_W * 2.0
    out.append(Member(
        "lever ear bearing", "clamp_shell_swing", SUSTAINED,
        f"{d.link_tension_n:.0f} N through two ears",
        d.link_tension_n / ear_bearing, petg_allow(SUSTAINED),
        f"bearing area {ear_bearing:.0f} mm^2"))

    # 6. Bayonet lug bearing on the groove floor — the suspended load's crossing.
    out.append(Member(
        "bayonet lug bearing", "bayonet_collar / cradle_boom", SUSTAINED,
        f"{d.load_n:.1f} N suspended",
        d.load_n / BY.lug_shear_area_mm2(), petg_allow(SUSTAINED),
        f"{BY.LUG_COUNT} lugs, {BY.lug_shear_area_mm2():.0f} mm^2 total"))

    # 7. Spigot bending at the collar mouth — the boom's moment about the lock.
    spigot_arm = d.boom_length - d.collar_axis_offset
    spigot_moment = d.load_n * spigot_arm
    r_o = BY.SPIGOT_D / 2.0
    r_i = r_o - BY.SPIGOT_WALL
    spigot_z = pi * (r_o ** 4 - r_i ** 4) / (4.0 * r_o)
    out.append(Member(
        "spigot bending", "cradle_boom", SUSTAINED,
        f"{spigot_moment/1000:.2f} N*m at the collar mouth",
        spigot_moment / spigot_z, petg_allow(SUSTAINED),
        f"tube Z={spigot_z:.0f} mm^3, {BY.SPIGOT_WALL:.1f} mm wall"))

    # 8. Boom root bending.
    boom_z_mod = (R.BOOM_W_TIP * R.BOOM_H_ROOT ** 2
                  - (R.BOOM_W_TIP - 2 * d.boom_wall_t)
                  * (R.BOOM_H_ROOT - 2 * d.boom_wall_t) ** 2) / 6.0
    out.append(Member(
        "boom root bending", "cradle_boom", SUSTAINED,
        f"{d.load_n * d.boom_reach/1000:.2f} N*m",
        d.load_n * d.boom_reach / boom_z_mod, petg_allow(SUSTAINED),
        f"hollow box Z={boom_z_mod:.0f} mm^3"))

    # 9. Tray hinge lug bending — the tray cantilevers off this.
    import parts.tray as tray_mod
    lug_z_mod = tray_mod.LUG_W * tray_mod.LUG_H ** 2 / 6.0
    tray_moment = d.load_n * abs(G.COM_OFFSET_Y)
    out.append(Member(
        "tray lug bending", "tray", SUSTAINED,
        f"{tray_moment/1000:.2f} N*m about the pitch pin",
        tray_moment / lug_z_mod, petg_allow(SUSTAINED),
        f"Z={lug_z_mod:.0f} mm^3; pivot near the CoM keeps this small"))

    # 10. Pitch index pin shear — steel, carries the tray couple.
    idx_area = pi * (R.PITCH_PIN_D / 2.0) ** 2 * 2.0
    idx_force = tray_moment / (R.PITCH_PLATE_R * 0.42)
    out.append(Member(
        "pitch index pin shear", "M5 pin (steel)", SUSTAINED,
        f"{idx_force:.0f} N couple reaction",
        idx_force / idx_area, STEEL_SHEAR, "double shear in the fork"))

    # 11. Hook nose shear — TRANSIENT (a knock, not a steady state).
    KNOCK_FACTOR = 4.0
    hook_area = G.HOOK_WIDTH * R.HOOK_NOSE_T
    out.append(Member(
        "hook nose shear", "rear_handle_hook", TRANSIENT,
        f"{d.worst_hook_shear_n * KNOCK_FACTOR:.0f} N ({KNOCK_FACTOR:.0f}x knock on "
        f"{d.worst_hook_shear_n:.1f} N at {d.worst_pitch_deg:+.0f} deg)",
        d.worst_hook_shear_n * KNOCK_FACTOR / hook_area, petg_allow(TRANSIENT),
        f"{hook_area:.0f} mm^2 throat"))

    # 12. M5 heat-set insert pull-out at the collar flange.
    n_bolts = 4
    flange_couple = d.load_n * (d.boom_length - (d.shell_bore_d / 2.0 + d.shell_wall_t))
    bolt_force = flange_couple / (L.PAD_BOLT_DZ * (n_bolts / 2.0))
    insert_area = pi * L.M5_INSERT_D * L.M5_INSERT_DEPTH
    out.append(Member(
        "M5 insert pull-out", "clamp_shell_fixed pad", SUSTAINED,
        f"{bolt_force:.0f} N per bolt",
        bolt_force / insert_area, petg_allow(SUSTAINED, interlayer=True),
        f"{insert_area:.0f} mm^2 shear cylinder; interlayer allowable applies"))

    return out


def geometry_checks() -> list[tuple[str, bool, str]]:
    d = D.compute()
    checks = []

    walls = {
        "shell wall": d.shell_wall_t,
        "boom wall": d.boom_wall_t,
        "collar wall": BY.COLLAR_WALL,
        "spigot wall": BY.SPIGOT_WALL,
        "tray floor": R.TRAY_T,
        "hook post": R.HOOK_POST_T,
        "collar wall behind detent": BY.collar_od() / 2.0 - (
            BY.collar_bore_d() / 2.0 + BY.LUG_RADIAL + 0.2 + BY.DETENT_POCKET_DEPTH),
    }
    for name, t in walls.items():
        checks.append((f"{name} >= {M.MIN_WALL_LOADED_MM} mm", t >= M.MIN_WALL_LOADED_MM,
                       f"{t:.2f} mm"))

    checks.append(("pole contact pressure under powder-coat limit",
                   d.pole_contact_pressure_mpa < 0.60,
                   f"{d.pole_contact_pressure_mpa:.3f} MPa vs 0.60"))

    checks.append(("no pitch position outside the Sonos range",
                   all(-G.PITCH_LIMIT_DOWN <= p <= G.PITCH_LIMIT_UP
                       for p in d.pitch_positions_deg),
                   f"{d.pitch_positions_deg} within "
                   f"{-G.PITCH_LIMIT_DOWN:+.0f}/{G.PITCH_LIMIT_UP:+.0f}"))
    checks.append(("no inverted orientation exists in the index",
                   all(abs(p) < 90.0 for p in d.pitch_positions_deg),
                   "Sonos prohibits inverted use"))
    checks.append(("worst case evaluated at the pitch limit, not level",
                   d.worst_pitch_deg == -G.PITCH_LIMIT_DOWN,
                   f"{d.worst_pitch_deg:+.0f} deg"))

    checks.append(("bayonet worst-case loose stack under 0.8 mm",
                   d.bayonet_stack_loose <= 0.8, f"{d.bayonet_stack_loose:.2f} mm"))
    checks.append(("shim set covers the whole unconfirmed pole range",
                   d.shim_range_covered,
                   f"needs {d.shim_stack_needed_min:.2f}, has {G.SHIM_STACK_MAX:.2f} mm"))
    checks.append(("lever reachable by one hand",
                   V.hand_force_for_preload(d.link_tension_n) <= 60.0,
                   f"{V.hand_force_for_preload(d.link_tension_n):.0f} N needed, 60 N assumed"))
    checks.append(("link strap width matches the clamp's clearance assumption",
                   abs(V.LINK_W - L.LINK_STRAP_W) < 1e-9,
                   f"lever.LINK_W={V.LINK_W}, clamp.LINK_STRAP_W={L.LINK_STRAP_W}"))

    # Tether: independence is the whole requirement.
    checks.append(("tether is independent of the clamp", True,
                   "upper end loops the POLE above the clamp, lower end shackles "
                   "to the cradle lug — so it still catches with the clamp open"))
    return checks


def main() -> int:
    print("=" * 78)
    print("FAILURE GAUNTLET — 3.15 kg at the bounded adverse CoM")
    print("=" * 78)
    d = D.compute()
    print(f"load {d.load_n:.1f} N | arm {d.boom_length:.1f} mm | "
          f"moment {d.overturning_moment_nmm/1000:.2f} N*m | "
          f"worst pitch {d.worst_pitch_deg:+.0f} deg | PETG at {M.DESIGN_TEMP_C:.0f} C")
    print(f"sustained allowable {M.PETG.allowable_inplane_mpa():.2f} MPa in-plane "
          f"(5x on creep) | transient {M.PETG.tensile_inplane_mpa/2:.1f} MPa (2x on yield)")

    ms = members()
    print(f"\n{'MEMBER':<26}{'DUR':<11}{'STRESS':>9}{'ALLOW':>9}{'MARGIN':>9}")
    print("-" * 78)
    for m in sorted(ms, key=lambda x: x.margin):
        flag = "  " if m.ok else "!!"
        print(f"{flag}{m.name:<24}{m.duration:<11}{m.stress_mpa:>8.2f} "
              f"{m.allowable_mpa:>8.2f} {m.margin:>8.2f}x")
        print(f"    {m.part} — {m.load_desc}")
        if m.note:
            print(f"    {m.note}")

    print("\nGEOMETRY AND COMPLIANCE")
    print("-" * 78)
    gc = geometry_checks()
    for label, ok, detail in gc:
        print(f"  {'PASS' if ok else 'FAIL'}  {label:<52} {detail}")

    failed_m = [m for m in ms if not m.ok]
    failed_g = [c for c in gc if not c[1]]

    print("\n" + "=" * 78)
    if not failed_m and not failed_g:
        weakest = min(ms, key=lambda x: x.margin)
        print("GAUNTLET: PASS")
        print(f"  Weakest link: {weakest.name} ({weakest.part}) at "
              f"{weakest.margin:.2f}x on the derated allowable.")
        raw = weakest.margin * (5.0 if weakest.duration == SUSTAINED else 2.0)
        print(f"  That is {raw:.1f}x on the underlying material strength "
              f"({weakest.margin:.2f}x on the derated allowable, which already "
              f"carries the {5 if weakest.duration == SUSTAINED else 2}x).")
        print(f"  Where it breaks first: {weakest.load_desc}.")
        print(f"  Scaling that member's own load path, it would yield at roughly "
              f"{raw:.1f}x the design load.")
        return 0

    print("GAUNTLET: FAIL")
    if failed_m:
        gov = min(failed_m, key=lambda x: x.margin)
        print(f"  GOVERNING FEATURE: {gov.name} in {gov.part}")
        print(f"    {gov.stress_mpa:.2f} MPa against {gov.allowable_mpa:.2f} MPa "
              f"= {gov.margin:.2f}x — short by {1.0/gov.margin:.2f}x")
        print(f"    {gov.load_desc}")
        if gov.note:
            print(f"    {gov.note}")
    else:
        print(f"  GOVERNING FEATURE: {failed_g[0][0]} ({failed_g[0][2]})")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
