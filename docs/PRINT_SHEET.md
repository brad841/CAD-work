# Print sheet

Material: **PETG**, with TPU 95A for the two compliant parts. Design temperature 55 C.

Print hot and slow. PETG's interlayer bond *is* the strength in the loaded
parts, and a fast cold PETG part is a delamination waiting for a hot
afternoon. 0.4 mm nozzle, 0.2 mm layers, 4 perimeters minimum on anything in
the load path, 40% infill or better in the clamp shells.

Orientation is a STRENGTH decision, not a convenience. Layer boundaries never
run normal to a principal tensile stress. Each choice and its reason:

| Part | Material | Qty | Mass | Orientation | Why |
|---|---|---|---|---|---|
| `clamp_shell_fixed` | PETG | 1 | 72.3 g | Pole axis normal to the plate. | Puts hoop tension in-plane. Standing it the other way would run the clamping load straight across layer boundaries. |
| `clamp_shell_swing` | PETG | 1 | 52.3 g | Pole axis normal to the plate. | Same hoop path as the fixed half. |
| `pole_liner` | TPU 95A | 2 | 27.4 g | Pole axis normal to the plate. | Compression only; orientation chosen for print reliability. |
| `over_center_lever` | PETG | 1 | 21.4 g | Lever flat on the plate, pivot axis vertical. | Bending is in-plane. This part is also visible jewelry, so the flat face against the plate becomes the show face. |
| `bayonet_collar` | PETG | 1 | 55.7 g | Bayonet axis normal to the plate. | Lug bearing faces come out as in-plane walls, and the slots print without bridging. |
| `cradle_boom` | PETG | 1 | 74.3 g | Long axis flat on the plate. Never standing up. | Axial tension and bending both in-plane. Standing it up would put the entire suspended load across layer boundaries — this is the single most orientation-critical part in the assembly. |
| `tray` | PETG | 1 | 80.7 g | Tray face down on the plate. | Show surface against glass, and tray bending stays in-plane. |
| `rear_handle_hook` | PETG | 1 | 54.3 g | Hook profile flat on the plate. | Loaded in shear across the hook throat; in-plane keeps the shear off layer boundaries. |
| `hook_nose` | TPU 95A | 1 | 1.2 g | Nose profile flat on the plate. | The compliant face that meets the handle lip. TPU because the lip radius is unpublished — the nose conforms to whatever is actually there instead of matching a number we never got. |
| `usbc_retainer` | PETG | 1 | 8.5 g | Plug axis flat on the plate, capture jaws vertical. | Module B. Carries no suspended load, only cable sway, so this is a stiffness and water-shedding part. Jaws vertical keeps the snap fingers' bending in-plane. |
| `pole_gauge_coupon` | PETG | 1 | 45.8 g | Axis normal to the plate — same as the clamp shells. | This coupon is only honest if printed the way the shells will be, so its bore reflects the same dimensional behaviour. |
| `bayonet_coupon_male` | PETG | 1 | 17.6 g | Bayonet axis normal to the plate. | Same as the production spigot, so the coupon tests the real joint. |
| `bayonet_coupon_female` | PETG | 1 | 38.5 g | Bayonet axis normal to the plate. | Same as the production collar. |

**Shims:** print `pole_shim_0p5mm`, `1p0mm` and `1p5mm` as one set. You will
use one or two of them, whichever the pole gauge selects. Curved face flat on
the plate, or a 0.5 mm shim will curl off the bed.

**Printed mount mass: 475 g**, against a 400 g budget — over by 75 g. The reason and the available trade are in the README; it is
not closed by thinning anything the gauntlet is checking.

## Print order — the coupons are a gate, not a suggestion

1. `pole_gauge_coupon` and both bayonet coupons. **Stop.** Fit them to the
   actual pole and to each other. Every clearance downstream depends on what
   these tell you about your machine.
2. Clamp group: both shells, both liners, the shim set, the lever.
3. Dock and cradle: collar, boom, tray, hook, TPU nose.
4. `usbc_retainer` (Module B).

## Supports

None needed on any part, by design: every unsupported overhang is under
50 deg and no bridge exceeds 12 mm.
If your slicer wants supports on a visible face, check the orientation against
the table before adding them — the fix is usually that the part is upside down.

## Not printed

`lever_link` is 3 mm steel. `out/lever_link.step` is a cutting profile, not a
print. See `docs/HARDWARE_BOM.md`.
