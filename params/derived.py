"""
DERIVED DIMENSIONS — computed, never typed.

Nothing in here is a measurement and nothing in here is a taste decision.
Measurements live in gate0.py, gaps live in clearances.py, and material
allowables live in material.py. This file is only arithmetic between them.

Evaluation is LAZY. Importing this module is always safe; calling compute()
while Gate 0 is open raises UnmeasuredParameterError naming the first missing
field. That ordering is deliberate — the validator needs to import and report
before anything is allowed to compute.

Changing the measured pole OD means editing gate0.py and nothing else. Every
downstream number below re-derives, including the boom length, the clamp
couple, and therefore the shell wall thickness.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians, sin

from . import clearances as C
from . import gate0 as G

G_ACCEL = 9.80665  # m/s^2


@dataclass(frozen=True)
class Derived:
    # Pole envelope
    pole_od_max: float
    pole_od_min: float
    pole_ovality: float
    pole_od_nominal: float

    # Clamp
    shell_bore_d: float
    liner_id_free: float
    liner_thickness: float
    clamp_band_height: float

    # Boom / load path
    boom_length: float
    load_n: float
    overturning_moment_nmm: float
    clamp_couple_arm: float
    clamp_couple_n: float

    # Worst-case bayonet stack
    bayonet_stack_loose: float
    bayonet_stack_tight: float

    # Pitch
    pitch_positions_deg: tuple[float, ...]


def _pole_ods() -> list[float]:
    return [
        G.POLE_OD_LO_A, G.POLE_OD_LO_B,
        G.POLE_OD_MID_A, G.POLE_OD_MID_B,
        G.POLE_OD_HI_A, G.POLE_OD_HI_B,
    ]


def compute() -> Derived:
    """Derive every dependent dimension. Raises while Gate 0 is open."""
    G.require_gate0()

    ods = _pole_ods()
    od_max = max(ods)
    od_min = min(ods)
    ovality = od_max - od_min
    # The clamp band is at MID, so the shell bore is driven by what is actually
    # under it — but it must still close over the largest section it may be slid
    # past during install. Use the global max, not the MID average.
    od_nominal = (G.POLE_OD_MID_A + G.POLE_OD_MID_B) / 2.0

    # --- Clamp geometry ---------------------------------------------------
    # Liner is squeezed by LINER_TO_POLE at the smallest measured section, so
    # grip survives ovality rather than depending on the pole being round.
    liner_thickness = 3.0 + G.POLE_SEAM_PROUD + C.LINER_SEAM_RELIEF
    liner_id_free = od_min + C.LINER_TO_POLE
    shell_bore_d = od_max + C.SHELL_BORE_TO_POLE_OPEN + 2.0 * liner_thickness

    # Band height follows the couple it has to resist, not a round number.
    # Set after the couple is known, below.

    # --- Load path --------------------------------------------------------
    load_n = (G.SUSPENDED_MASS / 1000.0) * G_ACCEL

    # Boom reaches from the pole surface to the speaker's CoM in plan.
    # Half the shell OD, plus the speaker's aft face standoff, plus how far
    # forward of that face the CoM sits.
    shell_wall = 5.0  # provisional; the gauntlet sizes this from the couple
    boom_length = (shell_bore_d / 2.0 + shell_wall) + (G.SPEAKER_D / 2.0) - G.COM_OFFSET_Y

    overturning_moment = load_n * boom_length  # N*mm about the clamp band

    # The clamp resists that moment as a couple over the band height. Taller
    # band, lower contact force, less chance of denting the pole wall.
    clamp_band_height = max(70.0, 2.2 * G.POLE_WALL_T * 10.0, boom_length * 0.55)
    clamp_couple_arm = clamp_band_height * 0.72  # effective, pressure not uniform
    clamp_couple_n = overturning_moment / clamp_couple_arm

    # --- Bayonet worst-case stack, both directions ------------------------
    bayonet_stack_loose = (
        C.BAYONET_SPIGOT_TO_BORE + C.BAYONET_LUG_RADIAL + C.DETENT_BALL_TO_POCKET
    )
    bayonet_stack_tight = -(abs(C.DETENT_PRELOAD_CRUSH) * 0.5)

    # --- Pitch index, clipped to what Sonos permits -----------------------
    candidates = (-20.0, -15.0, -10.0, -5.0, 0.0, 5.0)
    pitch = tuple(
        p for p in candidates
        if -G.PITCH_LIMIT_DOWN <= p <= G.PITCH_LIMIT_UP
    )

    return Derived(
        pole_od_max=od_max,
        pole_od_min=od_min,
        pole_ovality=ovality,
        pole_od_nominal=od_nominal,
        shell_bore_d=shell_bore_d,
        liner_id_free=liner_id_free,
        liner_thickness=liner_thickness,
        clamp_band_height=clamp_band_height,
        boom_length=boom_length,
        load_n=load_n,
        overturning_moment_nmm=overturning_moment,
        clamp_couple_arm=clamp_couple_arm,
        clamp_couple_n=clamp_couple_n,
        bayonet_stack_loose=bayonet_stack_loose,
        bayonet_stack_tight=bayonet_stack_tight,
        pitch_positions_deg=pitch,
    )


def com_at_pitch(pitch_deg: float) -> tuple[float, float]:
    """CoM offset (y, z) rotated to a pitch index position.

    Pitch moves the CoM, which moves the moment. The gauntlet must run at the
    worst position, not at level.
    """
    G.require_gate0()
    a = radians(pitch_deg)
    y, z = G.COM_OFFSET_Y, G.COM_OFFSET_Z
    return (y * cos(a) - z * sin(a), y * sin(a) + z * cos(a))
