"""
CLAMP SHELL, SWING HALF — the half that opens.

Wraps the aft half of the pole. Carries no suspended load: it closes the band and
generates preload, nothing else. Its single hinge knuckle lands between the fixed
half's outer pair, which puts the pin in double shear rather than cantilevering it.

At the lever parting line it carries the catch pin the over-centre link pulls
against. That pin is loaded in pure tension through the link, so the boss around
it is webbed back into the band the same way the hinge is.

Print: pole axis normal to the plate, same as the fixed half — the hoop path is
identical and so is the reason.
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
from parts.clamp_shell_fixed import OUTER_KNUCKLE_FRACTION  # noqa: E402

NAME = "clamp_shell_swing"
MATERIAL = "PETG"


def middle_knuckle_span(band_h: float) -> tuple[float, float]:
    """z0 and height of the single knuckle, derived from the fixed half's pair.

    Imported from the fixed shell rather than restated, so the interleave cannot
    drift. The gap either side is the named hinge clearance.
    """
    outer_h = band_h * OUTER_KNUCKLE_FRACTION
    z0 = outer_h + L.HINGE_KNUCKLE_GAP
    height = band_h - 2.0 * (outer_h + L.HINGE_KNUCKLE_GAP)
    return z0, height


def build() -> Part:
    d = D.compute()
    band_h = d.clamp_band_height
    centre, arc = L.swing_arc()

    solid = _clamp.band(centre, arc)

    hinge_end = centre - arc / 2.0        # toward 0 deg / +X
    lever_end = centre + arc / 2.0        # toward 180 deg / -X

    # --- Hinge: the single middle knuckle, in double shear ------------------
    z0, kh = middle_knuckle_span(band_h)
    pin_bore = L.HINGE_PIN_D + C.HINGE_PIN_TO_BORE
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
    solid = solid - _clamp.pin_bore_cutter(
        angle_deg=L.HINGE_DEG, z0=z0 - 1.0, height=kh + 2.0,
        bore_d=pin_bore, axis_radius=_clamp.hinge_axis_radius(),
    )

    # --- Catch pin boss for the over-centre link ----------------------------
    # Sits between the fixed half's lever ears, so the link pulls symmetrically
    # and the catch pin sees no bending couple.
    catch_bore = L.CATCH_PIN_D + C.LEVER_PIN_TO_BORE
    catch_h = L.LEVER_EAR_GAP - 2.0 * C.LEVER_PIN_TO_BORE
    catch_z = (band_h - catch_h) / 2.0
    solid = solid + _clamp.knuckle(
        angle_deg=L.LEVER_DEG, z0=catch_z, height=catch_h,
        radius=L.CATCH_BOSS_R, bore_d=catch_bore,
        axis_radius=_clamp.lever_axis_radius(),
    )
    solid = solid + _clamp.knuckle_web(
        angle_deg=lever_end, z0=catch_z, height=catch_h,
        axis_radius=_clamp.lever_axis_radius(),
        width=L.CATCH_BOSS_R * 2.0, toward_deg=centre,
    )
    solid = solid - _clamp.pin_bore_cutter(
        angle_deg=L.LEVER_DEG, z0=catch_z - 1.0, height=catch_h + 2.0,
        bore_d=catch_bore, axis_radius=_clamp.lever_axis_radius(),
    )

    return solid


if __name__ == "__main__":
    d = D.compute()
    z0, kh = middle_knuckle_span(d.clamp_band_height)
    print(f"band {d.clamp_band_height:.1f} mm, wrap {L.SHELL_WRAP_DEG:.0f} deg "
          f"centred on {L.SWING_CENTRE_DEG:.0f} deg")
    print(f"middle knuckle z {z0:.1f} to {z0+kh:.1f} mm "
          f"({L.HINGE_KNUCKLE_GAP:.1f} mm gap each side, double shear)")
    print(f"carries no suspended load — closes the band only")
    raise SystemExit(_base.cli(build, NAME, MATERIAL))
