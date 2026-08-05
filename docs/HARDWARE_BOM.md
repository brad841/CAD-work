# Hardware BOM

Everything not printed. Quantities are per one complete mount.

Sizes derive from `params/` — if you change the pole range or the band height, the
pin lengths below change with it. Re-run `scripts/gauntlet.py`, which prints the
current values.

## Fasteners and pins

| # | Item | Spec | Qty | Notes |
|---|---|---|---|---|
| 1 | Hinge pin | M4 × 75 mm plain steel dowel, A2 stainless preferred | 1 | **Plain, not threaded.** A thread in a hinge bore chews the PETG boss every time the clamp opens. Band is 62.5 mm; 75 mm leaves ends to retain. |
| 2 | Hinge pin retainers | 4 mm E-clip or 1.6 mm split pin | 2 | One each end. Must be removable by hand — teardown is under 30 s, no tools. |
| 3 | Lever pivot pin | M5 × 45 mm clevis pin, steel | 1 | Through both lever ears (9 mm each) and the 20 mm blade gap. |
| 4 | Catch pin | M5 × 35 mm clevis pin, steel | 1 | Through the catch boss (19.8 mm) plus the link. |
| 5 | Clevis pin retainers | 5 mm R-clip | 2 | Hand-removable. |
| 6 | Collar bolts | M5 × 16 mm socket cap, A2 stainless | 4 | Into heat-set inserts on the clamp pad, 30 × 42 mm centres. |
| 7 | Heat-set inserts | M5 brass, 6.4 mm OD × 9.5 mm | 4 | Bores are cut 0.05 mm **under** insert OD so the brass bites melted plastic. |
| 8 | Pitch hinge pin | M6 × 55 mm clevis pin, steel | 1 | Double shear in the boom fork. |
| 9 | Pitch index pin | M5 × 55 mm clevis pin, steel | 1 | The part you pull to change pitch. R-clip, no tool. |
| 10 | Hook clamp bolts | M5 × 20 mm socket cap + nyloc | 2 | Clamp the hook post at the height you find. |
| 11 | Detent balls | 4 mm stainless ball | 3 | One per bayonet lug. |
| 12 | Detent springs | 4 mm OD × 6 mm free length compression, ~5 N | 3 | Pocket is 3.2 mm deep, so ~2.8 mm of crush. |
| 13 | Anti-slip pads | 22 mm dia × 1.5 mm EPDM or silicone, adhesive-backed | 4 | Sit in 1.2 mm recesses so they are proud by ~0.3 mm only. |

## Steel link — not a purchased part

| # | Item | Spec | Qty |
|---|---|---|---|
| 14 | Lever link | 3 mm mild steel plate, laser-cut from `out/lever_link.step` | 1 |

27.6 mm pin centres, 8 mm strap, two Ø5.12 mm bores. Deburr both bores — a sharp
steel edge will chew the M5 clevis pin and the PETG boss it works against.

Sized in steel because it holds **172 N continuously**. A printed PETG link at the
same duty reaches only ~1.5× over the 5×-derated allowable even at 8 × 10 mm, and
its pin bearing exceeds the sustained tensile allowable outright. Steel gives 21×
at 8 g. If you have no cutter, file it from 3 mm flat bar — it is two holes and a
rounded rectangle.

## Tether

See `docs/TETHER_SPEC.md`. Summary: 2 mm 7×7 stainless cable, 450 mm, two swaged
thimble eyes, one M5 stainless screw-gate shackle.

## Deliberately absent

- **No adhesive** anywhere structural. The TPU liner and hook nose are press fits
  so they stay replaceable.
- **No threadlocker.** The over-centre lever holds itself; nothing relies on a
  fastener staying torqued.
- **No thread cut into any printed part.** Every threaded joint goes into a brass
  heat-set insert or a nyloc nut.
