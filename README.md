# Sonos Move 2 — 2.5 in tent pole mount

Suspended Move 2, over-centre wrap clamp into a 15° bayonet cradle. No adhesive,
no drilling, no tools, teardown under 30 s.

## Status

**Geometry complete for the core mount and Module B. Failure gauntlet passes.
Module A (drip canopy) is still blocked. Mass is 485 g against a 400 g budget.**

```bash
python3 -m venv .venv && .venv/bin/python -m pip install build123d

.venv/bin/python scripts/validate_params.py     # gate + bounds report
.venv/bin/python tests/test_gate0.py            # 69 checks
.venv/bin/python scripts/check_bayonet_fit.py   # 12 checks, tolerance both ways
.venv/bin/python scripts/check_clamp_fit.py     # 8 checks
.venv/bin/python scripts/assemble.py            # clash check + merged STEP
.venv/bin/python scripts/gauntlet.py            # failure critic
.venv/bin/python scripts/build_all.py           # all parts + mass (fails on budget)
```

All exit 0 except `build_all`, which fails on the mass budget — deliberately, see
below. Deliverables land in `out/`: STEP + STL per part, plus `assembly.step`.

## Gauntlet result

**PASS.** Weakest link: **lever ear bearing** in `clamp_shell_swing` at **1.65×**
on the derated allowable — 8.3× on the underlying material strength, since the
allowable already carries the 5× creep factor.

The gauntlet's one real idea is that **load duration picks the allowable**:

- **Sustained** members hold load for days at 55 °C. Creep governs: short-term
  strength knocked down for temperature and duration, then ÷5.
- **Transient** members are loaded only while a hand is on them — the lever while
  you close it, the hook during a knock. Yield governs, with ÷2.

Applying the creep allowable to the lever would demand a 3× heavier lever for a
load lasting four seconds. Applying the transient allowable to the link would be
dangerous. It caught one genuine violation during the mass pass: the detent pocket
left 1.20 mm of collar wall, under the 2.4 mm floor. `COLLAR_WALL` is now derived
from the pocket depth so it cannot drift again.

## Mass: 485 g against 400 g, and why I stopped there

Mass is not in your priority list — the four priorities are doesn't drop, doesn't
mar, survives an overnight, reads as a product — and "load path wins" is explicit.
So I did a real reduction pass (576 → 485 g) and then stopped rather than thin
anything the gauntlet checks.

What the pass actually did: band height 82 → 62.5 mm (it drives both shells *and*
both TPU liners, ~2.9 g per mm across four parts), tray floor from a solid plate to
a rib grid (192 → 87 g), hollow boom and root gusset, I-sectioned hook post, liner
base 3.0 → 2.4 mm.

Three honest routes to the remaining 85 g, in order of value:

1. **ASA instead of PETG** — removes the 1.174× wall multiplier outright. Worth
   roughly 60–70 g and it fixes the UV problem too. Needs an enclosure.
2. **Measure the two CoM numbers.** The boom arm is 148.9 mm because CoM is
   *bounded* 20 mm forward and 135 mm up. Real values are almost certainly kinder,
   and boom length cascades into band height, shells and liners.
3. Accept 485 g. Nothing about it is unsafe; it is 85 g of conservatism.

## What the unmeasured numbers cost

| Unknown | How it was handled |
|---|---|
| Pole OD | Designed as a **range** (62–65 mm) with a printed shim set. A shim only ever adds material, so guessing wrong thickens the stack rather than loosening the grip. `pole_gauge_coupon` measures it at install. |
| Handle recess ×4 | The hook stopped depending on it: 26 mm wide (any four-finger recess is wider), TPU nose that conforms to any lip radius, height set by the installer over 140–205 mm. |
| CoM ×2 | Bounded to the adverse corner of the speaker's own envelope. Legitimate because a rigid body's CoM is physically confined inside it — reality is kinder in every case. Costs ~20% extra moment. |
| Charging base ×6 | **Still blocks Module A.** No conservative direction exists: too small a canopy drips on 15 V indoor-rated electronics, too large fouls the bayonet. |

`scripts/validate_params.py` prints all 8 bounds in use with the safety argument
and the cost of each, every run, so a bound cannot quietly become a fact.

## Load path

Gravity does the work. The speaker sits upright **on** the tray and compresses into
the base contacts; the body is never clamped. Anti-tip engages the moulded rear
handle recess in **shear only**.

The load runs boom → pad → band → pole. **Neither the hinge pin nor the lever link
is in the suspended path** — they only close the band. That is why a failed lever
releases the *clamp* rather than dropping the speaker.

Secondary retention is independent: the tether's upper end chokes the **pole**
above the clamp, not the clamp, so it still catches with the clamp fully open.

| | |
|---|---|
| Suspended load | 30.9 N (3.15 kg) |
| Moment arm to bounded CoM | 148.9 mm |
| Overturning moment | 4.60 N·m |
| Band height | 62.5 mm |
| Required friction preload | 343 N (5× anti-slip, μ = 0.45) |
| Link tension | 172 N continuous → **steel, not printed** |
| Lever advantage | 4.46×, so 38 N of hand force |
| Pole contact pressure | **0.035 MPa** vs a 0.60 limit |
| Worst tip moment | 1.86 N·m at −20° |
| Bayonet stack, worst case | +0.55 / −0.15 mm |

## Documents

- `docs/GATE0_MEASUREMENT_PROTOCOL.md` — the numbers, and which still block
- `docs/HARDWARE_BOM.md` — every non-printed part, with grades and lengths
- `docs/PRINT_SHEET.md` — generated from live geometry: mass, orientation, why
- `docs/INSTALL_CARD.md` — two-motion install, one page
- `docs/TETHER_SPEC.md` — cable, shock numbers, and why it bypasses the clamp

## Two gates I cannot discharge here

**Physical gate.** Printing the pole-gauge and bayonet coupons and confirming fit
on the actual pole needs the printer and the pole in hand. The coupons are built
and are the first thing on the print sheet; the tolerance stack is *not* verified
until you run them.

**Aesthetic critic.** The brief asks for a blind A/B against unlabeled renders of
commercial mounts across five views. I cannot execute that honestly in this
environment: there is no renderer here, and I cannot view the commercial mount
images the comparison depends on. `out/assembly.step` opens in any viewer — that
judgement is yours, and I would rather hand you the model than fabricate a verdict.
