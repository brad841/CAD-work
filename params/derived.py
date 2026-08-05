"""
DERIVED DIMENSIONS — computed, never typed.

Measurements and bounds live in gate0.py, gaps in clearances.py, allowables in
material.py. This file is only arithmetic between them.

Two things changed when the pole became unconfirmable and PETG became the
material:

  1. There is no single pole diameter. Every pole-facing dimension derives from
     the design RANGE, and the design must be valid at BOTH ends simultaneously
     — the shell closes on the max, the shim stack reaches the min. Worst case
     is checked in both directions rather than at a nominal.

  2. PETG's sustained knockdown is lower than ASA's, so loaded sections get
     scaled by the ratio of allowables rather than by eye. wall_scale() is that
     ratio, and it is why the PETG build is heavier than the ASA build would be.

Evaluation is lazy: importing is always safe, compute() raises if a blocking
field is open.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, pi, radians, sin, sqrt

from . import clearances as C
from . import gate0 as G
from . import material as M

G_ACCEL = 9.80665


@dataclass(frozen=True)
class Derived:
    # Pole envelope — a range, not a value
    pole_od_min: float
    pole_od_max: float
    pole_range: float

    # Clamp
    liner_thickness: float
    shell_bore_d: float
    shim_stack_needed_min: float
    shim_stack_needed_max: float
    shim_range_covered: bool

    # Load path, at the bounded adverse CoM
    load_n: float
    boom_length: float
    overturning_moment_nmm: float
    clamp_band_height: float
    clamp_couple_arm: float
    clamp_couple_n: float
    required_preload_n: float
    pole_contact_area_mm2: float
    pole_contact_pressure_mpa: float

    # PETG sizing
    wall_scale: float
    boom_wall_t: float
    shell_wall_t: float

    # Bayonet
    bayonet_stack_loose: float
    bayonet_stack_tight: float

    # Pitch
    pitch_positions_deg: tuple[float, ...]
    worst_pitch_deg: float
    worst_tip_moment_nmm: float
    worst_hook_shear_n: float


def wall_scale(material: M.Material = M.PETG,
               reference: M.Material = M.ASA) -> float:
    """How much thicker a loaded section must be in `material` vs `reference`.

    Section capacity in bending scales with thickness squared, so the linear
    scale is the square root of the allowable ratio. This is the honest cost of
    choosing PETG: not a guess at "a bit thicker", a derived multiplier.
    """
    ratio = reference.allowable_interlayer_mpa() / material.allowable_interlayer_mpa()
    return sqrt(ratio)


def compute(material: M.Material = M.PETG) -> Derived:
    """Derive every dependent dimension. Raises if a blocking field is open."""
    G.require("core")

    od_min = G.POLE_OD_DESIGN_MIN
    od_max = G.POLE_OD_DESIGN_MAX
    pole_range = od_max - od_min

    # --- Clamp geometry, valid at both ends of the range -------------------
    liner_thickness = 3.0 + G.POLE_SEAM_PROUD + C.LINER_SEAM_RELIEF

    # The shell bore is set by the LARGEST pole it must close on. A smaller pole
    # is brought up to this bore by shims, never by over-squeezing the liner.
    shell_bore_d = od_max + C.SHELL_BORE_TO_POLE_OPEN + 2.0 * liner_thickness

    # Radial shim needed at each end of the range. At od_max, none.
    shim_stack_needed_max = 0.0
    shim_stack_needed_min = (od_max - od_min) / 2.0
    shim_range_covered = shim_stack_needed_min <= G.SHIM_STACK_MAX

    # --- Load path at the bounded adverse CoM -----------------------------
    load_n = (G.SUSPENDED_MASS / 1000.0) * G_ACCEL

    scale = wall_scale(material)
    shell_wall_t = max(M.MIN_WALL_LOADED_MM, 4.0 * scale)
    boom_wall_t = max(M.MIN_WALL_LOADED_MM, 3.6 * scale)

    # Boom reaches from pole surface to the CoM in plan. COM_OFFSET_Y is bounded
    # negative (forward, away from the pole), which lengthens this lever — the
    # adverse direction, deliberately.
    boom_length = (
        shell_bore_d / 2.0 + shell_wall_t
        + G.SPEAKER_D / 2.0
        - G.COM_OFFSET_Y
    )

    overturning_moment = load_n * boom_length

    # The clamp resists that moment as a couple over the band height. With the
    # pole wall bounded THIN, band height is driven by keeping contact pressure
    # under what powder coat tolerates, not by strength.
    clamp_band_height = max(70.0, boom_length * 0.55, 88.0)
    clamp_couple_arm = clamp_band_height * 0.72
    clamp_couple_n = overturning_moment / clamp_couple_arm

    # Contact pressure is NOT set by the couple. The couple is carried by direct
    # bearing — the shells press top-and-bottom against the pole and need no
    # friction to do it. What sets pressure is the PRELOAD required to stop the
    # clamp sliding down the pole, which is a friction problem:
    #
    #     mu * N >= load, with the sustained margin applied
    #
    # Sizing pressure off the couple instead understates it by an order of
    # magnitude and produces a check that cannot fail.
    required_preload_n = (
        M.SUSTAINED_MARGIN_REQUIRED * load_n / C.LINER_FRICTION_COEFF
    )

    # Preload spreads over the liner wrap: two shells, ~40% of circumference
    # each, full band height. Computed at the SMALL end of the pole range, where
    # the same preload acts on the least area and pressure is highest.
    pole_contact_area_mm2 = 2.0 * (0.40 * pi * od_min) * clamp_band_height
    pole_contact_pressure_mpa = required_preload_n / pole_contact_area_mm2

    # --- Bayonet worst case, both directions ------------------------------
    bayonet_stack_loose = (
        C.BAYONET_SPIGOT_TO_BORE + C.BAYONET_LUG_RADIAL + C.DETENT_BALL_TO_POCKET
    )
    bayonet_stack_tight = -(abs(C.DETENT_PRELOAD_CRUSH) * 0.5)

    # --- Pitch, clipped to what Sonos permits -----------------------------
    candidates = (-20.0, -15.0, -10.0, -5.0, 0.0, 5.0)
    pitch = tuple(p for p in candidates
                  if -G.PITCH_LIMIT_DOWN <= p <= G.PITCH_LIMIT_UP)

    # Worst anti-tip demand across the permitted pitch positions.
    #
    # Pitched nose-down, gravity gains a component along the tray plane. That
    # component is what the rear-handle hook resists in shear, and it acts at
    # the CoM height above the tray, so it also tries to rotate the speaker off
    # the tray's front lip. Both scale with sin(pitch), which is why level is
    # never the governing case and the critic must run at the limit.
    worst_pitch, worst_tip, worst_shear = 0.0, 0.0, 0.0
    for p in pitch:
        s = abs(sin(radians(p)))
        shear = load_n * s                      # N, along the tray plane
        tip = load_n * s * G.COM_OFFSET_Z       # N*mm, about the front lip
        if tip >= worst_tip:
            worst_pitch, worst_tip, worst_shear = p, tip, shear

    return Derived(
        pole_od_min=od_min,
        pole_od_max=od_max,
        pole_range=pole_range,
        liner_thickness=liner_thickness,
        shell_bore_d=shell_bore_d,
        shim_stack_needed_min=shim_stack_needed_min,
        shim_stack_needed_max=shim_stack_needed_max,
        shim_range_covered=shim_range_covered,
        load_n=load_n,
        boom_length=boom_length,
        overturning_moment_nmm=overturning_moment,
        clamp_band_height=clamp_band_height,
        clamp_couple_arm=clamp_couple_arm,
        clamp_couple_n=clamp_couple_n,
        required_preload_n=required_preload_n,
        pole_contact_area_mm2=pole_contact_area_mm2,
        pole_contact_pressure_mpa=pole_contact_pressure_mpa,
        wall_scale=scale,
        boom_wall_t=boom_wall_t,
        shell_wall_t=shell_wall_t,
        bayonet_stack_loose=bayonet_stack_loose,
        bayonet_stack_tight=bayonet_stack_tight,
        pitch_positions_deg=pitch,
        worst_pitch_deg=worst_pitch,
        worst_tip_moment_nmm=worst_tip,
        worst_hook_shear_n=worst_shear,
    )


def com_at_pitch(pitch_deg: float) -> tuple[float, float]:
    """Bounded CoM offset (y, z) rotated to a pitch index position.

    Pitch moves the CoM, so the failure critic must run at the worst permitted
    position rather than at level.
    """
    a = radians(pitch_deg)
    y, z = G.COM_OFFSET_Y, G.COM_OFFSET_Z
    return (y * cos(a) - z * sin(a), y * sin(a) + z * cos(a))
