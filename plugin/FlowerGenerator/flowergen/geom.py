"""Small geometry toolkit: vectors as 3-tuples, a polygon mesh, blades and tubes.

Pure Python (Cinema 4D ships no numpy). Y is up, as in Cinema 4D.
"""

import math

TAU = 2.0 * math.pi


# ---- vectors -------------------------------------------------------------------------------

def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def length(a):
    return math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])


def norm(a):
    n = length(a)
    if n < 1e-12:
        return (0.0, 1.0, 0.0)
    return (a[0] / n, a[1] / n, a[2] / n)


def rotate(v, k, ang):
    """Rotate v around unit axis k by ang radians (Rodrigues)."""
    c = math.cos(ang)
    s = math.sin(ang)
    kv = cross(k, v)
    kd = dot(k, v) * (1.0 - c)
    return (v[0] * c + kv[0] * s + k[0] * kd,
            v[1] * c + kv[1] * s + k[1] * kd,
            v[2] * c + kv[2] * s + k[2] * kd)


def frame_apply(origin, x, y, z, p):
    """Point p given in the frame (x, y, z axes at origin)."""
    return (origin[0] + x[0] * p[0] + y[0] * p[1] + z[0] * p[2],
            origin[1] + x[1] * p[0] + y[1] * p[1] + z[1] * p[2],
            origin[2] + x[2] * p[0] + y[2] * p[1] + z[2] * p[2])


def lerp(a, b, t):
    return a + (b - a) * t


def clamp01(t):
    return 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)


def smooth(t):
    t = clamp01(t)
    return t * t * (3.0 - 2.0 * t)


def smoothstep(e0, e1, x):
    if e1 == e0:
        return 0.0 if x < e0 else 1.0
    return smooth((x - e0) / (e1 - e0))


def window(b, start, end):
    """Linear 0..1 progress of b through [start, end]."""
    if end <= start:
        return 1.0 if b >= start else 0.0
    return clamp01((b - start) / (end - start))


def perp(v):
    """Any unit vector perpendicular to unit v."""
    a = (1.0, 0.0, 0.0) if abs(v[0]) < 0.9 else (0.0, 0.0, 1.0)
    return norm(cross(v, a))


# ---- mesh ----------------------------------------------------------------------------------

class Mesh:
    """Quads (d == c for triangles), per-polygon UVs and a per-point 0..1 weight."""

    def __init__(self):
        self.points = []
        self.polys = []
        self.uvs = []
        self.weights = []
        self.groups = []  # per polygon: which petal, leaf or part it belongs to (-1 = none)

    def add_points(self, pts, weights=None):
        base = len(self.points)
        self.points.extend(pts)
        if weights is None:
            self.weights.extend([0.0] * len(pts))
        else:
            self.weights.extend(weights)
        return base

    def add_grid(self, grid, weights=None, close_v=False, uv_rect=(0.0, 0.0, 1.0, 1.0), group=-1):
        """grid[i][j]: i runs along the length (u), j across (v). Returns first point index."""
        nu = len(grid)
        nv = len(grid[0])
        flat = [p for row in grid for p in row]
        w = None if weights is None else [x for row in weights for x in row]
        base = self.add_points(flat, w)
        u0, v0, u1, v1 = uv_rect
        cols = nv if close_v else nv - 1
        for i in range(nu - 1):
            for j in range(cols):
                j2 = (j + 1) % nv
                a = base + i * nv + j
                b = base + (i + 1) * nv + j
                c = base + (i + 1) * nv + j2
                d = base + i * nv + j2
                self.polys.append((a, b, c, d))
                self.groups.append(group)
                su0 = lerp(u0, u1, j / cols)
                su1 = lerp(u0, u1, (j + 1) / cols)
                sv0 = lerp(v0, v1, i / (nu - 1))
                sv1 = lerp(v0, v1, (i + 1) / (nu - 1))
                self.uvs.append(((su0, sv0), (su0, sv1), (su1, sv1), (su1, sv0)))
        return base

    def add_fan(self, ring_start, count, center, weight=0.0, flip=False):
        """Close a ring of `count` points with triangles to a new center point."""
        ci = self.add_points([center], [weight])
        for j in range(count):
            a = ring_start + j
            b = ring_start + (j + 1) % count
            if flip:
                a, b = b, a
            self.polys.append((a, b, ci, ci))
            self.groups.append(-1)
            self.uvs.append(((0.0, 0.0), (1.0, 0.0), (0.5, 1.0), (0.5, 1.0)))

    def extend(self, other):
        base = len(self.points)
        self.points.extend(other.points)
        self.weights.extend(other.weights)
        for (a, b, c, d) in other.polys:
            self.polys.append((a + base, b + base, c + base, d + base))
        self.uvs.extend(other.uvs)
        self.groups.extend(other.groups)

    def transform(self, fn):
        self.points = [fn(p) for p in self.points]


