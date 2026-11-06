"""Cinema 4D side of the Flower object: Attribute Manager, presets, materials and mesh output.

The .pyp only registers the plugin and forwards to the functions here, so this module (and
the flowergen core) can be reloaded in a running Cinema 4D with dev_reload().
"""

import math
import random

import c4d

import flowergen
from flowergen import flower, params, presets

PART_MATERIAL = {
    "Stem": "mat_stem", "Calyx": "mat_stem", "Leaves": "mat_leaf", "Thorns": "mat_thorn",
    "Petals": "mat_petal", "Stamens": "mat_center", "Disc": "mat_center",
}
DEFAULT_COLORS = {
    "mat_petal": ("Flower Petal", c4d.Vector(0.85, 0.22, 0.32)),
    "mat_leaf": ("Flower Leaf", c4d.Vector(0.18, 0.42, 0.12)),
    "mat_stem": ("Flower Stem", c4d.Vector(0.24, 0.45, 0.16)),
    "mat_center": ("Flower Center", c4d.Vector(0.95, 0.75, 0.15)),
    "mat_thorn": ("Flower Thorn", c4d.Vector(0.45, 0.3, 0.15)),
}
# Groups whose edits turn the preset menu back to "Custom".
SHAPE_GROUPS = tuple(g + params.ID_OFFSET for g in (300, 400, 500, 600, 700, 800))
TAB_PARENT = None  # set by dev tests if tabs need another parent; None = root


def dev_reload():
    """Reload the core and this module in a running Cinema 4D (call from exec_python)."""
    import importlib
    import sys
    for name in ("flowergen.geom", "flowergen.layering", "flowergen.params", "flowergen.presets",
                 "flowergen.flower", "flowergen"):
        if name in sys.modules:
            importlib.reload(sys.modules[name])
    importlib.reload(sys.modules[__name__])
    return flowergen.VERSION


# ---- values --------------------------------------------------------------------------------

def _to_c4d(p, v):
    if p["unit"] == "deg":
        return math.radians(v)
    return v


def write_values(node, values):
    bc = node.GetDataInstance()
    for key, v in values.items():
        p = params.BY_KEY.get(key)
        if p is None or p["type"] not in params.VALUE_TYPES:
            continue
        if p["type"] == "float":
            bc.SetFloat(p["id"], float(_to_c4d(p, v)))
        elif p["type"] == "bool":
            bc.SetBool(p["id"], bool(v))
        else:
            bc.SetInt32(p["id"], int(v))


def read_values(node):
    bc = node.GetDataInstance()
    out = {}
    for p in params.SPEC:
        t = p["type"]
        if t not in params.VALUE_TYPES:
            continue
        if t == "float":
            v = bc.GetFloat(p["id"], _to_c4d(p, p["default"]))
            out[p["key"]] = math.degrees(v) if p["unit"] == "deg" else v
        elif t == "bool":
            out[p["key"]] = bc.GetBool(p["id"], p["default"])
        else:
            out[p["key"]] = bc.GetInt32(p["id"], p["default"])
    return out


def init(node):
    write_values(node, params.defaults())
    vals = presets.preset_values(params.BY_KEY["preset"]["default"])
    if vals:
        apply_preset(node, vals)
    return True


# Values a preset never overwrites: the animation and placement set up in the scene.
KEEP_KEYS = ("bloom", "scale", "anim_mode", "start_frame", "end_frame")


def apply_preset(node, vals):
    keep = set(KEEP_KEYS)
    write_values(node, {k: v for k, v in vals.items() if k not in keep})
    node.GetDataInstance().SetInt32(params.BY_KEY["preset"]["id"], vals["preset"])


# ---- Attribute Manager ---------------------------------------------------------------------

_DTYPES = {
    "float": c4d.DTYPE_REAL, "int": c4d.DTYPE_LONG, "bool": c4d.DTYPE_BOOL, "cycle": c4d.DTYPE_LONG,
    "button": c4d.DTYPE_BUTTON, "link": c4d.DTYPE_BASELISTLINK,
}
_UNITS = {"cm": c4d.DESC_UNIT_METER, "deg": c4d.DESC_UNIT_DEGREE, "pct": c4d.DESC_UNIT_PERCENT}


