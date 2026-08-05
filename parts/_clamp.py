"""
Shared clamp-shell geometry. Both halves are built from these.

The band, the hinge knuckles and the lever hardware are defined once here so the
two shells cannot drift apart. A knuckle width changed in one place moves the
mating gap in the other half automatically.
"""

from __future__ import annotations

from math import cos, radians, sin

from build123d import Align, Box, Cylinder, Part, Pos, Rot

from params import clamp as L
from params import clearances as C
from params import derived as D
from parts import _base


def safe_and(a, b):
    """Intersection that returns None instead of blowing up on an empty result.

    build123d's `&` yields None for a clean miss but an EMPTY COMPOUND in some
    cases, and intersecting an empty compound again raises
    "Cannot intersect shape with empty compound". Boolean chains have to tolerate
    both, or a legitimate empty region becomes a crash three lines later.
    """
    if a is None or b is None:
        return None
    try:
        r = a & b
    except ValueError:
        return None
    if r is None:
        return None
    try:
        if not r.solids() or r.volume <= 1e-9:
            return None
    except (AttributeError, TypeError):
        return None
    return r


def band(centre_deg: float, arc_deg: float) -> Part:
    """The wrap itself: shell bore out to shell OD, full band height."""
    d = D.compute()
    r_in = d.shell_bore_d / 2.0
    r_out = r_in + d.shell_wall_t
    return _base.sector(
        r_outer=r_out, r_inner=r_in, height=d.clamp_band_height,
        centre_deg=centre_deg, arc_deg=arc_deg,
    )


def shell_radii() -> tuple[float, float]:
    d = D.compute()
    r_in = d.shell_bore_d / 2.0
    return r_in, r_in + d.shell_wall_t


def at_angle(radius: float, angle_deg: float) -> tuple[float, float]:
    a = radians(angle_deg)
    return radius * cos(a), radius * sin(a)


def hinge_axis_radius() -> float:
    _, r_out = shell_radii()
    return r_out + L.HINGE_STANDOFF


def lever_axis_radius() -> float:
    _, r_out = shell_radii()
    return r_out + L.lever_standoff()


def knuckle(angle_deg: float, z0: float, height: float, radius: float,
            bore_d: float, axis_radius: float) -> Part:
    """A hinge or pivot knuckle: a bored post standing off the shell OD.

    Pin axis runs parallel to the pole axis, so the hinge swings the shell open
    in the plane the hand moves it. A knuckle on any other axis would need the
    installer to think about which way it opens.
    """
    x, y = at_angle(axis_radius, angle_deg)
    post = Cylinder(radius=radius, height=height,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))
    post -= Cylinder(radius=bore_d / 2.0, height=height * 3,
                     align=(Align.CENTER, Align.CENTER, Align.CENTER))
    return Pos(x, y, z0) * post


def pin_bore_cutter(angle_deg: float, z0: float, height: float,
                    bore_d: float, axis_radius: float) -> Part:
    """A SOLID cylinder on the pin axis, for re-cutting a bore after webbing.

    Deliberately not knuckle() with a tiny bore: knuckle() always subtracts an
    inner cylinder, so re-cutting with it leaves a hair-thin spike of material
    standing in the middle of the bore. Those slivers are disjoint bodies that
    fail validation, and if they ever slipped through they would be an
    unprintable whisker inside a hole a pin has to pass through.
    """
    x, y = at_angle(axis_radius, angle_deg)
    return Pos(x, y, z0) * Cylinder(
        radius=bore_d / 2.0, height=height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )


