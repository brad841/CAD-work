"""
CLAMP SHELL, FIXED HALF — the one the load actually goes through.

Wraps the forward half of the pole and carries the boom pad at 270 deg, so the
suspended load runs boom -> pad -> band -> pole without passing through the hinge
pin or the lever link. Neither mechanism is in the suspended path. That is
deliberate and it is the reason a failed lever cannot drop the speaker: opening
the lever releases the CLAMP, and the tether catches the cradle.

Carries:
  - two hinge knuckles (outer pair) at the hinge parting line
  - the lever pivot ears at the lever parting line
  - the boom / bayonet-collar mounting pad with four M5 heat-set bosses
  - the tether anchor, in the band wall rather than on any mechanism

Print: pole axis normal to the plate, so hoop tension is in-plane. Standing it
the other way runs the clamping load straight across layer boundaries, and PETG's
interlayer allowable is the number that would govern.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Part  # noqa: E402

from params import clamp as L  # noqa: E402
from params import clearances as C  # noqa: E402
from params import derived as D  # noqa: E402
from parts import _base, _clamp  # noqa: E402

NAME = "clamp_shell_fixed"
MATERIAL = "PETG"

# Knuckle split up the band. The fixed half takes the outer pair so the swing
# half's single knuckle lands between them in double shear.
OUTER_KNUCKLE_FRACTION = 0.28
FILLET_R = 2.0


def build() -> Part:
    d = D.compute()
    band_h = d.clamp_band_height
    centre, arc = L.fixed_arc()

    solid = _clamp.band(centre, arc)

    # Parting-line angles: the ends of this shell's wrap.
    hinge_end = centre + arc / 2.0        # toward 0 deg / +X
    lever_end = centre - arc / 2.0        # toward 180 deg / -X

    # --- Hinge: outer knuckle pair -----------------------------------------
    kh = band_h * OUTER_KNUCKLE_FRACTION
    pin_bore = L.HINGE_PIN_D + C.HINGE_PIN_TO_BORE
    for z0 in (0.0, band_h - kh):
        solid = solid + _clamp.knuckle(
            angle_deg=L.HINGE_DEG, z0=z0, height=kh,
            radius=L.HINGE_BOSS_R, bore_d=pin_bore,
            axis_radius=_clamp.hinge_axis_radius(),
        )
        solid = solid + _clamp.knuckle_web(
            angle_deg=hinge_end, z0=z0, height=kh,
            axis_radius=_clamp.hinge_axis_radius(),
            width=L.HINGE_KNUCKLE_W, toward_deg=centre,
        )
        # Re-cut the bore: the web crosses it.
        solid = solid - _clamp.pin_bore_cutter(
            angle_deg=L.HINGE_DEG, z0=z0 - 1.0, height=kh + 2.0,
            bore_d=pin_bore, axis_radius=_clamp.hinge_axis_radius(),
        )

    # --- Lever pivot ears ---------------------------------------------------
    ear_bore = L.LEVER_PIVOT_D + C.LEVER_PIN_TO_BORE
    ear_z = (band_h - L.LEVER_EAR_GAP) / 2.0 - L.LEVER_EAR_W
    for z0 in (ear_z, ear_z + L.LEVER_EAR_W + L.LEVER_EAR_GAP):
        solid = solid + _clamp.knuckle(
            angle_deg=L.LEVER_DEG, z0=z0, height=L.LEVER_EAR_W,
            radius=L.LEVER_BOSS_R, bore_d=ear_bore,
            axis_radius=_clamp.lever_axis_radius(),
        )
        solid = solid + _clamp.knuckle_web(
            angle_deg=lever_end, z0=z0, height=L.LEVER_EAR_W,
            axis_radius=_clamp.lever_axis_radius(),
            width=L.LEVER_EAR_W, toward_deg=centre,
        )
        solid = solid - _clamp.pin_bore_cutter(
            angle_deg=L.LEVER_DEG, z0=z0 - 1.0, height=L.LEVER_EAR_W + 2.0,
            bore_d=ear_bore, axis_radius=_clamp.lever_axis_radius(),
        )

    # --- Boom pad and tether anchor ----------------------------------------
    solid = solid + _clamp.boom_pad()
    solid = solid + _clamp.tether_anchor(L.BOOM_DEG - 52.0)

    return solid


if __name__ == "__main__":
    d = D.compute()
    r_in, r_out = _clamp.shell_radii()
    print(f"band {d.clamp_band_height:.1f} mm tall, bore {r_in*2:.2f} mm, "
          f"OD {r_out*2:.2f} mm, wall {d.shell_wall_t:.2f} mm")
    print(f"wrap {L.SHELL_WRAP_DEG:.0f} deg centred on {L.FIXED_CENTRE_DEG:.0f} deg, "
          f"parting gap {L.gap_deg():.0f} deg each side")
    print(f"resists {d.overturning_moment_nmm/1000:.2f} N*m over a "
          f"{d.clamp_couple_arm:.1f} mm couple arm")
    raise SystemExit(_base.cli(build, NAME, MATERIAL))
