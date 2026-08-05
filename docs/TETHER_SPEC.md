# Tether spec — mandatory, independent secondary retention

The requirement is precise and it drives the whole design of this part: the tether
must catch the speaker **with the clamp fully open.**

That single clause rules out the obvious build. If both ends attach to the clamp,
then the failure where the shells release and slide down the pole takes the tether
with them. A clamp-to-cradle tether only covers a bayonet release; it does nothing
for a clamp release, which is the more consequential of the two.

## So the tether does not touch the clamp

```
        pole
         ||
    [====]  <-- cable's upper eye: a choked loop around the POLE,
         ||      200-300 mm ABOVE the clamp band
         ||
    [CLAMP]  <-- tether passes it, anchored to neither shell
         ||
      \  ||
       \ ||   <-- slack, gathered in the shell's keeper lug
        \||
      [CRADLE]  <-- lower eye shackles to the boom's tether lug
```

- **Upper end:** choked loop around the pole itself, above the clamp. Choked, not
  clipped: it must grip under load rather than slide.
- **Lower end:** M5 screw-gate shackle to the tether lug on `cradle_boom`.
- **Keeper:** the lug on `clamp_shell_fixed` gathers the slack so the cable cannot
  swing or get lost. It is a keeper, **not** a load path.

## Parts

| Item | Spec | Qty |
|---|---|---|
| Cable | 2 mm 7×7 stainless (316), ~1.9 kN minimum breaking load | 450 mm |
| Eyes | Swaged copper or aluminium thimble eye, both ends | 2 |
| Shackle | M5 stainless screw-gate, 250 kg WLL | 1 |
| Keeper | Nylon P-clip or the printed lug on the fixed shell | 1 |

## Numbers

Static hang is 30.9 N. A drop onto the tether is not static: with ~40 mm of slack
and no compliance, a 3.15 kg mass arrests at roughly 15–20× static, so call it
**600 N** at the peak. A 2 mm 7×7 stainless cable at ~1.9 kN gives about **3×** on
that shock, and the swaged eye is the weak point at roughly 80–90% of cable
strength.

Keep the slack short. Halving the slack halves the arrest energy, and the cable is
the only thing in the assembly that is not designed to be loaded at all in normal
use.

## What it does and does not cover

Covers: bayonet released or failed; clamp lever released; clamp slid down the pole;
any single printed part in the suspended path failing.

Does **not** cover: the pole itself coming down, or the speaker being lifted out of
the tray by hand while the cradle stays put. Neither is a mount failure.

## Inspect it

Steel cable fails visibly before it fails structurally. Before each use, look for
broken strands at the swages — that is where they always start.
