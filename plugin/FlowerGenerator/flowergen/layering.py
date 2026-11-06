"""Petal layering: keeps every inner part inside the parts outside it, so nothing intersects.

All parts of the head are processed from the outside in (sepals, outer petals, inner petals,
stamens). Points are seen in spherical coordinates around the head center: rho (distance),
theta (angle from the head axis; 0 = pointing straight up, 90 deg = flat, more = reflexed)
and phi (azimuth). A "ceiling" grid over (phi, rho) stores the smallest theta of everything
placed so far. Each new part is clamped below the ceiling minus a clearance, then added to it.

A part that still has m overlapping layers inside it also gets a floor of m clearances above
the axis, so a tight bud keeps room for its inner petals instead of crushing them onto the axis.

Clamping moves points only along their meridian (theta), so rho and phi, and with them the
part's length and spread, are kept. The result is the same on every frame, with no simulation.
"""

import math

from .geom import TAU


def to_sph(p):
    x, y, z = p
    rho = math.sqrt(x * x + y * y + z * z)
    if rho < 1e-12:
        return 0.0, 0.0, 0.0
    c = y / rho
    c = 1.0 if c > 1.0 else (-1.0 if c < -1.0 else c)
    return rho, math.acos(c), math.atan2(z, x) % TAU


def from_sph(rho, theta, phi):
    st = math.sin(theta)
    return (rho * st * math.cos(phi), rho * math.cos(theta), rho * st * math.sin(phi))


def phi_span(grid, phi0, rows=(0.3, 0.85)):
    """Azimuth interval (lo, hi) of a grid relative to phi0, from its middle rows."""
    nu = len(grid)
    lo = hi = 0.0
    for i in range(int(rows[0] * (nu - 1)), int(rows[1] * (nu - 1)) + 1):
        for p in grid[i]:
            if p[0] * p[0] + p[2] * p[2] < 1e-10:
                continue
            d = (math.atan2(p[2], p[0]) - phi0 + math.pi) % TAU - math.pi
            if d < lo:
                lo = d
            if d > hi:
                hi = d
    return phi0 + lo, phi0 + hi


def spans_overlap(a, b):
    """Do two azimuth intervals (unwrapped, each shorter than a full turn) overlap?"""
    if a[1] - a[0] >= TAU or b[1] - b[0] >= TAU:
        return True
    shift = ((b[0] - a[0] + math.pi) % TAU) - math.pi - (b[0] - a[0])
    b0, b1 = b[0] + shift, b[1] + shift
    for off in (-TAU, 0.0, TAU):
        if b0 + off <= a[1] and a[0] <= b1 + off:
            return True
    return False


def _xz(c):
    s = math.sin(c[1]) * c[0]
    return s * math.cos(c[2]), s * math.sin(c[2])


def _seg_dist2(a, b):
    """Squared distance from the origin to segment a-b in the plane."""
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    l2 = dx * dx + dy * dy
    t = 0.0 if l2 < 1e-18 else max(0.0, min(1.0, -(a[0] * dx + a[1] * dy) / l2))
    x = a[0] + t * dx
    y = a[1] + t * dy
    return x * x + y * y


def _chord_factor(c0, c1, c2, c3):
    """How much closer to the axis a straight quad (triangles c0 c1 c3 and c0 c3 c2) gets than
    its nearest corner, as a ratio in [0, 1]. A quad that spans a wide azimuth cuts a chord
    across the axis, so a corner-only ceiling would let an inner part poke through it."""
    p = (_xz(c0), _xz(c1), _xz(c3), _xz(c2))
    dv = min(x * x + y * y for (x, y) in p)
    if dv < 1e-14:
        return 1.0
    # Winding number of the origin around the quad (inside -> chord reaches the axis).
    wn = 0
    for k in range(4):
        a = p[k]
        b = p[(k + 1) % 4]
        if (a[1] <= 0.0) != (b[1] <= 0.0):
            xc = a[0] + (0.0 - a[1]) / (b[1] - a[1]) * (b[0] - a[0])
            if xc > 0.0:
                wn += 1 if b[1] > a[1] else -1
    if wn:
        return 0.02
    dm = min(_seg_dist2(p[k], p[(k + 1) % 4]) for k in range(4))
    dm = min(dm, _seg_dist2(p[0], p[2]))
    f = math.sqrt(dm / dv)
    return 0.02 if f < 0.02 else (1.0 if f > 1.0 else f)


