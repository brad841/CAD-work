# Sonos Move 2 — 2.5 in tent pole mount

Suspended Move 2 with the factory charging base integrated. Over-centre wrap
clamp into a 15° bayonet cradle. No adhesive, no drilling, no tools, teardown
under 30 s.

## Status: core mount CLEAR to generate. Module A gated on 6 numbers.

```bash
python3 -m venv .venv && .venv/bin/python -m pip install build123d
.venv/bin/python scripts/validate_params.py    # exit 0, prints the full load path
.venv/bin/python tests/test_gate0.py           # 69 checks, all passing
```

Material: **PETG**, confirmed. Toolchain: build123d 0.11.1, STEP export verified.

## How the gate works now

Gate 0 originally demanded 21 measurements or nothing. Two of those turned out
to be unobtainable — the pole is rented and unconfirmable, and the Move 2's
handle and CoM figures are genuinely unpublished. So the gate now sorts numbers
into three kinds, and only one of them blocks:

| Kind | Meaning | Blocks? |
|---|---|---|
| `MEASURED(x)` | Someone put a caliper on it. | — |
| `BOUNDED(x)` | Not measured. A conservative substitute chosen so that being wrong makes the mount **stronger or looser**, never weaker or tighter. Every one records *why* it is safe and *what the conservatism costs*. | No |
| `UNMEASURED(x)` | No safe direction exists, so no guess can be made safe. | **Yes** |

The validator prints all 8 bounds in use on every run, each with its safety
argument, so a bound can never quietly become a fact months later.

### What was searched for, and not found

Sonos product/support pages, the Move 2 user guide, retailer spec tables,
GrabCAD, STLFinder, Printables, MakerWorld, Thingiverse, Creality Cloud, FCC
(model **RM044**), iFixit, and a dozen reviews.

**Confirmed:** base is 0.15 kg, 15 V 3 A, 45 W detachable adapter, 2 m cable,
and **indoor only**. It is a low-profile loop. The handle is a tapered recess
with a hollow top, room for four fingers; the *Move 1* equivalent is ~60 mm deep.

**Not published anywhere:** base footprint, height, contact-pad offsets, cable
exit direction, handle recess width/depth/lip radius/lip height, and CoM. No
Move 2 CAD exists publicly and there is no Move 2 teardown.

## How the unknowns were designed around

**Pole → a range, taken up by shims.** There is no pole diameter variable. The
design range is `62.0–65.0 mm` (2.44–2.56 in), the shells close on the **largest**
end, and a printed shim set (0.5 / 1.0 / 1.5 mm, stacking to 3.0 mm) brings a
smaller pole up to the bore. A shim only ever *adds* material between shell and
pole, so a wrong guess about the pole makes the stack thicker, never looser.
Changing the range means editing two numbers.

**Handle recess → a compliant, adjustable hook.** The hook stops depending on
the recess. It is 36 mm wide — narrower than any four-finger recess can be — its
nose is TPU so it conforms to whatever lip radius is actually there, and its
height is set by the installer on a slotted M5 adjustment over a 140–205 mm
range. Engagement becomes something you feel and lock, not something predicted.

**CoM → bounded to the adverse corner.** This is the one place a bound is as
good as a measurement, because the CoM of a rigid body is physically confined
inside its own envelope. It is placed at the corner producing the **largest**
overturning and tip moments: 20 mm forward of centre (the long-lever direction)
and 135 mm up (above the 95–125 mm expected). Reality will be kinder in every
case. Cost: the boom, band and shells carry ~20–30 % more moment than the truth.
Mass, not risk.

**Charging base → gated separately.** These six have *no* conservative
direction: a canopy that misses the real footprint drips on 15 V electronics
Sonos rates indoor only. So they still block — but they block **Module A alone**.
Module B, the right-angle USB-C plug retainer, needs none of them, which is
exactly why the brief says build B first.

## Current derived load path

At the bounded adverse CoM, in PETG:

| | |
|---|---|
| Suspended load | 30.9 N (3.15 kg) |
| Boom length to CoM | 125.5 mm |
| Overturning moment | 3.88 N·m |
| Clamp band height | 88.0 mm |
| Couple force (direct bearing) | 61 N |
| Required friction preload | 343 N (5× anti-slip, μ = 0.45) |
| Pole contact pressure | **0.025 MPa** vs 0.60 limit |
| Worst tip moment | 1.43 N·m at −20° |
| Worst hook shear | 10.6 N at −20° |
| Bayonet stack, worst case | +0.55 / −0.15 mm |

Pole contact pressure is computed from the **friction preload**, not the couple.
The couple is carried by direct bearing top-and-bottom and needs no friction;
sizing pressure off it instead understates the number ~10× and produces a
pole-marring check that cannot fail. The 0.025 MPa result is real and it is good
news — an 88 mm band spreads 343 N very thinly.

## PETG's cost, stated honestly

PETG's sustained knockdown is 0.35 against ASA's 0.45. `derived.wall_scale()`
turns that ratio into a **1.174× thickness multiplier** on every loaded section
(√ of the allowable ratio, since bending capacity goes as t²). Shell wall
4.69 mm, boom wall 4.23 mm. The mount gets heavier rather than weaker.

Two things PETG does not fix: UV is unmanaged, so sustained sun embrittles it —
fine for an overnight, not for a season. And its layer bond *is* the strength
here, so print hot and slow; a fast cold PETG part is a delamination waiting for
a hot afternoon.

## Load path

Gravity does the work. The speaker sits **upright on** the tray and compresses
into the base contacts. The body is never clamped. Anti-tip capture engages the
moulded rear handle recess **in shear only**, never friction. Secondary
retention is mandatory and independent: a captive steel tether that catches the
speaker **with the clamp fully open**.

## Layout

| Path | What it is |
|---|---|
| `params/gate0.py` | The design envelope. Measured / bounded / blocking, with each bound's safety argument. |
| `params/clearances.py` | One named variable per mating pair. No hardcoded gaps elsewhere. |
| `params/derived.py` | Lazy arithmetic only. Valid at both ends of the pole range. |
| `params/material.py` | Creep-governed allowables at 55 °C. Per-part material and print orientation. |
| `scripts/validate_params.py` | Gate + plausibility + the bounds report. Exit 0/1/2. |
| `tests/test_gate0.py` | 69 checks, including that the checks which should fail still can. |
| `docs/GATE0_MEASUREMENT_PROTOCOL.md` | How to produce any number you choose to measure. |

## Next

1. **Geometry** — Module B path first: clamp shells, liner, shim set, lever and
   link, bayonet collar, boom, tray, adjustable hook, USB-C retainer.
2. **Failure critic** — per loaded part and on the assembly, at −20° pitch.
3. **Aesthetic critic** — assembly only, blind A/B across five views.
4. **Physical gate** — pole-gauge and bayonet coupons, fit confirmed on the
   actual pole. Needs a printer and the pole in hand; cannot be discharged here.

### Worth measuring even though nothing blocks on it

The 4 handle-recess numbers and the 2 CoM numbers are **bounded, not required**.
Measuring them would let the boom and clamp shed the 20–30 % conservatism they
currently carry, which is real mass against the 400 g budget. The 6 base numbers
are **required** before Module A can exist at all.