def _param_bc(p):
    bc = c4d.GetCustomDataTypeDefault(_DTYPES[p["type"]])
    bc[c4d.DESC_NAME] = p["label"]
    bc[c4d.DESC_SHORT_NAME] = p["label"]
    t = p["type"]
    ex = p["extra"]
    if t in ("float", "int"):
        bc[c4d.DESC_ANIMATE] = c4d.DESC_ANIMATE_ON
        lo, hi = _to_c4d(p, p["min"]), _to_c4d(p, p["max"])
        if t == "float":
            bc.SetFloat(c4d.DESC_MIN, lo)
            bc.SetFloat(c4d.DESC_MAX, hi)
            bc.SetFloat(c4d.DESC_STEP, math.radians(1.0) if p["unit"] == "deg" else (0.01 if p["unit"] == "pct" else 0.1))
            if p["unit"] in _UNITS:
                bc.SetInt32(c4d.DESC_UNIT, _UNITS[p["unit"]])
            if ex.get("slider"):
                bc.SetInt32(c4d.DESC_CUSTOMGUI, c4d.CUSTOMGUI_REALSLIDER)
                bc.SetFloat(c4d.DESC_MINSLIDER, lo)
                bc.SetFloat(c4d.DESC_MAXSLIDER, hi)
            elif "smin" in ex:
                bc.SetInt32(c4d.DESC_CUSTOMGUI, c4d.CUSTOMGUI_REALSLIDER)
                bc.SetFloat(c4d.DESC_MINSLIDER, ex["smin"])
                bc.SetFloat(c4d.DESC_MAXSLIDER, ex["smax"])
        else:
            bc.SetInt32(c4d.DESC_MIN, int(lo))
            bc.SetInt32(c4d.DESC_MAX, int(hi))
            bc.SetInt32(c4d.DESC_STEP, 1)
    elif t == "bool":
        bc[c4d.DESC_ANIMATE] = c4d.DESC_ANIMATE_ON
    elif t == "cycle":
        bc.SetInt32(c4d.DESC_CUSTOMGUI, c4d.CUSTOMGUI_CYCLE)
        cyc = c4d.BaseContainer()
        for i, name in enumerate(ex["options"]):
            cyc.SetString(i, name)
        bc.SetContainer(c4d.DESC_CYCLE, cyc)
        bc[c4d.DESC_ANIMATE] = c4d.DESC_ANIMATE_OFF if p["key"] == "preset" else c4d.DESC_ANIMATE_ON
    elif t == "button":
        bc.SetInt32(c4d.DESC_CUSTOMGUI, c4d.CUSTOMGUI_BUTTON)
    elif t == "link":
        acc = c4d.BaseContainer()
        acc.SetInt32(c4d.Mbase, 0)
        bc.SetContainer(c4d.DESC_ACCEPT, acc)
        bc[c4d.DESC_ANIMATE] = c4d.DESC_ANIMATE_OFF
    return bc


def get_ddescription(node, description, flags):
    if not description.LoadDescription(node.GetType()):
        return False
    single = description.GetSingleDescID()
    root = TAB_PARENT if TAB_PARENT is not None else c4d.DescID()
    # Obase's "Object" tab stays empty here, so hide it.
    obj_tab = description.GetParameterI(c4d.DescID(c4d.ID_OBJECTPROPERTIES), None)
    if obj_tab is not None:
        obj_tab[c4d.DESC_HIDE] = True

    def add(did, bc, parent):
        if single is None or did.IsPartOf(single)[0]:
            description.SetParameter(did, bc, parent)

    gids = {}
    for gid, label in params.GROUPS:
        bc = c4d.GetCustomDataTypeDefault(c4d.DTYPE_GROUP)
        bc[c4d.DESC_NAME] = label
        bc[c4d.DESC_SHORT_NAME] = label
        bc.SetInt32(c4d.DESC_COLUMNS, 1)
        bc.SetBool(c4d.DESC_DEFAULT, True)
        did = c4d.DescID(c4d.DescLevel(gid, c4d.DTYPE_GROUP, 0))
        gids[gid] = did
        add(did, bc, root)
    for p in params.SPEC:
        did = c4d.DescID(c4d.DescLevel(p["id"], _DTYPES[p["type"]], 0))
        add(did, _param_bc(p), gids[p["group"]])
    return (True, flags | c4d.DESCFLAGS_DESC_LOADED)


