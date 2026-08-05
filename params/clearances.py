"""
CLEARANCES — one named variable per mating pair. No hardcoded gaps anywhere else.

Sign convention:
    positive = free space between the two faces
    negative = interference / designed preload

Every value here is a decision, and each carries the reason it has that value.
If a printed part binds or rattles, the fix is a line in this file, not a
number buried in a generator.

FDM reality baked into these numbers: a printed hole comes out undersize and a
printed boss comes out oversize, both by roughly one extrusion width of elephant
-foot and over-extrusion. Values assume a 0.4 mm nozzle at 0.2 mm layers and a
dimensionally-calibrated machine. VERIFY_BEFORE_COMMIT below flags the ones the
coupon print has to confirm, because they are the ones that bite.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# POLE INTERFACE — do not mar the rented pole
# ---------------------------------------------------------------------------
# The liner is the only thing that touches the pole. It is TPU so that clamp
# load spreads into the coating instead of concentrating on a printed edge.
# Negative: the liner is deliberately squeezed. This is the grip.
LINER_TO_POLE = -0.8
# TPU against powder-coated steel, dry. Deliberately the low end of the range
# quoted for elastomer-on-painted-steel: a pessimistic mu drives the required
# preload UP, which is the safe direction for "does not drop the speaker". It is
# also the wet-and-cold value, which is the condition that actually matters here.
LINER_FRICTION_COEFF = 0.45
# How much thinner the liner runs where the weld seam passes, so the seam is
# straddled rather than crushed. Added to POLE_SEAM_PROUD to size the groove.
LINER_SEAM_RELIEF = 0.4
# TPU liner sits in a shell pocket. Slight interference so it stays put with
# the clamp open and cannot fall into the grass.
LINER_TO_SHELL_POCKET = -0.15

# The shell bore is sized to the measured pole, never to 2.5 in nominal.
# This is the slack the shells need to swing closed around the liner before
# the lever takes up tension.
SHELL_BORE_TO_POLE_OPEN = 1.2

# ---------------------------------------------------------------------------
# CLAMP MECHANISM
# ---------------------------------------------------------------------------
HINGE_PIN_TO_BORE = 0.15          # free rotation, no slop that reads as wobble
LEVER_PIN_TO_BORE = 0.12          # tighter: slop here shows up as lever rattle
SHELL_HALF_TO_HALF_CLOSED = 0.6   # parting gap at full clamp; must not close to
                                  # zero or the shells bottom out and the liner
                                  # stops being preloaded
LEVER_TO_SHELL_SWEEP = 1.5        # knuckle clearance through the lever's arc
M5_INSERT_TO_BOSS = -0.05         # heat-set: bore slightly under insert OD

# ---------------------------------------------------------------------------
# BAYONET — the tolerance stack that has to be checked worst-case both ways
# ---------------------------------------------------------------------------
# Loose here and the speaker nods. Tight and it will not seat wet or cold.
BAYONET_LUG_RADIAL = 0.20         # lug flank to collar slot wall
BAYONET_LUG_AXIAL = 0.15          # lug top to slot ramp at full lock
BAYONET_SPIGOT_TO_BORE = 0.25     # cradle spigot into collar bore, drop-in fit
BAYONET_ANGULAR_OVERTRAVEL = 1.5  # deg past the detent, so the detent seats
                                  # against a hard stop rather than the lug
DETENT_BALL_TO_POCKET = 0.10      # ball must seat, not jam
DETENT_PRELOAD_CRUSH = -0.30      # spring pocket depth vs free length

# ---------------------------------------------------------------------------
# SPEAKER AND CHARGING INTERFACES — never clamp the body
# ---------------------------------------------------------------------------
# The tray locates the speaker; gravity holds it. These are locating gaps, not
# grip. Generous, because a cold wet speaker still has to drop in one-handed.
TRAY_TO_SPEAKER_FOOTPRINT = 1.0
# The hook engages the moulded handle lip in shear. Small gap: this is the
# anti-tip path and slack becomes tip-over travel.
HOOK_TO_HANDLE_LIP = 0.35
# Module A: pocket for the unmodified factory base. It must not be squeezed —
# it is a sealed consumer product, not a structural member.
BASE_TO_TRAY_POCKET = 0.5
# Module B: right-angle USB-C plug retainer. Snug, it carries no load but must
# not back out under cable sway.
USBC_PLUG_TO_RETAINER = 0.20

# ---------------------------------------------------------------------------
# WEATHER
# ---------------------------------------------------------------------------
# Canopy overhang past the base footprint on every side. Water must leave the
# canopy edge outboard of the electronics, not track back under it.
CANOPY_OVERHANG = 12.0
# Air gap under the canopy so a drop cannot bridge canopy to base by surface
# tension.
CANOPY_TO_BASE_AIR = 4.0
# Cable channel is oversize on purpose: a pinched cable is a water path.
CABLE_CHANNEL_TO_CABLE = 1.0

# ---------------------------------------------------------------------------
# PITCH INDEX
# ---------------------------------------------------------------------------
PITCH_PIN_TO_PLATE_HOLE = 0.15    # crisp index feel, no rock

# ---------------------------------------------------------------------------
# Coupon-print gate: these are the clearances that decide fit, and printed
# reality moves them. The physical gate exists to confirm exactly this list.
# ---------------------------------------------------------------------------
VERIFY_BEFORE_COMMIT = (
    "LINER_TO_POLE",
    "SHELL_BORE_TO_POLE_OPEN",
    "BAYONET_LUG_RADIAL",
    "BAYONET_LUG_AXIAL",
    "BAYONET_SPIGOT_TO_BORE",
    "M5_INSERT_TO_BOSS",
)
