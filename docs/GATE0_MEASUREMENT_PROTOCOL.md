# Gate 0 — Measurement Protocol

> **Status update.** This document originally covered 21 blocking measurements.
> After the pole turned out to be unconfirmable and the Move 2's handle and CoM
> figures turned out to be genuinely unpublished, the gate was restructured.
> What is still required, and what is now optional:
>
> | Section | Status |
> |---|---|
> | 1. Pole OD ×6 + seam | **Superseded.** Designed as a range (62.0–65.0 mm) with a printed shim set. Do not measure; shim at install. |
> | 2. Pole wall + material | **Waived** by you as non-structural. Bounded to the thin/delicate case, which caps clamp pressure low and protects the pole. |
> | 3. Handle recess ×4 | **Optional.** Bounded conservatively; the hook is compliant and adjustable so it works without them. Measuring sheds ~20–30 % conservatism. |
> | 4. Charging base ×6 | **STILL REQUIRED.** Blocks Module A. No conservative direction exists — see below. |
> | 5. CoM ×2 | **Optional.** Bounded to the adverse corner of the speaker's envelope. Measuring sheds mass. |
>
> Sections 3 and 5 are worth doing if you have ten minutes and a caliper.
> Section 4 is the only one that blocks anything.
>
> **Why section 4 cannot be bounded:** every other unknown has a direction in
> which being wrong is safe. A canopy does not. Guess the footprint too small and
> water runs onto 15 V electronics that Sonos rates indoor only; guess it too
> large and the canopy fouls the bayonet and the silhouette. There is no
> conservative direction, so there is no honest bound, so it blocks.

This document is how to produce each number; `params/gate0.py` is where they go.

**Record everything in millimetres.** If you measure in inches, convert before
writing (`in × 25.4`), and write the converted number only. The validator traps
the obvious unit slips but it cannot catch all of them.

**Tools:** digital caliper (0.01 mm), steel rule, a length of string, your phone
camera, and a marker you can wipe off the pole. Nothing else.

---

## Why these 21 and not others

Each one changes geometry that cannot be fudged later:

| Group | What it decides |
|---|---|
| Pole OD ×6 | Shell bore, liner preload, whether the clamp grips an oval pole |
| Seam proud | Whether the liner straddles the weld or crushes it |
| Wall + material | How hard the clamp may squeeze before the rented pole dents |
| Handle recess ×4 | Whether the anti-tip hook engages in shear, or misses |
| Base ×6 | Drip canopy footprint, tray pocket, cable exit direction |
| CoM ×2 | Boom moment — multiplies into every structural number downstream |

---

## 1. Pole OD — six readings (3 heights × 2 axes)

A 2.5 in nominal pole measures anywhere from 62.0 to 65.0 mm in practice, and
it is rarely round. Averaging hides exactly the ovality the clamp has to grip
through, so we take six.

1. Decide where the clamp band will sit and mark it lightly — the speaker
   underside lands at **~2100 mm AGL**, so the band centre is roughly
   **2000 mm AGL**. Call this **MID**.
2. Mark **LO** 100 mm below MID and **HI** 100 mm above MID.
3. Find the weld seam. Run a fingernail up the tube — you will feel it before
   you see it. Mark its line down all three heights. This is **axis A**.
4. At each height take two caliper readings: **A** across the seam (jaws on the
   seam and directly opposite it), and **B** at 90° to it.
5. Close the caliper on the tube firmly enough to seat but not to compress the
   coating. Take each reading twice; if the pair disagrees by more than
   0.05 mm, take it again.

→ `POLE_OD_LO_A`, `POLE_OD_LO_B`, `POLE_OD_MID_A`, `POLE_OD_MID_B`,
  `POLE_OD_HI_A`, `POLE_OD_HI_B`

### Seam proud height

Lay the caliper's depth blade or a steel rule flat across the seam. Measure how
far the seam stands above the surrounding surface. Powder coat often buries it
to near-flush.

**If the seam is genuinely flush, write `0.0` — do not leave it unmeasured.**

→ `POLE_SEAM_PROUD`

## 2. Pole wall thickness and material

Wall thickness sets how hard the clamp may squeeze before the tube dents, and a
dented rented pole is priority-2 failure.

- **If an end is reachable:** caliper the wall directly at the tube end.
- **If not:** measure OD, then find the manufacturer's spec for the pole model.
  A typical 2.5 in steel tent pole runs 1.5–2.0 mm.
- **Last resort:** tap it. A ring means thin wall (<1.5 mm) and the clamp
  pressure needs to stay low; a dull thud means thicker.

Material matters because it sets what the liner is protecting: powder coat
scratches and chips, bare aluminium galls, galvanising is tougher than both.