def get_denabling(node, did, flags):
    vals = read_values(node)
    i = did[0].id
    p = params.BY_ID.get(i)
    if p is None:
        return True
    k = p["key"]
    toggles = {300: "stem_on", 400: "leaf_on", 500: "thorn_on"}
    gate = toggles.get(p["group"] - params.ID_OFFSET)
    if gate and k != gate and not vals[gate]:
        return False
    if k in ("start_frame", "end_frame"):
        return vals["anim_mode"] == 1
    if k == "bloom":
        return vals["anim_mode"] == 0
    spiral = vals["petal_arrangement"] == 0
    if k in ("petal_count", "petal_divergence"):
        return spiral
    if k in ("petal_whorls", "petal_per_whorl"):
        return not spiral
    if k == "leaf_whorl":
        return vals["leaf_arrangement"] == 3
    if k.startswith("sepal_") and k != "sepal_on":
        return vals["sepal_on"]
    if k.startswith("stamen_") and k != "stamen_on" or k == "anther_size":
        return vals["stamen_on"]
    if k in ("pistil_length", "pistil_radius", "stigma_size"):
        return vals["pistil_on"]
    if k in ("disc_count", "disc_dome", "floret_size"):
        return vals["disc_on"]
    return True


# ---- messages: presets, buttons ------------------------------------------------------------

def message(node, mtype, data):
    if mtype == c4d.MSG_DESCRIPTION_POSTSETPARAMETER and data:
        try:
            pid = data["descid"][0].id
        except (KeyError, TypeError, IndexError):
            return True
        if pid == params.BY_KEY["preset"]["id"]:
            idx = node.GetDataInstance().GetInt32(pid)
            vals = presets.preset_values(idx)
            if vals:
                apply_preset(node, vals)
        else:
            p = params.BY_ID.get(pid)
            if p and p["group"] in SHAPE_GROUPS:
                node.GetDataInstance().SetInt32(params.BY_KEY["preset"]["id"], 0)
    elif mtype == c4d.MSG_DESCRIPTION_COMMAND and data:
        pid = data["id"][0].id
        if pid == params.BY_KEY["randomize"]["id"]:
            node.GetDataInstance().SetInt32(params.BY_KEY["seed"]["id"], random.randint(1, 99999))
            node.SetDirty(c4d.DIRTYFLAGS_DATA)
        elif pid == params.BY_KEY["make_materials"]["id"]:
            make_materials(node)
    return True


def make_materials(node):
    doc = node.GetDocument()
    if doc is None:
        return
    bc = node.GetDataInstance()
    doc.StartUndo()
    doc.AddUndo(c4d.UNDOTYPE_CHANGE_SMALL, node)
    for key, (name, color) in DEFAULT_COLORS.items():
        pid = params.BY_KEY[key]["id"]
        if bc.GetLink(pid, doc) is not None:
            continue
        mat = c4d.BaseMaterial(c4d.Mmaterial)
        mat.SetName(name)
        mat[c4d.MATERIAL_COLOR_COLOR] = color
        if key in ("mat_petal", "mat_leaf"):
            mat[c4d.MATERIAL_USE_LUMINANCE] = False
        doc.InsertMaterial(mat)
        doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, mat)
        bc.SetLink(pid, mat)
    doc.EndUndo()
    node.SetDirty(c4d.DIRTYFLAGS_DATA)
    c4d.EventAdd()


