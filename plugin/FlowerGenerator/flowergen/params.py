"""Parameter spec: the single source of truth for every Flower control.

Each entry has a stable numeric id (saved in scenes and animation tracks, so never renumber),
a key used by the geometry core, a type, a default and a range. The C4D layer builds its
Attribute Manager from this list; the core reads plain dicts keyed by `key`.

Units: lengths in cm, angles in degrees, fractions 0..1 (shown as percent in C4D).
"""

# Every id below is offset by ID_OFFSET in GROUPS/SPEC so none collides with Cinema 4D's own
# object parameters (Obase uses 800-1107). Raw numbers are kept short here for readability.
ID_OFFSET = 20000

# Tabs, in display order: (group id, label)
_GROUPS = [
    (100, "Flower"),
    (200, "Bloom"),
    (300, "Stem"),
    (400, "Leaves"),
    (500, "Thorns"),
    (600, "Petals"),
    (700, "Calyx"),
    (800, "Center"),
    (900, "Materials"),
    (950, "Quality"),
]

PRESET_NAMES = ["Custom", "Rose", "Tulip", "Daisy", "Lily", "Poppy", "Lotus", "Cherry Blossom", "Wild Rose"]

# (id, key, type, default, min, max, unit, group, label, extra)
# type: float, int, bool, cycle, button, link, sep
# unit: cm, deg, pct, "" (plain number)
_S = [
    # Flower
    (1001, "preset", "cycle", 1, 0, 0, "", 100, "Preset", {"options": PRESET_NAMES}),
    (1002, "seed", "int", 1, 0, 99999, "", 100, "Seed", {}),
    (1003, "randomize", "button", None, 0, 0, "", 100, "New Seed", {}),
    (1004, "bloom", "float", 1.0, 0.0, 1.0, "pct", 100, "Bloom", {"slider": True}),
    (1005, "scale", "float", 1.0, 0.01, 100.0, "pct", 100, "Scale", {"smin": 0.1, "smax": 4.0}),
    (1006, "anim_mode", "cycle", 0, 0, 0, "", 100, "Animate", {"options": ["Bloom Slider", "Frame Range"]}),
    (1007, "start_frame", "int", 0, -100000, 100000, "", 100, "Start Frame", {}),
    (1008, "end_frame", "int", 120, -100000, 100000, "", 100, "End Frame", {}),

    # Bloom timing (fractions of the 0..1 bloom)
    (2001, "grow_start", "float", 0.0, 0.0, 1.0, "pct", 200, "Stem Grow Start", {"slider": True}),
    (2002, "grow_end", "float", 0.35, 0.0, 1.0, "pct", 200, "Stem Grow End", {"slider": True}),
    (2003, "leaf_dur", "float", 0.2, 0.01, 1.0, "pct", 200, "Leaf Unfurl Time", {"slider": True}),
    (2004, "bud_start", "float", 0.2, 0.0, 1.0, "pct", 200, "Bud Swell Start", {"slider": True}),
    (2005, "bud_end", "float", 0.5, 0.0, 1.0, "pct", 200, "Bud Swell End", {"slider": True}),
    (2006, "open_start", "float", 0.45, 0.0, 1.0, "pct", 200, "Open Start", {"slider": True}),
    (2007, "open_end", "float", 1.0, 0.0, 1.0, "pct", 200, "Open End", {"slider": True}),
    (2008, "stagger", "float", 0.5, 0.0, 0.95, "pct", 200, "Petal Stagger", {"slider": True}),
    (2009, "bud_size", "float", 0.3, 0.01, 1.0, "pct", 200, "Bud Size", {"slider": True}),
    (2010, "bud_angle", "float", 8.0, 0.0, 90.0, "deg", 200, "Bud Petal Angle", {}),
    (2011, "bud_curl", "float", 35.0, -180.0, 180.0, "deg", 200, "Bud Petal Curl", {}),
    (2012, "bud_petal_size", "float", 0.7, 0.05, 1.0, "pct", 200, "Bud Petal Size", {"slider": True}),

    # Stem
    (3001, "stem_on", "bool", True, 0, 0, "", 300, "Stem", {}),
    (3002, "stem_length", "float", 40.0, 0.0, 10000.0, "cm", 300, "Length", {}),
    (3003, "stem_radius", "float", 0.35, 0.001, 100.0, "cm", 300, "Radius", {}),
    (3004, "stem_taper", "float", 0.6, 0.0, 1.0, "pct", 300, "Tip Radius", {"slider": True}),
    (3005, "stem_bend", "float", 20.0, -360.0, 360.0, "deg", 300, "Bend", {}),
    (3006, "stem_bend_dir", "float", 0.0, -360.0, 360.0, "deg", 300, "Bend Direction", {}),
    (3007, "stem_wiggle", "float", 8.0, 0.0, 180.0, "deg", 300, "Wiggle", {}),
    (3008, "stem_wiggle_freq", "float", 2.0, 0.0, 20.0, "", 300, "Wiggle Frequency", {}),
    (3009, "stem_nod", "float", 15.0, -180.0, 180.0, "deg", 300, "Head Nod", {}),
    (3010, "stem_unfurl", "float", 0.0, 0.0, 1.0, "pct", 300, "Unfurl Coil", {"slider": True}),
    (3011, "stem_sides", "int", 8, 3, 64, "", 300, "Sides", {}),
    (3012, "stem_segments", "int", 48, 2, 1000, "", 300, "Segments", {}),

    # Leaves
    (4001, "leaf_on", "bool", True, 0, 0, "", 400, "Leaves", {}),
    (4002, "leaf_count", "int", 5, 0, 500, "", 400, "Count", {}),
    (4003, "leaf_start", "float", 0.1, 0.0, 1.0, "pct", 400, "Start", {"slider": True}),
    (4004, "leaf_end", "float", 0.7, 0.0, 1.0, "pct", 400, "End", {"slider": True}),
    (4005, "leaf_arrangement", "cycle", 2, 0, 0, "", 400, "Arrangement",
     {"options": ["Alternate", "Opposite", "Spiral", "Whorled"]}),
    (4006, "leaf_whorl", "int", 3, 2, 12, "", 400, "Leaves per Whorl", {}),
    (4007, "leaf_length", "float", 8.0, 0.0, 1000.0, "cm", 400, "Length", {}),
    (4008, "leaf_width", "float", 3.0, 0.0, 1000.0, "cm", 400, "Width", {}),
    (4009, "leaf_width_pos", "float", 0.35, 0.05, 0.95, "pct", 400, "Widest Point", {"slider": True}),
    (4010, "leaf_base", "float", 0.15, 0.0, 1.0, "pct", 400, "Base Width", {"slider": True}),
    (4011, "leaf_tip", "float", 0.7, 0.0, 1.0, "pct", 400, "Tip Point", {"slider": True}),
    (4012, "leaf_serration", "int", 0, 0, 100, "", 400, "Teeth per Side", {}),
    (4013, "leaf_serration_depth", "float", 0.12, 0.0, 1.0, "pct", 400, "Teeth Depth", {"slider": True}),
    (4014, "leaf_fold", "float", 20.0, -90.0, 90.0, "deg", 400, "Midrib Fold", {}),
    (4015, "leaf_angle", "float", 50.0, 0.0, 180.0, "deg", 400, "Angle from Stem", {}),
    (4016, "leaf_droop", "float", 60.0, -360.0, 360.0, "deg", 400, "Droop", {}),
    (4017, "leaf_twist", "float", 10.0, -360.0, 360.0, "deg", 400, "Twist", {}),
    (4018, "leaf_ruffle", "float", 0.03, 0.0, 1.0, "pct", 400, "Ruffle", {"slider": True}),
    (4019, "leaf_petiole", "float", 0.8, 0.0, 100.0, "cm", 400, "Petiole Length", {}),
    (4020, "leaf_top_scale", "float", 0.6, 0.0, 2.0, "pct", 400, "Top Leaf Size", {"slider": True}),
    (4021, "leaf_random", "float", 0.2, 0.0, 1.0, "pct", 400, "Randomness", {"slider": True}),

    # Thorns
    (5001, "thorn_on", "bool", False, 0, 0, "", 500, "Thorns", {}),
    (5002, "thorn_count", "int", 14, 0, 2000, "", 500, "Count", {}),
    (5003, "thorn_start", "float", 0.05, 0.0, 1.0, "pct", 500, "Start", {"slider": True}),
    (5004, "thorn_end", "float", 0.85, 0.0, 1.0, "pct", 500, "End", {"slider": True}),
    (5005, "thorn_length", "float", 0.6, 0.0, 100.0, "cm", 500, "Length", {}),
    (5006, "thorn_width", "float", 0.3, 0.0, 100.0, "cm", 500, "Base Width", {}),
    (5007, "thorn_angle", "float", -25.0, -90.0, 90.0, "deg", 500, "Tilt", {}),
    (5008, "thorn_hook", "float", -35.0, -180.0, 180.0, "deg", 500, "Hook", {}),
    (5009, "thorn_random", "float", 0.3, 0.0, 1.0, "pct", 500, "Randomness", {"slider": True}),

    # Petals
    (6001, "petal_arrangement", "cycle", 0, 0, 0, "", 600, "Arrangement", {"options": ["Spiral", "Whorls"]}),
    (6002, "petal_count", "int", 24, 1, 1000, "", 600, "Count (Spiral)", {}),
    (6003, "petal_divergence", "float", 137.508, -360.0, 360.0, "deg", 600, "Divergence (Spiral)", {}),
    (6004, "petal_whorls", "int", 2, 1, 50, "", 600, "Whorls", {}),
    (6005, "petal_per_whorl", "int", 5, 1, 200, "", 600, "Petals per Whorl", {}),
    (6006, "petal_length", "float", 4.0, 0.0, 1000.0, "cm", 600, "Length", {}),
    (6007, "petal_width", "float", 3.6, 0.0, 1000.0, "cm", 600, "Width", {}),
    (6008, "petal_width_pos", "float", 0.6, 0.05, 0.95, "pct", 600, "Widest Point", {"slider": True}),
    (6009, "petal_base", "float", 0.25, 0.0, 1.0, "pct", 600, "Base Width", {"slider": True}),
    (6010, "petal_tip", "float", 0.15, 0.0, 1.0, "pct", 600, "Tip Point", {"slider": True}),
    (6011, "petal_notch", "float", 0.0, 0.0, 1.0, "pct", 600, "Tip Notch", {"slider": True}),
    (6012, "petal_fringe", "int", 0, 0, 100, "", 600, "Fringe Teeth", {}),
    (6013, "petal_fringe_depth", "float", 0.15, 0.0, 1.0, "pct", 600, "Fringe Depth", {"slider": True}),
    (6014, "petal_cup", "float", 70.0, -360.0, 360.0, "deg", 600, "Cup", {}),
    (6015, "petal_curl", "float", -10.0, -360.0, 360.0, "deg", 600, "Curl", {}),
    (6016, "petal_tip_curl", "float", -45.0, -360.0, 360.0, "deg", 600, "Tip Curl", {}),
    (6017, "petal_twist", "float", 0.0, -360.0, 360.0, "deg", 600, "Twist", {}),
    (6018, "petal_ruffle", "float", 0.04, 0.0, 1.0, "pct", 600, "Ruffle", {"slider": True}),
    (6019, "petal_ruffle_freq", "float", 3.0, 0.0, 50.0, "", 600, "Ruffle Waves", {}),
    (6020, "petal_open_outer", "float", 100.0, 0.0, 180.0, "deg", 600, "Open Angle Outer", {}),
    (6021, "petal_open_inner", "float", 25.0, 0.0, 180.0, "deg", 600, "Open Angle Inner", {}),
    (6022, "petal_open_curve", "float", 1.0, 0.1, 10.0, "", 600, "Open Angle Falloff", {}),
    (6023, "petal_inner_size", "float", 0.55, 0.0, 2.0, "pct", 600, "Inner Petal Size", {"slider": True}),
    (6024, "petal_attach_outer", "float", 80.0, 0.0, 180.0, "deg", 600, "Attach Outer", {}),
    (6025, "petal_attach_inner", "float", 10.0, 0.0, 180.0, "deg", 600, "Attach Inner", {}),
    (6026, "petal_random", "float", 0.12, 0.0, 1.0, "pct", 600, "Size Randomness", {"slider": True}),
    (6027, "petal_rot_random", "float", 6.0, 0.0, 180.0, "deg", 600, "Angle Randomness", {}),
    (6028, "petal_thickness", "float", 0.04, 0.0, 10.0, "cm", 600, "Clearance", {}),

    # Calyx: receptacle and sepals
    (7001, "receptacle_radius", "float", 0.6, 0.001, 100.0, "cm", 700, "Receptacle Radius", {}),
    (7002, "sepal_on", "bool", True, 0, 0, "", 700, "Sepals", {}),
    (7003, "sepal_count", "int", 5, 1, 100, "", 700, "Sepal Count", {}),
    (7004, "sepal_length", "float", 2.2, 0.0, 1000.0, "cm", 700, "Sepal Length", {}),
    (7005, "sepal_width", "float", 0.8, 0.0, 1000.0, "cm", 700, "Sepal Width", {}),
    (7006, "sepal_open", "float", 120.0, 0.0, 180.0, "deg", 700, "Sepal Open Angle", {}),
    (7007, "sepal_curl", "float", -30.0, -360.0, 360.0, "deg", 700, "Sepal Curl", {}),

    # Center: stamens, pistil, disc
    (8001, "stamen_on", "bool", True, 0, 0, "", 800, "Stamens", {}),
    (8002, "stamen_count", "int", 30, 0, 2000, "", 800, "Stamen Count", {}),
    (8003, "stamen_length", "float", 1.3, 0.0, 100.0, "cm", 800, "Stamen Length", {}),
    (8004, "stamen_spread", "float", 35.0, 0.0, 180.0, "deg", 800, "Stamen Spread", {}),
    (8005, "stamen_curve", "float", 20.0, -180.0, 180.0, "deg", 800, "Stamen Curve", {}),
    (8006, "stamen_radius", "float", 0.025, 0.0, 10.0, "cm", 800, "Filament Radius", {}),
    (8007, "anther_size", "float", 0.12, 0.0, 10.0, "cm", 800, "Anther Size", {}),
    (8008, "pistil_on", "bool", True, 0, 0, "", 800, "Pistil", {}),
    (8009, "pistil_length", "float", 1.2, 0.0, 100.0, "cm", 800, "Pistil Length", {}),
    (8010, "pistil_radius", "float", 0.06, 0.0, 10.0, "cm", 800, "Pistil Radius", {}),
    (8011, "stigma_size", "float", 0.15, 0.0, 10.0, "cm", 800, "Stigma Size", {}),
    (8012, "disc_on", "bool", False, 0, 0, "", 800, "Disc Florets", {}),
    (8013, "disc_count", "int", 300, 0, 5000, "", 800, "Floret Count", {}),
    (8014, "disc_dome", "float", 0.35, 0.0, 1.0, "pct", 800, "Disc Dome", {"slider": True}),
    (8015, "floret_size", "float", 0.08, 0.0, 10.0, "cm", 800, "Floret Size", {}),

    # Materials (C4D only: links filled per part)
    (9001, "mat_petal", "link", None, 0, 0, "", 900, "Petals", {}),
    (9002, "mat_leaf", "link", None, 0, 0, "", 900, "Leaves", {}),
    (9003, "mat_stem", "link", None, 0, 0, "", 900, "Stem and Calyx", {}),
    (9004, "mat_center", "link", None, 0, 0, "", 900, "Center", {}),
    (9005, "mat_thorn", "link", None, 0, 0, "", 900, "Thorns", {}),
    (9006, "make_materials", "button", None, 0, 0, "", 900, "Create Default Materials", {}),

    # Quality
    (9501, "petal_res", "int", 18, 3, 200, "", 950, "Petal Rows", {}),
    (9502, "petal_res_v", "int", 11, 3, 200, "", 950, "Petal Columns", {}),
    (9503, "leaf_res", "int", 12, 3, 200, "", 950, "Leaf Rows", {}),
    (9504, "avoid_intersections", "bool", True, 0, 0, "", 950, "Avoid Petal Intersections", {}),
    (9505, "smooth", "bool", True, 0, 0, "", 950, "Smooth Shading", {}),
]

FIELDS = ("id", "key", "type", "default", "min", "max", "unit", "group", "label", "extra")
GROUPS = [(gid + ID_OFFSET, label) for gid, label in _GROUPS]
SPEC = []
for _row in _S:
    _p = dict(zip(FIELDS, _row))
    _p["id"] += ID_OFFSET
    _p["group"] += ID_OFFSET
    SPEC.append(_p)
BY_KEY = {p["key"]: p for p in SPEC}
BY_ID = {p["id"]: p for p in SPEC}

# Keys a preset may set (everything that describes the plant, not timing ranges or materials).
VALUE_TYPES = ("float", "int", "bool", "cycle")


def defaults():
    """Plain dict of every value parameter at its default."""
    return {p["key"]: p["default"] for p in SPEC if p["type"] in VALUE_TYPES}


def check_unique():
    ids = [p["id"] for p in SPEC]
    keys = [p["key"] for p in SPEC]
    assert len(ids) == len(set(ids)), "duplicate parameter id"
    assert len(keys) == len(set(keys)), "duplicate parameter key"
    return True