# ---- blades: petals, sepals and leaves -----------------------------------------------------

def blade_halfwidth(u, width_pos, base, tip):
    """Outline half-width (0..1) along the length u in 0..1."""
    wp = min(max(width_pos, 0.05), 0.95)
    k = math.log(0.5) / math.log(wp)
    t = u ** k if u > 0.0 else 0.0
    s = math.sin(math.pi * t)
    if t <= 0.5:
        return base + (1.0 - base) * (s ** 0.8)
    e = lerp(0.3, 1.6, tip)
    return max(s, 0.0) ** e


def build_blade(shape, res_u, res_v):
    """Return (grid, weights) of a blade in its local frame.

    Local frame: base at the origin, length along +Y, width along +X, and +Z is the inner
    (adaxial) face. Positive curl bends the blade toward +Z.
    shape keys: length, width, width_pos, base, tip, notch, fringe, fringe_depth, serration,
    serration_depth, cup, fold, curl, tip_curl, twist, ruffle, ruffle_freq, phase.
    Angles are in radians.
    """
    L = shape["length"]
    W = shape["width"]
    serr = shape.get("serration", 0)
    if serr:
        res_u = max(res_u, serr * 4 + 2)
    fringe = shape.get("fringe", 0)
    if fringe:
        res_v = max(res_v, fringe * 4 + 1)
    if res_v % 2 == 0:
        res_v += 1  # keep a center column for the midrib

    cup = shape.get("cup", 0.0)
    fold = shape.get("fold", 0.0)
    curl = shape.get("curl", 0.0)
    tip_curl = shape.get("tip_curl", 0.0)
    twist = shape.get("twist", 0.0)
    ruffle = shape.get("ruffle", 0.0) * W
    rfreq = shape.get("ruffle_freq", 3.0)
    rphase = shape.get("phase", 0.0)
    notch = shape.get("notch", 0.0)
    fdepth = shape.get("fringe_depth", 0.0)
    sdepth = shape.get("serration_depth", 0.0)

    # Centerline: bend angle beta(u) integrated over the length (64 steps, interpolated).
    steps = 64
    cy = [0.0]
    cz = [0.0]
    betas = [0.0]
    y = z = 0.0
    for n in range(1, steps + 1):
        um = (n - 0.5) / steps
        beta = curl * um ** 1.3 + tip_curl * (max(0.0, (um - 0.55) / 0.45) ** 2)
        y += math.cos(beta) * L / steps
        z += math.sin(beta) * L / steps
        cy.append(y)
        cz.append(z)
        betas.append(curl * (n / steps) ** 1.3 + tip_curl * (max(0.0, (n / steps - 0.55) / 0.45) ** 2))

    def center(s):
        f = clamp01(s) * steps
        i = min(int(f), steps - 1)
        t = f - i
        return (lerp(cy[i], cy[i + 1], t), lerp(cz[i], cz[i + 1], t), lerp(betas[i], betas[i + 1], t))

    kappa = cup / W if (W > 1e-9 and abs(cup) > 1e-6) else 0.0
    cf = math.cos(fold)
    sf = math.sin(fold)

    grid = []
    weights = []
    for i in range(res_u):
        u = i / (res_u - 1)
        hw = blade_halfwidth(u, shape.get("width_pos", 0.5), shape.get("base", 0.2), shape.get("tip", 0.5))
        if serr and 0.05 < u < 0.97:
            saw = (u * serr) % 1.0
            hw *= 1.0 - sdepth * saw
        row = []
        wrow = []
        for j in range(res_v):
            v = -1.0 + 2.0 * j / (res_v - 1)
            av = abs(v)
            s = u
            if notch > 0.0:
                s *= 1.0 - notch * 0.3 * (1.0 - av) ** 2 * smoothstep(0.5, 1.0, u)
            if fringe:
                tooth = 0.5 - 0.5 * math.cos(math.pi * fringe * (v + 1.0))
                s *= 1.0 - fdepth * 0.3 * tooth * smoothstep(0.6, 1.0, u)
            x = hw * 0.5 * W * v
            # Across-width cup (an arc) and midrib fold (a V); edges rise toward +Z.
            if kappa:
                a = kappa * x
                xz = (math.sin(a) / kappa, (1.0 - math.cos(a)) / kappa)
            else:
                xz = (x, 0.0)
            px = xz[0] * cf
            pz = xz[1] + abs(xz[0]) * sf
            if ruffle:
                # Flutes fanning out from the base, so the waves run around the rim.
                lx = x / L if L > 1e-9 else 0.0
                rad = math.sqrt(s * s + lx * lx)
                ang = math.atan2(lx, s if s > 1e-6 else 1e-6)
                pz += ruffle * 0.5 * smoothstep(0.2, 1.0, rad) * math.sin(2.0 * rfreq * ang + rphase)
            if twist:
                ta = twist * s
                c = math.cos(ta)
                sn = math.sin(ta)
                px, pz = px * c - pz * sn, px * sn + pz * c
            ccy, ccz, beta = center(s)
            # Normal of the bent centerline in the YZ plane.
            ny = -math.sin(beta)
            nz = math.cos(beta)
            row.append((px, ccy + pz * ny, ccz + pz * nz))
            wrow.append(s)
        grid.append(row)
        weights.append(wrow)
    return grid, weights