class Ceiling:
    def __init__(self, rho_max, clearance, gap_cap=math.radians(3.0), theta_cap=math.radians(165.0),
                 nphi=240, nrho=64):
        self.nphi = nphi
        self.nrho = nrho
        self.rho_max = max(rho_max, 1e-6)
        self.clearance = clearance
        self.grid = [theta_cap] * (nphi * nrho)
        self.dphi = TAU / nphi
        self.drho = self.rho_max / nrho
        self.gap_cap = gap_cap

    def gap(self, rho):
        g = self.clearance / rho if rho > 1e-6 else self.gap_cap
        return g if g < self.gap_cap else self.gap_cap

    def ceiling(self, rho, phi):
        """Bilinear lookup; add_grid dilates by one cell so this stays conservative."""
        fr = rho / self.drho - 0.5
        fp = phi / self.dphi - 0.5
        r0 = int(math.floor(fr))
        p0 = int(math.floor(fp))
        tr = fr - r0
        tp = fp - p0
        nr = self.nrho
        npf = self.nphi
        r0c = 0 if r0 < 0 else (nr - 1 if r0 >= nr else r0)
        r1c = 0 if r0 + 1 < 0 else (nr - 1 if r0 + 1 >= nr else r0 + 1)
        p0c = p0 % npf
        p1c = (p0 + 1) % npf
        g = self.grid
        a = g[r0c * npf + p0c]
        b = g[r0c * npf + p1c]
        c = g[r1c * npf + p0c]
        d = g[r1c * npf + p1c]
        return (a * (1 - tp) + b * tp) * (1 - tr) + (c * (1 - tp) + d * tp) * tr

    def _limits(self, rho, ph, layers, core_r, core_from):
        """(lo, hi, ok) for a point: each of the `layers` inner layers takes at most its share of
        the room under the ceiling, so the floor can never exceed the ceiling. ok is False when
        the ceiling cannot even hold the stamen column plus one gap (pull inward in rho)."""
        c = self.ceiling(rho, ph)
        cf = min(core_r / rho, math.radians(25.0)) if (core_r > 0.0 and rho > core_from) else 0.0
        room = max(c - cf, 0.0)
        ge = min(self.gap(rho), room / (layers + 2))
        hi = c - ge
        lo = min(layers * ge + cf, hi - 1e-6)
        if lo < 0.0:
            lo = 0.0
        return lo, hi, (c >= cf + 0.25 * self.gap(rho) and hi > 0.0), c, ge

    def clamp_grid(self, grid, floor_layers=0, smooth_iters=3, core_r=0.0, core_from=0.0, rho_min=0.0):
        """Clamp a 2D grid of points (list of rows) in place. Returns the number of points moved."""
        nu = len(grid)
        nv = len(grid[0])
        sph = [[to_sph(p) for p in row] for row in grid]
        lo = []
        hi = []
        cs = []
        es = []
        bad = []
        core_eff = [[core_r] * nv for _ in range(nu)]
        for i in range(nu):
            lr = []
            hr = []
            cr = []
            er = []
            for j in range(nv):
                l, h, ok, c, ge = self._limits(sph[i][j][0], sph[i][j][2], floor_layers, core_eff[i][j], core_from)
                lr.append(l)
                hr.append(h)
                cr.append(c)
                er.append(ge)
                if not ok:
                    bad.append((i, j))
            lo.append(lr)
            hi.append(hr)
            cs.append(cr)
            es.append(er)
        # Rim of the layers outside: a vertex just past the rim of an outer part has no ceiling,
        # but the quads it shares with vertices under the rim would slice through the outer part.
        # Such a vertex may not rise above the ceiling of its neighbours under the rim.
        cliff = 0.35
        for i in range(nu):
            for j in range(nv):
                cij = cs[i][j]
                best = None
                for di in (-1, 0, 1):
                    ii = i + di
                    if ii < 0 or ii >= nu:
                        continue
                    for dj in (-1, 0, 1):
                        jj = j + dj
                        if jj < 0 or jj >= nv or (di == 0 and dj == 0):
                            continue
                        if cij - cs[ii][jj] > cliff:
                            v = cs[ii][jj] - es[ii][jj]
                            if best is None or v < best:
                                best = v
                if best is not None and best < hi[i][j]:
                    hi[i][j] = max(best, lo[i][j])
        # The ceiling can dip between two vertices (a corner of an outer part): the straight edge
        # between them must stay under it too, so check the middle of every edge.
        for i in range(nu):
            for j in range(nv):
                for (di, dj) in ((0, 1), (1, 0), (1, 1)):
                    i2 = i + di
                    j2 = j + dj
                    if i2 >= nu or j2 >= nv:
                        continue
                    ca = cs[i][j]
                    cb = cs[i2][j2]
                    if ca > 3.0 or cb > 3.0 or abs(ca - cb) < 0.005:
                        continue
                    ta = min(sph[i][j][1], hi[i][j])
                    tb = min(sph[i2][j2][1], hi[i2][j2])
                    if min(ca, cb) - max(ta, tb) > 0.05:
                        continue
                    dp = (sph[i2][j2][2] - sph[i][j][2] + math.pi) % TAU - math.pi
                    rm = 0.5 * (sph[i][j][0] + sph[i2][j2][0])
                    cm = self.ceiling(rm, (sph[i][j][2] + 0.5 * dp) % TAU)
                    tm = cm - 0.5 * (es[i][j] + es[i2][j2])
                    ex = 0.5 * (ta + tb) - tm
                    if ex > 0.0:
                        hi[i][j] = max(min(hi[i][j], ta - ex), lo[i][j])
                        hi[i2][j2] = max(min(hi[i2][j2], tb - ex), lo[i2][j2])
        moved = 0
        # Where the ceiling has no room at all, pull the point inward in rho to the largest rho
        # that does have room (otherwise it would collapse onto the axis).
        step = self.drho * 0.5
        caps = [None] * nu
        rho0 = min(sph[0][j][0] for j in range(nv))
        rho1 = max(sph[i][j][0] for i in range(nu) for j in range(nv))
        cap_floor = rho0 + 0.3 * (rho1 - rho0)  # near the base the old per-vertex pull applies
        for (i, j) in bad:
            rho, th, ph = sph[i][j]
            r = rho - step
            found = False
            while r > rho_min:
                if self._limits(r, ph, floor_layers, core_eff[i][j], core_from)[2]:
                    found = True
                    break
                r -= step
            if found:
                if r < cap_floor and i > 0.5 * (nu - 1):
                    # Far along the blade: stay at the previous row's distance, never fold back.
                    r = max(r, min(sph[i - 1][jj][0] for jj in range(nv)) if not caps[i - 1] else caps[i - 1])
                if r >= cap_floor and (caps[i] is None or r < caps[i]):
                    caps[i] = r
                else:
                    sph[i][j] = (r, th, ph)
                    lo[i][j], hi[i][j], _, _, _ = self._limits(r, ph, floor_layers, core_eff[i][j], core_from)
                    grid[i][j] = from_sph(r, th, ph)
                    moved += 1
        # The blade is shortened, not folded back: once a row has to stop at some distance, every
        # row after it stops there too (a tip that jumped back down would cut through its own petal).
        run = None
        for i in range(nu):
            if caps[i] is not None and (run is None or caps[i] < run):
                run = caps[i]
            if run is None:
                continue
            for j in range(nv):
                rho, th, ph = sph[i][j]
                if rho > run:
                    sph[i][j] = (run, th, ph)
                    lo[i][j], hi[i][j], _, _, _ = self._limits(run, ph, floor_layers, core_eff[i][j], core_from)
                    grid[i][j] = from_sph(run, th, ph)
                    moved += 1
        delta = []
        for i in range(nu):
            r = []
            for j in range(nv):
                th = sph[i][j][1]
                t = th
                if t < lo[i][j]:
                    t = lo[i][j]
                if t > hi[i][j]:
                    t = hi[i][j]
                if t != th:
                    moved += 1
                r.append(t - th)
            delta.append(r)
        if not moved:
            return 0
        # Spread the push over neighbours so dents stay smooth, then re-apply the hard limits.
        soft = delta
        for _ in range(smooth_iters):
            nxt = []
            for i in range(nu):
                r = []
                up = soft[i - 1] if i > 0 else None
                dn = soft[i + 1] if i < nu - 1 else None
                row = soft[i]
                for j in range(nv):
                    acc = row[j] * 2.0
                    cnt = 2.0
                    if up is not None:
                        acc += up[j]; cnt += 1.0
                    if dn is not None:
                        acc += dn[j]; cnt += 1.0
                    if j > 0:
                        acc += row[j - 1]; cnt += 1.0
                    if j < nv - 1:
                        acc += row[j + 1]; cnt += 1.0
                    r.append(acc / cnt)
                nxt.append(r)
            soft = nxt
        for i in range(nu):
            row = grid[i]
            for j in range(nv):
                rho, th, ph = sph[i][j]
                t = th + soft[i][j]
                if t < lo[i][j]:
                    t = lo[i][j]
                if t > hi[i][j]:
                    t = hi[i][j]
                if t < 0.0:
                    t = 0.0
                if t != th:
                    row[j] = from_sph(rho, t, ph)
        return moved

    def _fit(self, rho, th, ph, extra):
        """Largest theta allowed for a tube of radius `extra` around a point (rho, th, ph):
        the lowest ceiling over the tube's footprint, less the gap and the tube's own angle."""
        ang = extra / rho if rho > 1e-6 else 0.0
        if ang <= 0.0:
            return self.ceiling(rho, ph) - self.gap(rho)
        s = math.sin(th)
        if s <= 1e-9 or math.sin(ang) >= s:
            w = math.pi
            n = 12
        else:
            w = math.asin(math.sin(ang) / s)
            n = 5
        cmin = 1e9
        for rr in (rho - extra, rho, rho + extra):
            if rr < self.drho * 0.5:
                rr = self.drho * 0.5
            for q in range(n):
                p2 = ph + (-w + 2.0 * w * q / n if w < math.pi else TAU * q / n)
                if w < math.pi and q == n - 1:
                    p2 = ph + w
                c = self.ceiling(rr, p2 % TAU)
                if c < cmin:
                    cmin = c
        return cmin - self.gap(rho) - ang

    def clamp_points(self, pts, extra=0.0, rho_min=0.0):
        """Clamp a flat list of points in place (stamen centerlines and the like). A tube of
        radius `extra` around each point must fit under the ceiling; if it cannot at this rho,
        the point moves inward in rho to the largest rho where it does."""
        moved = 0
        self.last_pulled = 0
        for k, p in enumerate(pts):
            rho, th, ph = to_sph(p)
            t = th
            lim = self._fit(rho, t, ph, extra)
            for _ in range(3):
                if lim >= t:
                    break
                t = max(lim, 0.0)
                lim = self._fit(rho, t, ph, extra)
            if lim < t - 1e-9 or lim < 0.0:
                step = self.drho * 0.5
                r = rho - step
                found = False
                step = max(step, 1e-9)
                while r > max(step, rho_min):
                    if self._fit(r, 0.0, ph, extra) >= 0.0:
                        found = True
                        break
                    r -= step
                rho = r if found else max(r, step, rho_min)
                t = 0.0
                lim = self._fit(rho, t, ph, extra)
                t = min(th, max(lim, 0.0))
                pts[k] = from_sph(rho, t, ph)
                moved += 1
                self.last_pulled += 1
            elif t != th:
                pts[k] = from_sph(rho, t, ph)
                moved += 1
        return moved

    def add_grid(self, grid):
        """Write a grid's quads into the ceiling: each quad's smallest theta over its bounds,
        dilated by one cell so the bilinear lookup never sees past the real surface."""
        nu = len(grid)
        nv = len(grid[0])
        sph = [[to_sph(p) for p in row] for row in grid]
        nphi = self.nphi
        nrho = self.nrho
        g = self.grid
        drho = self.drho
        dphi = self.dphi
        for i in range(nu - 1):
            r0 = sph[i]
            r1 = sph[i + 1]
            for j in range(nv - 1):
                c0, c1, c2, c3 = r0[j], r0[j + 1], r1[j], r1[j + 1]
                tmin = min(c0[1], c1[1], c2[1], c3[1])
                rlo = int(min(c0[0], c1[0], c2[0], c3[0]) / drho) - 1
                rhi = int(max(c0[0], c1[0], c2[0], c3[0]) / drho) + 1
                if rlo < 0:
                    rlo = 0
                if rhi >= nrho:
                    rhi = nrho - 1
                p0 = c0[2]
                lo = hi = 0.0
                for c in (c1, c2, c3):
                    d = (c[2] - p0 + math.pi) % TAU - math.pi
                    if d < lo:
                        lo = d
                    if d > hi:
                        hi = d
                if hi - lo > 0.05 and tmin < 1.5:
                    # A chord across a wide azimuth span dips toward the axis.
                    tmin = math.atan(math.tan(tmin) * _chord_factor(c0, c1, c2, c3))
                plo = int(math.floor((p0 + lo) / dphi)) - 1
                phi_ = int(math.floor((p0 + hi) / dphi)) + 1
                if phi_ - plo >= nphi:
                    plo, phi_ = 0, nphi - 1
                for ri in range(rlo, rhi + 1):
                    base = ri * nphi
                    for pi in range(plo, phi_ + 1):
                        idx = base + pi % nphi
                        if tmin < g[idx]:
                            g[idx] = tmin
