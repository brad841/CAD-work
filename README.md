# Sonos Move 2 — 2.5 in tent pole mount

Suspended Move 2 with the factory charging base integrated. Over-centre wrap
clamp into a 15° bayonet cradle. No adhesive, no drilling, no tools, teardown
under 30 s.

## Status: GATE 0 OPEN — geometry generation blocked

**0 of 21 required measurements are present.** No geometry has been written, and
none can be: the gate is enforced in code, not by convention.

```bash
python3 -m venv .venv && .venv/bin/python -m pip install build123d
.venv/bin/python scripts/validate_params.py    # exit 1 — names what is missing
.venv/bin/python tests/test_gate0.py           # 33 checks, all passing
```

To unblock: take the 21 measurements per
**[docs/GATE0_MEASUREMENT_PROTOCOL.md](docs/GATE0_MEASUREMENT_PROTOCOL.md)**,
write them into `params/gate0.py`, and re-run the validator until it exits 0.

### Why the gate is real and not a comment

Every unmeasured value is an `Unmeasured` object that raises on any arithmetic,
comparison, or cast. A part generator that tries to compute with a guessed pole
diameter does not produce a slightly-wrong solid — it raises
`UnmeasuredParameterError` naming the field and pointing at the protocol. This
is the mechanism that makes "do not assume" enforceable.

## What exists now

| Path | What it is |
|---|---|
| `params/gate0.py` | The 21 measured inputs. **The only file you edit** when the physical situation changes. |
| `params/clearances.py` | One named variable per mating pair. No hardcoded gaps anywhere else. |
| `params/derived.py` | Lazy arithmetic between the above. Boom moment, clamp couple, bayonet stack, pitch positions. |
| `params/material.py` | Creep-governed allowables at 55 °C, plus per-part material and print orientation. |
| `scripts/validate_params.py` | Gate enforcement + plausibility traps. Exit 0/1/2. |
| `tests/test_gate0.py` | Proves the tripwire fires and the derived arithmetic is right. |
| `docs/GATE0_MEASUREMENT_PROTOCOL.md` | How to produce each of the 21 numbers. |

Toolchain verified: build123d 0.11.1, STEP export available.

## Load path

Gravity does the work. The speaker sits **upright on** the tray and compresses
into the base contacts. The body is never clamped. Anti-tip capture engages the
moulded rear handle recess **in shear only**, never friction.

The clamp resists the overturning moment as a couple over the band height — a
taller band means lower contact pressure, which is what keeps the rented pole
undented. `derived.compute()` reports the numbers once Gate 0 closes.

Secondary retention is mandatory and independent: a captive steel tether that
catches the speaker **with the clamp fully open**.

## Sustained load, not yield

This hangs 3.15 kg for days in a hot tent, so creep governs. Design temperature
is **55 °C** — a closed tent in sun, not ambient. Allowables are short-term
strength knocked down for sustained load, temperature, and FDM anisotropy, then
divided by a 5× margin.

**No PLA.** Its Tg sits near tent temperature and it creeps under exactly this
dead load. PETG is the floor; ASA is preferred (UV stable); PC-blend for the
boom arm.

Print orientation is a strength decision and is declared per part in
`params/material.py` — clamp shells with the pole axis normal to the plate so
hoop tension is in-plane; boom arm long-axis flat, **never standing up**.

## Planned parts (none generated yet)

Clamp: shell halves · hinge pin · over-centre lever · lever link · TPU pole
liner · tension adjuster · M5 heat-set bosses
Dock: bayonet collar · detent spring pocket · index ring · release tab
Cradle: boom arm · tray · base retention lip · rear-handle hook · anti-slip
pads · pitch index plate and pin
Weather: drip canopy · cable channel · strain relief clip · drains
Detail: tether loop and anchor · cable clips · label recess

Charging is two modules on one bayonet interface. **Module B first** —
right-angle USB-C plug retainer with strain relief that breaks the water track
before the plug. Module A carries the unmodified factory base; because that base
is **rated indoor only**, its drip canopy is a primary requirement, not a
detail.

## Gates still ahead

1. **Gate 0** — 21 measurements. ← currently blocking
2. **Geometry** — one module per part, independently regenerable.
3. **Failure critic** — per loaded part and on the assembly. 5× sustained
   margin, no loaded wall under 2.4 mm, no overhang past 50°, no single-point
   failure the tether misses.
4. **Aesthetic critic** — assembly only, blind A/B against a commercial mount
   across five views. All five must win.
5. **Physical gate** — print a pole-gauge coupon and a bayonet coupon and
   confirm fit **on the actual pole** before committing the full set. This one
   requires a printer and the pole in hand; it cannot be discharged here.
