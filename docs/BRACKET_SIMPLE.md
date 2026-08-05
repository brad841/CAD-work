# Simple bracket — print, insert, bolt

**2 printed parts. 2 bolts. 2 inserts. No supports.**

Supersedes the over-centre/bayonet design, which is still in the repo (see
"Archived" at the bottom) but is not what you should print.

## Print

| Part | Mass | Orientation | Notes |
|---|---|---|---|
| `pole_bracket` | 299 g | **Saddle face DOWN on the bed** | The whole bracket: collar half, arm, saddle, backstop |
| `clamp_backer` | 56 g | Pole axis normal to the bed | Plain curved block |

**355 g total, one of each.** PETG. 0.4 mm nozzle, 0.2 mm layers, 4 perimeters,
40% infill. Print hot and slow — PETG's layer bond is what carries this.

Saddle-down is not a preference, it is what makes the part support-free: the
saddle floor becomes the first layer, the collar bore becomes a vertical hole with
nothing to bridge, and the arm, lip and backstop are all vertical walls. Bending
from the cantilevered speaker then runs parallel to the layers, so the interlayer
strength never governs. The only horizontal holes are the two 5.4 mm bolt bores.

Fits a 256 mm bed at 170 × 178 mm.

## Hardware

| Item | Spec | Qty |
|---|---|---|
| Heat-set inserts | M5 brass, 6.4 mm OD × 9.5 mm | 2 |
| Bolts | M5 × 25 mm socket cap, A2 stainless | 2 |
| Washers | **M5 penny/fender, 15 mm OD** | 2 |
| Pole tape | 2 mm adhesive EPDM or rubber, ~25 mm wide × 250 mm | 1 strip |

The washers are not optional. An M5 cap head bearing directly on PETG at 172 N
sits at 3.7 MPa — over the sustained allowable — and would slowly sink into the
flange until the clamp lost preload. A 15 mm washer drops that to 1.1 MPa.

The tape is what protects the rented pole. It also does real work: it lines the
bore so the clamp grips 60–66 mm, covering the whole 62–65 mm range with nothing
to measure and nothing to shim.

## Assemble

1. Melt the two M5 inserts into the pads on `pole_bracket` — the bores are cut
   0.05 mm under the insert OD so the brass bites melted plastic.
2. Line the bracket's bore and the backer's bore with the tape.
3. Put the bracket on the front of the pole, the backer behind it.
4. Two bolts, washers under the heads, from the back. Tighten alternately until
   it will not twist by hand. You need nowhere near M5's capacity — 172 N per
   bolt is finger-tight-plus.
5. Speaker in the saddle, back against the backstop.

Charging base sits in the saddle's open floor; the cable falls straight through.
That opening is why the base footprint never had to be measured.

## Numbers

| | |
|---|---|
| Load | 30.9 N (3.15 kg) |
| Moment about the pole | 3.38 N·m |
| Arm bending at the collar | 0.28 MPa — **11.2×** on the derated allowable |
| Bolt tension required | 172 N each (5× anti-slip, μ = 0.45) |
| Washer bearing | 1.12 MPa |
| Insert pull-out | 0.90 MPa vs 1.96 MPa interlayer |
| Pole contact pressure | 0.038 MPa vs a 0.60 powder-coat limit |
| Grip range | 60–66 mm |

Every margin is on the 5×-derated creep allowable, so 11.2× on the arm means
~56× on raw material strength. Verify with `scripts/check_bracket.py`.

## What this drops from the old design

Over-centre lever, steel link, 2 clevis pins, 2 R-clips, hinge pin, 2 retainers,
bayonet collar, spigot, 3 detent balls, 3 springs, pitch index plate, 2 pitch
pins, rear handle hook, TPU nose, 2 TPU liners, 3-piece shim set, pole gauge
coupon, 2 bayonet coupons.

**13 printed parts → 2. Level only, no pitch adjustment.**

It also deletes two whole unknowns: the pole OD (the clamp just closes on it) and
the four unpublished handle-recess dimensions (the speaker sits in a cup instead
of being hooked).

## Retargeting

Edit `SPEAKER_W` and `SPEAKER_D` in `params/bracket.py`. Every saddle dimension
derives from them. A round speaker like the Sonos One would want a circular
pocket rather than a rectangular one — that is a saddle-profile change, not a
parameter change.

## Archived

The over-centre design is still under `params/` and `parts/` (`clamp_shell_*`,
`bayonet_*`, `over_center_lever`, `cradle_*`, `tray`, `rear_handle_hook`) with its
own gauntlet at `scripts/gauntlet.py`. Kept for reference. Not the print target.