# ---- mesh output ---------------------------------------------------------------------------

def mesh_to_object(mesh, name, smooth=True, flip=False):
    npts = len(mesh.points)
    npol = len(mesh.polys)
    obj = c4d.PolygonObject(npts, npol)
    obj.SetName(name)
    V = c4d.Vector
    obj.SetAllPoints([V(x, y, z) for (x, y, z) in mesh.points])
    CP = c4d.CPolygon
    uvw = c4d.UVWTag(npol)
    for i, (a, b, c, d) in enumerate(mesh.polys):
        uv = mesh.uvs[i]
        if flip:
            a, b, c, d = (a, d, c, b) if c != d else (a, c, b, b)
            uv = (uv[0], uv[3], uv[2], uv[1]) if c != d else (uv[0], uv[2], uv[1], uv[1])
        obj.SetPolygon(i, CP(a, b, c, d))
        uvw.SetSlow(i, V(uv[0][0], uv[0][1], 0), V(uv[1][0], uv[1][1], 0),
                    V(uv[2][0], uv[2][1], 0), V(uv[3][0], uv[3][1], 0))
    obj.InsertTag(uvw)
    vmap = c4d.VariableTag(c4d.Tvertexmap, npts)
    vmap.SetAllHighlevelData([min(max(w, 0.0), 1.0) for w in mesh.weights])
    vmap.SetName("Base to Tip")
    obj.InsertTag(vmap)
    sel = c4d.SelectionTag(c4d.Tpolygonselection)
    sel.SetName(name)
    sel.GetBaseSelect().SelectAll(npol - 1)
    obj.InsertTag(sel)
    if smooth:
        ph = c4d.BaseTag(c4d.Tphong)
        ph[c4d.PHONGTAG_PHONG_ANGLELIMIT] = True
        ph[c4d.PHONGTAG_PHONG_ANGLE] = math.radians(70.0)
        obj.InsertTag(ph)
    obj.Message(c4d.MSG_UPDATE)
    return obj


def build_objects(vals, bloom, links=None):
    """Null with one polygon object per non-empty part. links: {param key: material}."""
    parts, stats = flower.build(vals, bloom)
    root = c4d.BaseObject(c4d.Onull)
    root.SetName("Flower")
    for name in flower.PARTS:
        mesh = parts[name]
        if not mesh.polys:
            continue
        obj = mesh_to_object(mesh, name, vals.get("smooth", True), flip=True)
        mat = (links or {}).get(PART_MATERIAL[name])
        if mat is None and name == "Thorns":
            mat = (links or {}).get("mat_stem")
        if mat is not None:
            tt = c4d.TextureTag()
            tt.SetMaterial(mat)
            tt[c4d.TEXTURETAG_PROJECTION] = c4d.TEXTURETAG_PROJECTION_UVW
            obj.InsertTag(tt)
        obj.InsertUnderLast(root)
    return root, stats


def current_bloom(op, vals):
    if vals["anim_mode"] == 1:
        doc = op.GetDocument()
        if doc is None:
            return vals["bloom"]
        frame = doc.GetTime().GetFrame(doc.GetFps())
        s, e = vals["start_frame"], vals["end_frame"]
        if e <= s:
            return 1.0 if frame >= s else 0.0
        return min(max((frame - s) / float(e - s), 0.0), 1.0)
    return vals["bloom"]


def get_virtual_objects(state, op, hh):
    vals = read_values(op)
    bloom = current_bloom(op, vals)
    dirty = op.CheckCache(hh) or op.IsDirty(c4d.DIRTYFLAGS_DATA) or state.get("bloom") != bloom
    if not dirty:
        return op.GetCache(hh)
    state["bloom"] = bloom
    doc = op.GetDocument()
    bc = op.GetDataInstance()
    links = {}
    for key in DEFAULT_COLORS:
        mat = bc.GetLink(params.BY_KEY[key]["id"], doc) if doc else None
        if mat is not None:
            links[key] = mat
    root, _stats = build_objects(vals, bloom, links)
    return root