# ---- tubes ---------------------------------------------------------------------------------

def tube(mesh, path, radii, sides, normal0=None, cap_start=False, cap_end=False, weights=None):
    """Sweep a circle along path (list of points) with per-point radii. Parallel-transport frames."""
    n = len(path)
    if n < 2:
        return
    tangents = []
    for i in range(n):
        a = path[max(i - 1, 0)]
        b = path[min(i + 1, n - 1)]
        tangents.append(norm(sub(b, a)))
    nrm = normal0 if normal0 is not None else perp(tangents[0])
    grid = []
    for i in range(n):
        t = tangents[i]
        if i > 0:
            # Transport the normal: remove its tangent component.
            nrm = norm(sub(nrm, mul(t, dot(nrm, t))))
        b = cross(t, nrm)
        r = radii[i]
        row = []
        for j in range(sides):
            a = TAU * j / sides
            ca = math.cos(a) * r
            sa = math.sin(a) * r
            p = path[i]
            row.append((p[0] + nrm[0] * ca + b[0] * sa, p[1] + nrm[1] * ca + b[1] * sa, p[2] + nrm[2] * ca + b[2] * sa))
        grid.append(row)
    w = None
    if weights is not None:
        w = [[weights[i]] * sides for i in range(n)]
    base = mesh.add_grid(grid, w, close_v=True)
    if cap_start:
        mesh.add_fan(base, sides, path[0], 0.0 if weights is None else weights[0], flip=True)
    if cap_end:
        mesh.add_fan(base + (n - 1) * sides, sides, path[-1], 1.0 if weights is None else weights[-1])


def ellipsoid(mesh, center, axis, radius, length, rings=4, sides=6):
    """Small closed ellipsoid along axis (for anthers, stigmas and florets)."""
    axis = norm(axis)
    nrm = perp(axis)
    bi = cross(axis, nrm)
    grid = []
    for i in range(rings + 1):
        a = math.pi * i / rings
        h = -math.cos(a) * length * 0.5
        r = math.sin(a) * radius
        row = []
        for j in range(sides):
            b = TAU * j / sides
            ca = math.cos(b) * r
            sa = math.sin(b) * r
            row.append((center[0] + axis[0] * h + nrm[0] * ca + bi[0] * sa,
                        center[1] + axis[1] * h + nrm[1] * ca + bi[1] * sa,
                        center[2] + axis[2] * h + nrm[2] * ca + bi[2] * sa))
        grid.append(row)
    mesh.add_grid(grid, close_v=True)
