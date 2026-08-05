"""
MATERIAL ALLOWABLES — creep governs, not yield.

This mount hangs 3.15 kg continuously for days in a hot tent. Nothing here is
sized against short-term tensile strength, because nothing here fails that way.
The failure mode is slow: sustained stress at elevated temperature, layer
boundaries opening, the boom drooping until the bayonet unloads.

So the allowable below is not the datasheet number. It is the datasheet number
knocked down for (a) sustained load rather than a two-minute pull, (b) the
inside of a tent in sun, and (c) FDM anisotropy, which is why every part
carries a declared print orientation.

PLA is absent on purpose. Its glass transition sits near the tent temperature
and it creeps under exactly this kind of dead load.
"""

from __future__ import annotations

from dataclasses import dataclass

# Design temperature. A closed tent in sun runs well above ambient; sizing at
# 25 C would be optimistic to the point of dishonesty.
DESIGN_TEMP_C = 55.0

SUSTAINED_MARGIN_REQUIRED = 5.0   # gauntlet pass criterion, on the creep path
MIN_WALL_LOADED_MM = 2.4          # gauntlet pass criterion, any loaded member
MAX_OVERHANG_DEG = 50.0           # gauntlet pass criterion, unsupported
MAX_BRIDGE_MM = 12.0


@dataclass(frozen=True)
class Material:
    name: str
    # Short-term tensile, printed, along layers (in-plane). Datasheet-ish.
    tensile_inplane_mpa: float
    # Across layers. The number that actually matters, because it is where
    # FDM parts break, and it is why orientation is declared per part.
    tensile_interlayer_mpa: float
    glass_transition_c: float
    # Fraction of short-term strength still available under continuous load at
    # DESIGN_TEMP_C. Empirical knockdown, deliberately conservative.
    sustained_knockdown: float
    notes: str

    def allowable_inplane_mpa(self) -> float:
        return self.tensile_inplane_mpa * self.sustained_knockdown / SUSTAINED_MARGIN_REQUIRED

    def allowable_interlayer_mpa(self) -> float:
        return self.tensile_interlayer_mpa * self.sustained_knockdown / SUSTAINED_MARGIN_REQUIRED


PETG = Material(
    name="PETG",
    tensile_inplane_mpa=45.0,
    tensile_interlayer_mpa=28.0,
    glass_transition_c=80.0,
    sustained_knockdown=0.35,
    notes=(
        "Floor, not the goal. Tg is adequate but PETG's creep resistance is "
        "mediocre and it is the least forgiving of the three if a wall ends up "
        "thin. Acceptable for the liner-adjacent and non-loaded parts."
    ),
)

ASA = Material(
    name="ASA",
    tensile_inplane_mpa=44.0,
    tensile_interlayer_mpa=30.0,
    glass_transition_c=105.0,
    sustained_knockdown=0.45,
    notes=(
        "Preferred. UV stable, which matters for an outdoor overnight that "
        "becomes a week, and Tg is far enough above tent temperature that the "
        "creep knockdown stays honest. Needs an enclosure."
    ),
)

PC_BLEND = Material(
    name="PC-blend",
    tensile_inplane_mpa=60.0,
    tensile_interlayer_mpa=38.0,
    glass_transition_c=110.0,
    sustained_knockdown=0.45,
    notes=(
        "Strongest option and the best choice for the boom arm specifically. "
        "Not UV stable bare — needs paint or a UV-stable topcoat if it will "
        "live outside for more than an overnight."
    ),
)

TPU_95A = Material(
    name="TPU 95A",
    tensile_inplane_mpa=30.0,
    tensile_interlayer_mpa=25.0,
    glass_transition_c=-30.0,
    sustained_knockdown=0.30,
    notes=(
        "Pole liner only. Chosen for compliance, not strength: it spreads clamp "
        "load into the pole coating so a printed edge never point-loads the "
        "rented pole. Never in a tension path."
    ),
)


# Per-part material and orientation. Orientation is a strength decision, so it
# is specified here alongside the material rather than left to the slicer
# operator. Rule: layer boundaries never normal to a principal tensile stress.
PART_SPEC: dict[str, dict[str, str]] = {
    "clamp_shell_fixed": {
        "material": "ASA",
        "orientation": "Pole axis normal to the plate.",
        "why": "Puts hoop tension in-plane. Standing it the other way would run "
               "the clamping load straight across layer boundaries.",
    },
    "clamp_shell_swing": {
        "material": "ASA",
        "orientation": "Pole axis normal to the plate.",
        "why": "Same hoop path as the fixed half.",
    },
    "over_center_lever": {
        "material": "PC-blend",
        "orientation": "Lever flat on the plate, pivot axis vertical.",
        "why": "Bending is in-plane. This part is also visible jewelry, so the "
               "flat face against the plate becomes the show face.",
    },
    "lever_link": {
        "material": "PC-blend",
        "orientation": "Flat on the plate, both pin axes vertical.",
        "why": "Pure tension between two pins, held in-plane.",
    },
    "pole_liner": {
        "material": "TPU 95A",
        "orientation": "Pole axis normal to the plate.",
        "why": "Compression only; orientation chosen for print reliability.",
    },
    "boom_arm": {
        "material": "PC-blend",
        "orientation": "Long axis flat on the plate. Never standing up.",
        "why": "Axial tension and bending both in-plane. Standing it up would "
               "put the entire suspended load across layer boundaries — this is "
               "the single most orientation-critical part in the assembly.",
    },
    "tray": {
        "material": "ASA",
        "orientation": "Tray face down on the plate.",
        "why": "Show surface against glass, and tray bending stays in-plane.",
    },
    "rear_handle_hook": {
        "material": "PC-blend",
        "orientation": "Hook profile flat on the plate.",
        "why": "Loaded in shear across the hook throat; in-plane keeps the "
               "shear off layer boundaries.",
    },
    "bayonet_collar": {
        "material": "ASA",
        "orientation": "Bayonet axis normal to the plate.",
        "why": "Lug bearing faces come out as in-plane walls, and the slots "
               "print without bridging.",
    },
    "drip_canopy": {
        "material": "ASA",
        "orientation": "Canopy convex side up, apex highest.",
        "why": "No supports on the visible upper surface, and every internal "
               "overhang stays under the 50 deg limit.",
    },
}
