"""
Shared export and validation plumbing for every part generator.

Each part module owns exactly one solid, exposes build() returning it, and is
regenerable in isolation. This module is the only place that knows how to write
a file or decide whether a solid is acceptable, so no generator can quietly ship
a broken body.

Validation is not advisory. export() refuses to write a solid that fails, which
means "the generator exited 0" and "the solid is sound" are the same statement.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from build123d import Part, export_step, export_stl

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"

# g/cm^3. Used only for mass reporting against the 400 g budget; the slicer's
# number is the one that counts and this is the sanity check on it.
DENSITY = {
    "PETG": 1.27,
    "TPU 95A": 1.21,
    "steel": 7.85,
}


class SolidRejected(RuntimeError):
    pass


def sector(r_outer: float, r_inner: float, height: float,
           centre_deg: float, arc_deg: float):
    """An annular sector with its axis on Z and its apex at the origin.

    build123d's `Cylinder(arc_size=...)` is avoided here on purpose: with
    Align.CENTER it centres the sector's BOUNDING BOX rather than its apex, so
    the sector silently lands off-axis. That produced a spigot whose lugs were
    displaced inside the body and vanished on union, with the part still passing
    validation because it was a perfectly sound solid of the wrong shape.

    Building the sector as an annulus intersected with two half-spaces through
    the origin has no alignment ambiguity. Valid for arc_deg < 180.
    """
    from build123d import Align, Box, Cylinder, Rot

    if not 0.0 < arc_deg < 180.0:
        raise ValueError(f"sector() needs 0 < arc < 180, got {arc_deg}")

    annulus = Cylinder(
        radius=r_outer, height=height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    if r_inner > 0.0:
        annulus -= Cylinder(
            radius=r_inner, height=height * 3,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
        )

    big = r_outer * 4.0
    start = centre_deg - arc_deg / 2.0
    end = centre_deg + arc_deg / 2.0

    # Keep the side of each plane that lies inside the wedge.
    keep_lo = Rot(0, 0, start) * Box(
        big, big, height * 3, align=(Align.CENTER, Align.MIN, Align.CENTER))
    keep_hi = Rot(0, 0, end) * Box(
        big, big, height * 3, align=(Align.CENTER, Align.MAX, Align.CENTER))

    return annulus & keep_lo & keep_hi


@dataclass
class PartReport:
    name: str
    material: str
    volume_mm3: float
    mass_g: float
    bbox: tuple[float, float, float]
    step: Path
    stl: Path

    def line(self) -> str:
        x, y, z = self.bbox
        return (f"{self.name:<24} {self.material:<9} {self.mass_g:>7.1f} g  "
                f"{x:>6.1f} x {y:>6.1f} x {z:>6.1f} mm")


def validate(solid: Part, name: str) -> None:
    """Refuse anything that is not a single sound watertight body."""
    problems: list[str] = []

    if solid is None:
        raise SolidRejected(f"{name}: build() returned None")

    if not solid.is_valid:
        problems.append("OCC reports the shape invalid")

    vol = solid.volume
    if vol <= 0.0:
        problems.append(f"volume is {vol:.3f} mm^3")

    # A watertight solid has closed shells and no free edges. Anything else will
    # slice into nonsense even if it renders fine on screen.
    try:
        n_solids = len(solid.solids())
        if n_solids != 1:
            problems.append(f"{n_solids} disjoint solids — expected exactly 1")
        for shell in solid.shells():
            if not shell.is_valid:
                problems.append("a shell is invalid")
    except Exception as e:  # noqa: BLE001
        problems.append(f"topology inspection failed: {e}")

    if problems:
        raise SolidRejected(f"{name}: " + "; ".join(problems))


def export(solid: Part, name: str, material: str,
           stl_note: str = "") -> PartReport:
    """Validate then write STEP + STL. Raises rather than writing junk."""
    validate(solid, name)

    OUT.mkdir(exist_ok=True)
    step = OUT / f"{name}.step"
    stl = OUT / f"{name}.stl"

    export_step(solid, str(step))
    export_stl(solid, str(stl))

    bb = solid.bounding_box()
    density = DENSITY.get(material, 1.27)
    mass = solid.volume / 1000.0 * density  # mm^3 -> cm^3 -> g

    return PartReport(
        name=name,
        material=material,
        volume_mm3=solid.volume,
        mass_g=mass,
        bbox=(bb.size.X, bb.size.Y, bb.size.Z),
        step=step,
        stl=stl,
    )


def cli(build_fn, name: str, material: str) -> int:
    """Standard entry point so every part module runs the same way."""
    try:
        report = export(build_fn(), name, material)
    except SolidRejected as e:
        print(f"REJECTED  {e}", file=sys.stderr)
        return 1
    print(report.line())
    print(f"  -> {report.step.relative_to(ROOT)}")
    print(f"  -> {report.stl.relative_to(ROOT)}")
    return 0