def knuckle_web(angle_deg: float, z0: float, height: float,
                axis_radius: float, width: float,
                toward_deg: float | None = None) -> Part:
    """Web tying a knuckle back into the band.

    Without this the pin load arrives at the shell through a single tangent line.
    The web spreads it into the band wall, which is the difference between a
    hinge that survives and one that tears its boss off.

    `angle_deg` is the parting line the web sits on, and `toward_deg` is this
    shell's own centre, which sets which side the inboard portion is trimmed to.
    See the comment below for why that trim is radial rather than a flat cut.

    Separately, what keeps the bored BOSSES clear of the other shell's band is
    L.HINGE_STANDOFF being derived from L.HINGE_BOSS_R — not anything here.
    """
    r_in, r_out = shell_radii()
    length = axis_radius - r_in * 0.9
    web = Box(length, width, height,
              align=(Align.MIN, Align.CENTER, Align.MIN))
    web = Rot(0, 0, angle_deg) * (Pos(r_in * 0.9, 0, z0) * web)

    if toward_deg is None:
        return web

    # The trim is RADIAL, not a flat cut, and the distinction is the whole point.
    #
    # The other shell's band occupies r <= r_out on the far side of the parting
    # line, so inboard of r_out the web must stay on its own side. But the shared
    # hinge axis sits out at axis_radius, PAST the parting line — so outboard of
    # r_out the web has to be free to cross, or it never reaches its own knuckle.
    #
    # Trimming the whole web at the parting plane (the obvious reading of "stay on
    # your own side") severs web from knuckle and leaves the boss floating as a
    # disjoint body. Both shells then fail validation — which is how this was
    # caught, and why the assembly check now validates before it measures.
    big = (axis_radius + width) * 4.0
    delta = ((toward_deg - angle_deg) + 180.0) % 360.0 - 180.0
    keep_align = Align.MIN if delta > 0 else Align.MAX
    own_side = Rot(0, 0, angle_deg) * Box(
        big, big, height * 4.0,
        align=(Align.CENTER, keep_align, Align.CENTER),
    )

    # Centred on THIS web's z range. Centring it at z=0 (the obvious mistake) means
    # it does not reach a knuckle high up the band, so `web & inboard` is empty and
    # `web - inboard` removes nothing — the web comes back fully untrimmed and its
    # inboard half crosses into the other shell's band. That is exactly what the
    # upper hinge web did, for 50 mm^3, while the lower one trimmed correctly.
    inboard = Pos(0, 0, z0 + height / 2.0) * Cylinder(
        radius=r_out, height=height * 4.0,
        align=(Align.CENTER, Align.CENTER, Align.CENTER))
    web_inner = safe_and(safe_and(web, inboard), own_side)
    web_outer = web - inboard

    if web_inner is None:
        return web_outer
    if web_outer is None:
        return web_inner
    return web_inner + web_outer


def boom_pad() -> Part:
    """Flat mounting pad at BOOM_DEG carrying four M5 heat-set bosses.

    Four bolts in a rectangle, not two: the boom arrives as a moment, and a
    rectangle resists it as a couple between bolt pairs. Two bolts would put that
    moment into bolt bending, which is how printed mounts fail at the fastener.
    """
    d = D.compute()
    _, r_out = shell_radii()
    band_h = d.clamp_band_height

    pad = Box(L.PAD_T, L.PAD_W, min(L.PAD_H, band_h),
              align=(Align.MIN, Align.CENTER, Align.CENTER))
    pad = Rot(0, 0, L.BOOM_DEG) * (
        Pos(r_out - 0.5, 0, band_h / 2.0) * pad
    )

    # Heat-set bosses, bored under the insert OD by the named interference so the
    # brass bites melted plastic rather than swimming in a loose hole.
    bore_d = L.M5_INSERT_D + C.M5_INSERT_TO_BOSS
    for dy in (-L.PAD_BOLT_DX / 2.0, L.PAD_BOLT_DX / 2.0):
        for dz in (-L.PAD_BOLT_DZ / 2.0, L.PAD_BOLT_DZ / 2.0):
            boss = Cylinder(radius=L.M5_BOSS_D / 2.0, height=L.PAD_T + 2.0,
                            align=(Align.CENTER, Align.CENTER, Align.MIN),
                            rotation=(0, 90, 0))
            hole = Cylinder(radius=bore_d / 2.0, height=L.M5_INSERT_DEPTH,
                            align=(Align.CENTER, Align.CENTER, Align.MIN),
                            rotation=(0, 90, 0))
            place = Rot(0, 0, L.BOOM_DEG) * Pos(r_out - 0.5, dy, band_h / 2.0 + dz)
            pad = pad + (place * boss) - (place * hole)

    return pad


def tether_anchor(angle_deg: float) -> Part:
    """Anchor for the captive steel tether — mandatory, independent retention.

    Deliberately NOT on the hinge or the lever. The tether has to catch the
    speaker with the clamp fully open, so it anchors into the band wall itself,
    on the load path that survives the mechanism being undone.
    """
    d = D.compute()
    _, r_out = shell_radii()
    x, y = at_angle(r_out - 1.0, angle_deg)

    lug = Cylinder(radius=6.5, height=7.0,
                   align=(Align.CENTER, Align.CENTER, Align.MIN))
    lug -= Cylinder(radius=2.6, height=21.0,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                    rotation=(0, 90, 0))
    return Pos(x, y, d.clamp_band_height * 0.5 - 3.5) * lug
