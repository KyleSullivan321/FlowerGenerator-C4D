"""Build a whole flower from a parameter dict and a bloom value.

build(params, bloom) returns {part name: Mesh}. Angles in params are degrees; lengths cm.
Everything here is deterministic for a given seed, so scrubbing and rendering always match.
"""

import math
import random

from . import geom as g
from .layering import Ceiling, phi_span, spans_overlap

GOLDEN = math.radians(137.50776)
R = math.radians

PARTS = ("Stem", "Leaves", "Thorns", "Calyx", "Petals", "Stamens", "Disc")


def _rng(seed, salt, k=0):
    return random.Random((seed * 1000003 + salt * 7919 + k * 104729) & 0xFFFFFFFF)


# ---- stem ----------------------------------------------------------------------------------

class Stem:
    """Turtle-integrated stem path with transported frames. lin is the 0..1 growth."""

    def __init__(self, P, lin):
        self.L = P["stem_length"] if P["stem_on"] else 0.0
        self.l = self.L * lin
        self.r0 = P["stem_radius"]
        self.taper = P["stem_taper"]
        n = max(2, int(P["stem_segments"]))
        self.n = n
        rnd = _rng(P["seed"], 11)
        ph1 = rnd.uniform(0, g.TAU)
        ph2 = rnd.uniform(0, g.TAU)
        bdir = R(P["stem_bend_dir"])
        d = (math.cos(bdir), 0.0, math.sin(bdir))
        K = g.norm(g.cross((0.0, 1.0, 0.0), d))
        T = (0.0, 1.0, 0.0)
        N = d
        pos = (0.0, 0.0, 0.0)
        self.pts = [pos]
        self.frames = [(T, N)]
        L = max(self.L, 1e-6)
        l = self.l
        ds = l / n
        bend = R(P["stem_bend"])
        nod = R(P["stem_nod"])
        wig = R(P["stem_wiggle"])
        wf = P["stem_wiggle_freq"]
        coil_total = P["stem_unfurl"] * 2.6 * math.pi * (1.0 - lin)
        coil_len = min(l, 0.35 * L)
        ax1 = (1.0, 0.0, 0.0)
        ax2 = (0.0, 0.0, 1.0)
        for k in range(n):
            s = (k + 0.5) * ds
            a = bend / L * ds
            if l > 1e-6 and s > 0.85 * l:
                a += nod / (0.15 * l) * ds
            if coil_total and coil_len > 1e-6 and s > l - coil_len:
                w = (s - (l - coil_len)) / coil_len
                a -= coil_total * 2.0 * w / coil_len * ds
            if a:
                T = g.rotate(T, K, a)
                N = g.rotate(N, K, a)
            if wig and wf:
                w1 = wig * g.TAU * wf / L * math.cos(g.TAU * wf * s / L + ph1) * ds
                w2 = wig * g.TAU * wf / L * math.cos(g.TAU * wf * 0.7 * s / L + ph2) * ds * 0.7
                T = g.rotate(T, ax1, w1)
                N = g.rotate(N, ax1, w1)
                T = g.rotate(T, ax2, w2)
                N = g.rotate(N, ax2, w2)
            N = g.norm(g.sub(N, g.mul(T, g.dot(N, T))))
            pos = g.add(pos, g.mul(T, ds))
            self.pts.append(pos)
            self.frames.append((T, N))

    def radius(self, s):
        return self.r0 * g.lerp(1.0, self.taper, s / self.L if self.L > 1e-9 else 1.0)

    def sample(self, s):
        """Position, tangent and normal at arc length s (s <= current length)."""
        if self.l <= 1e-9:
            return self.pts[0], self.frames[0][0], self.frames[0][1]
        f = g.clamp01(s / self.l) * self.n
        i = min(int(f), self.n - 1)
        t = f - i
        p = g.add(self.pts[i], g.mul(g.sub(self.pts[i + 1], self.pts[i]), t))
        T = g.norm(g.add(g.mul(self.frames[i][0], 1 - t), g.mul(self.frames[i + 1][0], t)))
        N = g.norm(g.add(g.mul(self.frames[i][1], 1 - t), g.mul(self.frames[i + 1][1], t)))
        return p, T, N

    def mesh(self, sides):
        m = g.Mesh()
        if self.l <= 1e-6:
            return m
        radii = [self.radius(self.l * i / self.n) for i in range(self.n + 1)]
        g.tube(m, self.pts, radii, sides, normal0=self.frames[0][1], cap_start=True,
               weights=[i / self.n for i in range(self.n + 1)])
        return m


