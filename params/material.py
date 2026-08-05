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
        "The declared floor, and the chosen build material. Tg is adequate but "
        "creep resistance is mediocre, so loaded sections are scaled up rather "
        "than left at ASA thickness. Not UV stable for a long exposure."
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


# The build material, chosen by the person printing it. PETG confirmed.
#
# PETG is the declared floor rather than the preference, so choosing it is not
# free: its sustained knockdown is 0.35 against ASA's 0.45, and derived.py turns
# that ratio into a thickness multiplier on every loaded section. The mount gets
# heavier instead of weaker. It also means UV is unmanaged — PETG embrittles in
# sustained sun, which is fine for an overnight and not fine for a season.
CHOSEN = PETG
CHOSEN_NOTES = (
    "PETG. Loaded sections scaled by derived.wall_scale() to hold the same 5x "
    "sustained margin ASA would have given at nominal thickness. Print hot and "
    "slow for interlayer strength — PETG's layer bond is the whole game here, "
    "and a fast cold PETG part is a delamination waiting for a hot afternoon."
)

# Per-part material and orientation. Orientation is a strength decision, so it
# is specified here alongside the material rather than left to the slicer
# operator. Rule: layer boundaries never normal to a principal tensile stress.
PART_SPEC: dict[str, dict[str, str]] = {
    "clamp_shell_fixed": {
        "material": "PETG",
        "orientation": "Pole axis normal to the plate.",
        "why": "Puts hoop tension in-plane. Standing it the other way would run "
               "the clamping load straight across layer boundaries.",
    },
    "clamp_shell_swing": {
        "material": "PETG",
        "orientation": "Pole axis normal to the plate.",
        "why": "Same hoop path as the fixed half.",
    },
    "over_center_lever": {
        "material": "PETG",
        "orientation": "Lever flat on the plate, pivot axis vertical.",
        "why": "Bending is in-plane. This part is also visible jewelry, so the "
               "flat face against the plate becomes the show face.",
    },
    "lever_link": {
        "material": "steel",
        "orientation": "NOT PRINTED — 3 mm steel plate, laser-cut profile.",
        "why": "172 N of sustained tension. A printed link reaches only ~1.5x on "
               "the derated allowable and its pin bearing already exceeds the "
               "sustained tensile limit. Steel gives 21x at 8 g.",
    },
    "pole_liner": {
        "material": "TPU 95A",
        "orientation": "Pole axis normal to the plate.",
        "why": "Compression only; orientation chosen for print reliability.",
    },
    "cradle_boom": {
        "material": "PETG",
        "orientation": "Long axis flat on the plate. Never standing up.",
        "why": "Axial tension and bending both in-plane. Standing it up would "
               "put the entire suspended load across layer boundaries — this is "
               "the single most orientation-critical part in the assembly.",
    },
    "tray": {
        "material": "PETG",
        "orientation": "Tray face down on the plate.",
        "why": "Show surface against glass, and tray bending stays in-plane.",
    },
    "rear_handle_hook": {
        "material": "PETG",
        "orientation": "Hook profile flat on the plate.",
        "why": "Loaded in shear across the hook throat; in-plane keeps the "
               "shear off layer boundaries.",
    },
    "bayonet_collar": {
        "material": "PETG",
        "orientation": "Bayonet axis normal to the plate.",
        "why": "Lug bearing faces come out as in-plane walls, and the slots "
               "print without bridging.",
    },
    "drip_canopy": {
        "material": "PETG",
        "orientation": "Canopy convex side up, apex highest.",
        "why": "No supports on the visible upper surface, and every internal "
               "overhang stays under the 50 deg limit.",
    },
    # --- Parts that exist because the pole and the speaker are unmeasured ---
    "pole_shim": {
        "material": "PETG",
        "orientation": "Curved face flat on the plate, arc lying down.",
        "why": "Pure compression between shell and liner, so orientation is a "
               "print-quality choice rather than a strength one. Printed in a "
               "0.5 / 1.0 / 1.5 mm set to cover the whole unconfirmed pole range.",
    },
    "hook_nose": {
        "material": "TPU 95A",
        "orientation": "Nose profile flat on the plate.",
        "why": "The compliant face that meets the handle lip. TPU because the "
               "lip radius is unpublished — the nose conforms to whatever is "
               "actually there instead of matching a number we never got.",
    },
    "pole_gauge_coupon": {
        "material": "PETG",
        "orientation": "Axis normal to the plate — same as the clamp shells.",
        "why": "This coupon is only honest if printed the way the shells will be, "
               "so its bore reflects the same dimensional behaviour.",
    },
    "bayonet_coupon_male": {
        "material": "PETG",
        "orientation": "Bayonet axis normal to the plate.",
        "why": "Same as the production spigot, so the coupon tests the real joint.",
    },
    "bayonet_coupon_female": {
        "material": "PETG",
        "orientation": "Bayonet axis normal to the plate.",
        "why": "Same as the production collar.",
    },
    "usbc_retainer": {
        "material": "PETG",
        "orientation": "Plug axis flat on the plate, capture jaws vertical.",
        "why": "Module B. Carries no suspended load, only cable sway, so this is "
               "a stiffness and water-shedding part. Jaws vertical keeps the "
               "snap fingers' bending in-plane.",
    },
}