→ `POLE_WALL_T`, `POLE_MATERIAL` (`'steel-powdercoat'`, `'steel-galv'`,
  `'aluminium-anodised'`, `'aluminium-bare'`)

## 3. Move 2 rear handle recess — four readings

This is the only place the mount touches the speaker other than the tray, and
it carries the anti-tip load **in shear**. Measure the real moulding, not the
press photos.

Stand the speaker upright on a flat table. The base plane is your Z datum.

1. **`HANDLE_RECESS_W`** — clear width of the recess opening at its widest.
   Caliper jaws inside the opening, spanning left to right.
2. **`HANDLE_RECESS_D`** — how far the recess cuts into the rear face. Caliper
   depth blade at the deepest point, referencing the outer rear surface.
3. **`HANDLE_LIP_R`** — radius of the moulded lip the hook will bear against.
   Use radius gauges if you have them; otherwise photograph the lip in profile
   against a rule and measure off the photo. **Round down**, never up: too small
   a modelled radius means the hook sits proud, too large means it rocks.
4. **`HANDLE_LIP_H_ABOVE_BASE`** — from the table surface up to the
   **load-bearing underside** of the lip, i.e. the face the hook pushes up
   against. Not the top of the opening. This one decides whether the hook
   engages at all.

Photograph all four with the caliper in frame. If a number later looks wrong,
the photo settles it without re-renting the pole.

## 4. Charging base — six readings

The base goes into Module A **unmodified**. It is rated indoor only, so the
canopy that keeps water off it is dimensioned entirely from these.

1. **`BASE_FOOTPRINT_X`** / **`BASE_FOOTPRINT_Y`** — outer footprint of the
   base where it meets a table. Left-right, then front-back. Include any rubber
   feet or flare at the bottom edge — the canopy overhangs the widest point.
2. **`BASE_HEIGHT`** — from the surface it sits on to the face the speaker's
   underside contacts.
3. **`BASE_PAD_OFFSET_X`** / **`BASE_PAD_OFFSET_Y`** — the charging contact pad
   is usually not centred. Measure from the footprint centre to the pad centre.
   Sign convention: **+X to the right, +Y aft (away from the speaker front)**.
   Write `0.0` for an axis where it genuinely is centred.
4. **`BASE_CABLE_EXIT`** — which way the USB-C cable leaves the base as it sits:
   `'aft'`, `'port'`, `'starboard'`, or `'under'`. This sets which way the drip
   loop runs and where the canopy drain goes. Getting it wrong routes water
   along the cable straight into the electronics.

## 5. Centre of mass — with the base installed

The number with the most leverage in the whole file. It multiplies against the
boom length to produce the overturning moment, which sizes the clamp, which
sizes the shells. A 15 mm error here propagates into every structural part.

**String-hang method — two orientations, intersect:**

1. Install the base on the speaker as it will actually hang. Tape it if needed
   so it cannot shift.
2. Tie a string loop around the assembly and hang it so it swings free. A body
   hanging from a single point always settles with its CoM directly below that
   point.
3. Photograph it **square-on**, camera level, no perspective tilt. The string
   line continued down through the body is one CoM line.
4. Re-hang from a clearly different point — rotate roughly 90° about the
   speaker's long axis. Photograph square-on again.
5. Overlay the two photos, extend both string lines, and mark where they cross.
   That intersection is the CoM.
6. Measure its position off the photo, scaled against a known dimension in
   frame. Use the verified **241 mm height** or **160 mm width** as your scale
   reference.

Report as offsets from the **speaker's base plane centre**:

- **`COM_OFFSET_Y`** — horizontal, **+ aft toward the pole**
- **`COM_OFFSET_Z`** — vertical, above the base plane

Sanity check before you write them: for a 241 mm speaker with a heavy driver
and battery low down, expect `COM_OFFSET_Z` somewhere around 95–125 mm. If your
number lands outside 30–200 mm the validator will reject it.

---

## Filling it in

Open `params/gate0.py`. Replace each `UNMEASURED(...)` call with the number:

```python
# before
POLE_OD_MID_A = UNMEASURED("POLE_OD_MID_A", "pole OD at clamp band centre, ...")

# after
POLE_OD_MID_A = 63.42
```

Strings for the two categorical fields:

```python
POLE_MATERIAL = "steel-powdercoat"
BASE_CABLE_EXIT = "aft"
```

Then run:

```bash
.venv/bin/python scripts/validate_params.py
```

- **exit 1** — still missing fields, it names them
- **exit 2** — all present but something is implausible, it says which and why
- **exit 0** — Gate 0 closed, geometry generation permitted

---

## If a measurement is genuinely unobtainable

Do not guess it into the file. Say which one and why, and it gets handled
explicitly — either the design changes so it stops mattering, or it becomes a
declared assumption recorded in the file with a comment, so the risk is visible
instead of buried in a plausible-looking number.