# ---- leaves and thorns ---------------------------------------------------------------------

def _leaf_slots(P):
    n = int(P["leaf_count"])
    arr = int(P["leaf_arrangement"])
    per = 1
    if arr == 1:
        per = 2
    elif arr == 3:
        per = max(2, int(P["leaf_whorl"]))
    groups = max(1, (n + per - 1) // per)
    slots = []
    for i in range(n):
        q = i // per
        f = q / (groups - 1) if groups > 1 else 0.0
        if arr == 0:
            psi = i * math.pi
        elif arr == 1:
            psi = (i % 2) * math.pi + q * math.pi / 2.0
        elif arr == 2:
            psi = i * GOLDEN
        else:
            psi = (i % per) * g.TAU / per + q * math.pi / per
        slots.append((f, psi))
    return slots


def build_leaves(P, stem, lin_ext):
    m = g.Mesh()
    if not P["leaf_on"] or stem.L <= 0:
        return m
    L = stem.L
    res = int(P["leaf_res"])
    for i, (f, psi) in enumerate(_leaf_slots(P)):
        rnd = _rng(P["seed"], 21, i)
        jit = P["leaf_random"]
        s = L * g.lerp(P["leaf_start"], P["leaf_end"], f)
        s = min(max(s + rnd.uniform(-0.03, 0.03) * L * jit, 0.0), L)
        if s >= stem.l:
            continue
        age = g.smooth((lin_ext * L - s) / max(P["leaf_dur"] * L, 1e-6))
        if age <= 0.0:
            continue
        p, T, N = stem.sample(s)
        Bn = g.norm(g.cross(N, T))
        psi += rnd.uniform(-0.3, 0.3) * jit
        O = g.norm(g.add(g.mul(N, math.cos(psi)), g.mul(Bn, math.sin(psi))))
        X = g.norm(g.cross(O, T))
        ang = R(g.lerp(6.0, P["leaf_angle"] * (1 + rnd.uniform(-0.3, 0.3) * jit), age))
        D = g.norm(g.rotate(T, X, -ang))
        if g.dot(D, O) < 0:  # make sure the leaf leans out toward O
            D = g.norm(g.rotate(T, X, ang))
        Z = g.cross(X, D)
        size = g.lerp(1.0, P["leaf_top_scale"], s / L) * (1.0 + rnd.uniform(-0.25, 0.25) * jit)
        r = stem.radius(s)
        base = g.add(p, g.mul(O, r * 0.6))
        pet = P["leaf_petiole"] * size * age
        if pet > 1e-4:
            end = g.add(base, g.mul(D, pet))
            pr = max(r * 0.28, 0.01)
            g.tube(m, [base, g.add(base, g.mul(D, pet * 0.5)), end], [pr, pr * 0.85, pr * 0.7], 4)
            base = end
        shape = {
            "length": P["leaf_length"] * size * g.lerp(0.12, 1.0, age),
            "width": P["leaf_width"] * size * g.lerp(0.25, 1.0, age),
            "width_pos": P["leaf_width_pos"], "base": P["leaf_base"], "tip": P["leaf_tip"],
            "serration": int(P["leaf_serration"]), "serration_depth": P["leaf_serration_depth"],
            "fold": R(g.lerp(75.0, P["leaf_fold"], age)),
            "curl": R(g.lerp(50.0, -P["leaf_droop"] * (1 + rnd.uniform(-0.3, 0.3) * jit), age)),
            "tip_curl": 0.0,
            "twist": R(P["leaf_twist"] * age * (1 + rnd.uniform(-0.5, 0.5) * jit)),
            "ruffle": P["leaf_ruffle"] * age, "ruffle_freq": 4.0, "phase": rnd.uniform(0, g.TAU),
        }
        if shape["length"] <= 1e-5 or shape["width"] <= 1e-5:
            continue
        grid, w = g.build_blade(shape, res, 7)
        grid = [[g.frame_apply(base, X, D, Z, q) for q in row] for row in grid]
        m.add_grid(grid, w)
    return m


def build_thorns(P, stem):
    m = g.Mesh()
    if not P["thorn_on"] or stem.L <= 0:
        return m
    L = stem.L
    rnd = _rng(P["seed"], 31)
    jit = P["thorn_random"]
    for i in range(int(P["thorn_count"])):
        s = L * rnd.uniform(P["thorn_start"], P["thorn_end"])
        psi = rnd.uniform(0, g.TAU)
        size = 1.0 + rnd.uniform(-0.5, 0.5) * jit
        tilt = R(P["thorn_angle"] + rnd.uniform(-20, 20) * jit)
        if s >= stem.l:
            continue
        age = g.smooth((stem.l - s) / (0.06 * L))
        if age <= 0:
            continue
        p, T, N = stem.sample(s)
        Bn = g.norm(g.cross(N, T))
        O = g.norm(g.add(g.mul(N, math.cos(psi)), g.mul(Bn, math.sin(psi))))
        k = g.norm(g.cross(O, T))
        r = stem.radius(s)
        ln = P["thorn_length"] * size * age
        wd = P["thorn_width"] * size * age * 0.5
        head = g.rotate(O, k, tilt)
        pos = g.add(p, g.mul(O, r * 0.5))
        path = [pos]
        radii = [wd]
        steps = 4
        for j in range(1, steps + 1):
            pos = g.add(pos, g.mul(head, (ln + r * 0.5) / steps))
            head = g.rotate(head, k, R(P["thorn_hook"]) / steps)
            path.append(pos)
            radii.append(wd * (1.0 - j / steps) ** 1.3)
        g.tube(m, path, radii, 5)
    return m


# ---- flower head ---------------------------------------------------------------------------

def _petal_layout(P):
    """List of (layer fraction 0 outer..1 inner, azimuth) from outside in."""
    out = []
    if int(P["petal_arrangement"]) == 0:
        n = max(1, int(P["petal_count"]))
        div = R(P["petal_divergence"])
        for k in range(n):
            out.append((k / (n - 1) if n > 1 else 0.0, k * div))
    else:
        wh = max(1, int(P["petal_whorls"]))
        per = max(1, int(P["petal_per_whorl"]))
        for mw in range(wh):
            for j in range(per):
                f = mw / (wh - 1) if wh > 1 else 0.0
                f += (j / per) * (0.5 / wh if wh > 1 else 0.0)
                out.append((min(f, 1.0), g.TAU * j / per + mw * math.pi / per))
    return out


def _place(grid, attach, X, D):
    Z = g.cross(X, D)
    return [[g.frame_apply(attach, X, D, Z, q) for q in row] for row in grid]


def _space_out(path, old, min_step):
    """After clamping, keep consecutive centerline points apart (along their unclamped
    direction) so a tube never gets a zero-length segment."""
    for k in range(1, len(path)):
        d = g.sub(path[k], path[k - 1])
        if g.dot(d, d) < min_step * min_step:
            u = g.sub(old[k], old[k - 1])
            ul = math.sqrt(g.dot(u, u))
            if ul < 1e-12:
                u, ul = (0.0, 1.0, 0.0), 1.0
            path[k] = g.add(path[k - 1], g.mul(u, min_step / ul))


def build_head(P, b, stats):
    """Return head meshes in head space: Y up, origin at the receptacle center."""
    calyx = g.Mesh()
    petals = g.Mesh()
    stamens = g.Mesh()
    disc = g.Mesh()
    rr = P["receptacle_radius"]
    os_, oe = P["open_start"], P["open_end"]
    span = max(oe - os_, 1e-6)
    avoid = P["avoid_intersections"]
    seed = P["seed"]
    layout = _petal_layout(P)
    rho_max = rr + 1.4 * max(P["petal_length"] * (1 + P["petal_random"]), P["sepal_length"],
                             P["stamen_length"] + P["anther_size"], P["pistil_length"]) + 0.01
    # Near the receptacle the layers can only be as far apart as their attach angles.
    n_layers = max(1, len(layout))
    attach_step = abs(R(P["petal_attach_outer"] - P["petal_attach_inner"])) / n_layers
    ceil = Ceiling(rho_max, P["petal_thickness"], gap_cap=min(R(3.0), max(0.9 * attach_step, R(1.0))))
    res_u = int(P["petal_res"])
    res_v = int(P["petal_res_v"])
    if P["petal_ruffle"] >= 0.03 and P["petal_ruffle_freq"] > 0.0:
        # Ruffle flutes fan out around the rim, so they need columns (about 4 per wave) and enough
        # rows to bend smoothly. Decided from the parameter, not the bloom, so the topology never
        # changes while animating.
        res_u = max(res_u, 22)
        res_v = max(res_v, int(math.ceil(4.0 * P["petal_ruffle_freq"])) + 3)

    # Receptacle: a lathe from the stem tip up over a sphere of radius rr.
    sides = max(6, int(P["stem_sides"]) * 2)
    r_tip = P["stem_radius"] * P["stem_taper"] if P["stem_on"] else rr * 0.3
    prof = [(r_tip, -1.5 * rr), (max(r_tip, 0.55 * rr), -1.2 * rr), (0.85 * rr, -0.8 * rr)]
    for k in range(7):
        th = R(135.0) * (1.0 - k / 7.0)
        prof.append((rr * math.sin(th), rr * math.cos(th)))
    prof.append((0.0, rr))
    grid = []
    for (pr, py) in prof:
        grid.append([(pr * math.cos(g.TAU * j / sides), py, pr * math.sin(g.TAU * j / sides)) for j in range(sides)])
    calyx.add_grid(grid, close_v=True)

    def sph_dir(theta, phi):
        st = math.sin(theta)
        return (st * math.cos(phi), math.cos(theta), st * math.sin(phi))

    # Pass 1: build every sepal and petal unclamped, outside in.
    layers = []  # (target mesh, grid, weights, group, phi)
    if P["sepal_on"] and P["sepal_length"] > 0:
        ns = max(1, int(P["sepal_count"]))
        ps = g.smooth(g.window(b, os_ - 0.15, os_ + 0.3 * span))
        rot0 = math.pi / ns
        for k in range(ns):
            rnd = _rng(seed, 41, k)
            phi = g.TAU * k / ns + rot0 + rnd.uniform(-0.1, 0.1)
            ta = R(min(P["petal_attach_outer"] + 25.0, 170.0))
            to = R(g.lerp(P["bud_angle"] + 4.0, P["sepal_open"], ps))
            shape = {"length": P["sepal_length"] * (1 + rnd.uniform(-0.1, 0.1)), "width": P["sepal_width"],
                     "width_pos": 0.3, "base": 0.7, "tip": 0.9, "cup": R(g.lerp(80.0, 40.0, ps)),
                     "curl": R(g.lerp(P["bud_curl"], P["sepal_curl"], ps)), "tip_curl": R(g.lerp(0.0, -20.0, ps))}
            grid, w = g.build_blade(shape, 8, 5)
            attach = g.mul(sph_dir(ta, phi), rr)
            grid = _place(grid, attach, (-math.sin(phi), 0.0, math.cos(phi)), sph_dir(to, phi))
            layers.append((calyx, grid, w, 1000 + k, phi))

    p_inner = 1.0
    for k, (f, phi) in enumerate(layout):
        rnd = _rng(seed, 51, k)
        start = os_ + P["stagger"] * span * f
        dur = span * (1.0 - P["stagger"])
        p = g.smooth(g.window(b, start, start + dur))
        p_inner = p
        size = g.lerp(1.0, P["petal_inner_size"], f) * (1.0 + rnd.uniform(-1, 1) * P["petal_random"])
        size *= g.lerp(P["bud_petal_size"], 1.0, p)
        size *= g.lerp(1.0 - 0.45 * f, 1.0, p)
        phi += R(rnd.uniform(-1, 1) * P["petal_rot_random"]) * 0.5
        ta = R(g.lerp(P["petal_attach_outer"], P["petal_attach_inner"], f))
        open_k = g.lerp(P["petal_open_outer"], P["petal_open_inner"], f ** P["petal_open_curve"])
        open_k += rnd.uniform(-1, 1) * P["petal_rot_random"]
        to = R(g.lerp(P["bud_angle"] * (1.0 - 0.6 * f), open_k, p))
        cup = P["petal_cup"]
        shape = {
            "length": P["petal_length"] * size, "width": P["petal_width"] * size,
            "width_pos": P["petal_width_pos"], "base": P["petal_base"], "tip": P["petal_tip"],
            "notch": P["petal_notch"], "fringe": int(P["petal_fringe"]), "fringe_depth": P["petal_fringe_depth"],
            "cup": R(g.lerp(max(cup, 90.0), cup, p)),
            "curl": R(g.lerp(P["bud_curl"], P["petal_curl"], p)),
            "tip_curl": R(g.lerp(0.0, P["petal_tip_curl"], p)),
            "twist": R(P["petal_twist"] * p),
            "ruffle": P["petal_ruffle"] * g.lerp(0.3, 1.0, p), "ruffle_freq": P["petal_ruffle_freq"],
            "phase": rnd.uniform(0, g.TAU),
        }
        if shape["length"] <= 1e-5 or shape["width"] <= 1e-5:
            continue
        grid, w = g.build_blade(shape, res_u, res_v)
        attach = g.mul(sph_dir(ta, phi), rr)
        grid = _place(grid, attach, (-math.sin(phi), 0.0, math.cos(phi)), sph_dir(to, phi))
        layers.append((petals, grid, w, k, phi))

    # Pass 2: each layer gets a floor for the overlapping layers still inside it, then is
    # clamped under the layers outside it.
    has_center = (P["stamen_on"] and P["stamen_count"] > 0) or P["pistil_on"] or P["disc_on"]
    # With avoidance on, a pistil too fat for the bud is scaled to fit (half the receptacle radius).
    p_rad, p_stig = P["pistil_radius"], P["stigma_size"]
    if avoid:
        fit = 0.5 * rr / max(p_rad + 0.6 * p_stig, 1e-9)
        if fit < 1.0:
            p_rad, p_stig = p_rad * fit, p_stig * fit
    core_r = 0.0
    if P["stamen_on"] and P["stamen_count"] > 0 and P["stamen_length"] > 0:
        core_r = P["stamen_radius"] + P["anther_size"] * 0.5
    if P["pistil_on"] and P["pistil_length"] > 0:
        core_r = max(core_r, p_rad + p_stig * 0.6)
    spans = [phi_span(grid, phi) for (_, grid, _, _, phi) in layers] if avoid else []
    for idx, (mesh, grid, w, grp, phi) in enumerate(layers):
        if avoid:
            inside = sum(1 for j in range(idx + 1, len(layers)) if spans_overlap(spans[idx], spans[j]))
            stats["moved"] += ceil.clamp_grid(grid, inside + (1 if has_center else 0), core_r=core_r, core_from=1.2 * rr, rho_min=rr)
            ceil.add_grid(grid)
        mesh.add_grid(grid, w, group=grp)

    # Stamens: filaments with anthers, inside the innermost petals.
    inner_t = R(max(P["petal_attach_inner"], 5.0)) * 0.85
    pst = min(g.smooth(g.window(b, os_ + 0.3 * span, oe)), p_inner)
    if P["stamen_on"] and P["stamen_count"] > 0 and P["stamen_length"] > 0:
        n = int(P["stamen_count"])
        for k in range(n):
            rnd = _rng(seed, 61, k)
            fr = math.sqrt((k + 0.5) / n)
            th0 = inner_t * fr
            phi = k * GOLDEN
            ln = P["stamen_length"] * g.lerp(0.15, 1.0, pst) * (1.0 + rnd.uniform(-0.12, 0.12))
            th = R(P["stamen_spread"]) * fr * pst
            pos = g.mul(sph_dir(th0, phi), rr * 0.97)
            path = [pos]
            steps = 5
            for j in range(steps):
                th_j = th + R(P["stamen_curve"]) * pst * (j / steps)
                pos = g.add(pos, g.mul(sph_dir(th_j, phi), ln / steps))
                path.append(pos)
            if avoid:
                # The base is clamped as well: inner petals squeezed over the receptacle can sit
                # closer to the axis than the stamen's own starting angle.
                tail = path[:]
                old = list(path)
                ceil.clamp_points(tail, P["stamen_radius"] + P["anther_size"] * 0.5, rho_min=rr * 0.97)
                path[:] = tail
                _space_out(path, old, 0.4 * ln / steps)
                if ceil.last_pulled and b < 0.999:
                    continue  # no room at all in a closed bud: the stamen stays out of sight
            rad = P["stamen_radius"]
            if rad > 0:
                g.tube(stamens, path, [rad] * len(path), 4)
            a = P["anther_size"] * g.lerp(0.5, 1.0, pst)
            if a > 0:
                tip_dir = g.sub(path[-1], path[-2])
                g.ellipsoid(stamens, path[-1], tip_dir, a * 0.45, a, rings=3, sides=5)
    if P["pistil_on"] and P["pistil_length"] > 0:
        ln = P["pistil_length"] * g.lerp(0.5, 1.0, pst)
        path = [(0.0, rr * 0.9 + ln * j / 4.0, 0.0) for j in range(5)]
        if avoid:
            tail = path[1:]
            old = list(path)
            ceil.clamp_points(tail, p_rad + p_stig * 0.6, rho_min=rr * 0.9)
            path[1:] = tail
            _space_out(path, old, 0.4 * ln / 4.0)
        rad = p_rad
        g.tube(stamens, path, [rad * (1.0 - 0.3 * j / 4.0) for j in range(5)], 6)
        if p_stig > 0:
            g.ellipsoid(stamens, path[-1], g.sub(path[-1], path[-2]), p_stig * 0.6,
                        p_stig, rings=4, sides=6)

    # Disc florets on the receptacle dome (daisies, sunflowers).
    if P["disc_on"] and P["disc_count"] > 0 and P["floret_size"] > 0:
        n = int(P["disc_count"])
        tmax = R(max(P["petal_attach_outer"] - 5.0, 10.0))
        flat = g.lerp(0.35, 1.0, P["disc_dome"])
        fs = P["floret_size"]
        for k in range(n):
            fr = math.sqrt((k + 0.5) / n)
            th = tmax * fr
            phi = k * GOLDEN
            d = sph_dir(th, phi)
            c = (d[0] * rr, d[1] * rr * flat, d[2] * rr)
            sz = fs * g.lerp(0.6, 1.0, fr) * g.lerp(0.6, 1.0, pst)
            g.ellipsoid(disc, g.add(c, g.mul(d, sz * 0.3)), d, sz * 0.5, sz, rings=3, sides=5)
        # Flatten the receptacle top to match the disc.
        calyx.points = [(x, y * flat if y > 0 else y, z) for (x, y, z) in calyx.points]

    return calyx, petals, stamens, disc


# ---- assembly ------------------------------------------------------------------------------

def build(P, bloom=None):
    """Build all parts. P: full param dict (see params.defaults()). Returns (parts, stats)."""
    b = P["bloom"] if bloom is None else bloom
    b = g.clamp01(b)
    gs, ge = P["grow_start"], P["grow_end"]
    lin_ext = (b - gs) / (ge - gs) if ge > gs else (1.0 if b >= gs else 0.0)
    lin = g.clamp01(lin_ext)
    stats = {"moved": 0}
    stem = Stem(P, lin)
    parts = {name: g.Mesh() for name in PARTS}
    parts["Stem"] = stem.mesh(max(3, int(P["stem_sides"])))
    parts["Leaves"] = build_leaves(P, stem, lin_ext)
    parts["Thorns"] = build_thorns(P, stem)

    calyx, petals, stamens, disc = build_head(P, b, stats)
    # Head frame on the stem tip; head scale grows with the bud.
    if stem.L > 0:
        tip, T, N = stem.sample(stem.l)
    else:
        tip, T, N = (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (1.0, 0.0, 0.0)
    Bz = g.norm(g.cross(N, T))
    rr = P["receptacle_radius"]
    hs = g.lerp(P["bud_size"], 1.0, g.smooth(g.window(b, P["bud_start"], P["bud_end"])))
    origin = g.add(tip, g.mul(T, 1.5 * rr * hs))

    def head_to_world(p):
        return g.frame_apply(origin, N, T, Bz, (p[0] * hs, p[1] * hs, p[2] * hs))

    for name, mesh in (("Calyx", calyx), ("Petals", petals), ("Stamens", stamens), ("Disc", disc)):
        mesh.transform(head_to_world)
        parts[name] = mesh

    sc = P["scale"]
    if sc != 1.0:
        for mesh in parts.values():
            mesh.points = [(x * sc, y * sc, z * sc) for (x, y, z) in mesh.points]
    return parts, stats
