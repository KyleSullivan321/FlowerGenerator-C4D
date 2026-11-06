"""Preset flowers: overrides on top of params.defaults(). Index matches params.PRESET_NAMES."""

from . import params

_PRESETS = {
    "Rose": {
        "petal_arrangement": 0, "petal_count": 28, "petal_length": 4.0, "petal_width": 3.6,
        "petal_cup": 70.0, "petal_curl": -10.0, "petal_tip_curl": -45.0,
        "petal_open_outer": 100.0, "petal_open_inner": 22.0, "petal_inner_size": 0.55,
        "petal_attach_outer": 70.0, "petal_attach_inner": 10.0,
        "receptacle_radius": 1.0, "bud_petal_size": 0.5, "petal_res": 24, "petal_res_v": 14, "seed": 2,
        "thorn_on": True, "leaf_serration": 8, "leaf_count": 5, "leaf_length": 6.0, "leaf_width": 3.2,
        "leaf_width_pos": 0.4, "stamen_count": 30, "stamen_length": 0.8, "pistil_on": False,
    },
    "Tulip": {
        "petal_arrangement": 1, "petal_whorls": 2, "petal_per_whorl": 3,
        "petal_length": 5.5, "petal_width": 3.8, "petal_width_pos": 0.55, "petal_base": 0.35, "petal_tip": 0.35,
        "petal_cup": 100.0, "petal_curl": 6.0, "petal_tip_curl": -8.0, "petal_ruffle": 0.01,
        "petal_open_outer": 32.0, "petal_open_inner": 22.0, "petal_inner_size": 0.95,
        "petal_attach_outer": 70.0, "petal_attach_inner": 50.0, "petal_random": 0.05,
        "sepal_on": False, "receptacle_radius": 0.5,
        "leaf_count": 2, "leaf_arrangement": 0, "leaf_start": 0.0, "leaf_end": 0.12, "leaf_length": 18.0,
        "leaf_width": 5.0, "leaf_width_pos": 0.3, "leaf_tip": 0.6, "leaf_fold": 30.0, "leaf_angle": 22.0,
        "leaf_droop": 35.0, "leaf_petiole": 0.0, "leaf_top_scale": 0.8,
        "stem_length": 35.0, "stem_radius": 0.3, "stem_bend": 8.0, "stem_nod": 5.0, "stem_wiggle": 3.0,
        "stamen_count": 6, "stamen_length": 1.6, "stamen_spread": 10.0, "anther_size": 0.4,
        "stamen_radius": 0.04, "pistil_length": 1.4, "pistil_radius": 0.15, "stigma_size": 0.35,
    },
    "Daisy": {
        "petal_arrangement": 1, "petal_whorls": 2, "petal_per_whorl": 17,
        "petal_length": 2.8, "petal_width": 0.55, "petal_width_pos": 0.6, "petal_base": 0.4, "petal_tip": 0.2,
        "petal_notch": 0.45, "petal_cup": 15.0, "petal_curl": 0.0, "petal_tip_curl": -10.0, "petal_ruffle": 0.0,
        "petal_open_outer": 93.0, "petal_open_inner": 86.0, "petal_inner_size": 0.95,
        "petal_attach_outer": 86.0, "petal_attach_inner": 82.0, "petal_random": 0.08, "petal_rot_random": 4.0,
        "bud_curl": 70.0, "receptacle_radius": 0.9,
        "disc_on": True, "disc_count": 350, "disc_dome": 0.45, "floret_size": 0.09,
        "stamen_on": False, "pistil_on": False,
        "sepal_count": 13, "sepal_length": 0.7, "sepal_width": 0.25, "sepal_open": 110.0,
        "leaf_count": 6, "leaf_arrangement": 0, "leaf_start": 0.02, "leaf_end": 0.4, "leaf_length": 6.0,
        "leaf_width": 1.4, "leaf_serration": 4, "leaf_serration_depth": 0.25, "leaf_petiole": 0.0,
        "stem_length": 35.0, "stem_radius": 0.18, "stem_bend": 10.0, "stem_nod": 8.0,
    },
    "Lily": {
        "petal_arrangement": 1, "petal_whorls": 2, "petal_per_whorl": 3,
        "petal_length": 7.0, "petal_width": 2.4, "petal_width_pos": 0.4, "petal_base": 0.3, "petal_tip": 0.8,
        "petal_cup": 40.0, "petal_curl": -55.0, "petal_tip_curl": -60.0, "petal_ruffle": 0.06,
        "petal_ruffle_freq": 4.0, "petal_open_outer": 72.0, "petal_open_inner": 66.0, "petal_inner_size": 0.95,
        "petal_attach_outer": 60.0, "petal_attach_inner": 48.0, "petal_random": 0.05,
        "sepal_on": False, "receptacle_radius": 0.8,
        "stamen_count": 6, "stamen_length": 5.5, "stamen_spread": 25.0, "stamen_curve": 25.0,
        "anther_size": 0.6, "stamen_radius": 0.05, "pistil_length": 6.0, "pistil_radius": 0.07, "stigma_size": 0.3,
        "leaf_count": 12, "leaf_arrangement": 2, "leaf_start": 0.1, "leaf_end": 0.8, "leaf_length": 9.0,
        "leaf_width": 1.4, "leaf_width_pos": 0.4, "leaf_tip": 0.8, "leaf_droop": 40.0, "leaf_angle": 40.0,
        "leaf_petiole": 0.0, "stem_length": 50.0, "stem_nod": 35.0,
    },
    "Poppy": {
        "petal_arrangement": 1, "petal_whorls": 2, "petal_per_whorl": 2,
        "petal_length": 4.5, "petal_width": 5.5, "petal_width_pos": 0.7, "petal_base": 0.2, "petal_tip": 0.0,
        "petal_cup": 55.0, "petal_curl": 0.0, "petal_tip_curl": -15.0, "petal_ruffle": 0.12,
        "petal_ruffle_freq": 6.0, "petal_open_outer": 72.0, "petal_open_inner": 55.0, "petal_inner_size": 0.95,
        "petal_attach_outer": 72.0, "petal_attach_inner": 60.0,
        "sepal_on": False, "receptacle_radius": 0.45,
        "stamen_count": 120, "stamen_length": 0.8, "stamen_spread": 50.0, "anther_size": 0.08,
        "stamen_radius": 0.015, "pistil_length": 0.8, "pistil_radius": 0.35, "stigma_size": 0.6,
        "leaf_count": 3, "leaf_start": 0.0, "leaf_end": 0.2, "leaf_serration": 6, "leaf_serration_depth": 0.35,
        "stem_length": 45.0, "stem_radius": 0.2, "stem_wiggle": 15.0, "stem_nod": 0.0,
    },
    "Lotus": {
        "petal_arrangement": 1, "petal_whorls": 4, "petal_per_whorl": 8,
        "petal_length": 6.0, "petal_width": 2.6, "petal_width_pos": 0.5, "petal_tip": 0.6,
        "petal_cup": 90.0, "petal_curl": 5.0, "petal_tip_curl": -5.0, "petal_ruffle": 0.0,
        "petal_open_outer": 85.0, "petal_open_inner": 50.0, "petal_open_curve": 1.5, "petal_inner_size": 0.75,
        "petal_attach_outer": 85.0, "petal_attach_inner": 45.0,
        "petal_thickness": 0.1, "petal_res": 24, "petal_res_v": 14,
        "sepal_on": False, "leaf_on": False, "receptacle_radius": 1.8,
        "stamen_count": 80, "stamen_length": 1.2, "anther_size": 0.15,
        "pistil_length": 1.0, "pistil_radius": 0.3, "stigma_size": 1.0,
        "stem_length": 30.0, "stem_bend": 0.0, "stem_nod": 0.0, "stem_wiggle": 2.0,
    },
    "Cherry Blossom": {
        "petal_arrangement": 1, "petal_whorls": 1, "petal_per_whorl": 5,
        "petal_length": 1.6, "petal_width": 1.4, "petal_width_pos": 0.65, "petal_base": 0.3, "petal_tip": 0.0,
        "petal_notch": 0.8, "petal_cup": 25.0, "petal_curl": 0.0, "petal_tip_curl": -15.0,
        "petal_open_outer": 80.0, "petal_attach_outer": 75.0, "petal_thickness": 0.02,
        "receptacle_radius": 0.25, "sepal_length": 0.5, "sepal_width": 0.35, "sepal_open": 130.0,
        "stamen_count": 35, "stamen_length": 0.9, "stamen_spread": 30.0, "anther_size": 0.06,
        "stamen_radius": 0.012, "pistil_length": 0.9, "pistil_radius": 0.02, "stigma_size": 0.05,
        "stem_length": 6.0, "stem_radius": 0.08, "stem_bend": 30.0, "stem_wiggle": 4.0, "leaf_on": False,
    },
    "Wild Rose": {
        "petal_arrangement": 1, "petal_whorls": 1, "petal_per_whorl": 5,
        "petal_length": 2.8, "petal_width": 3.0, "petal_width_pos": 0.65, "petal_tip": 0.0, "petal_notch": 0.35,
        "petal_cup": 35.0, "petal_curl": 0.0, "petal_tip_curl": -10.0, "petal_open_outer": 85.0,
        "petal_attach_outer": 78.0, "stamen_count": 80, "stamen_length": 0.6, "stamen_spread": 40.0,
        "anther_size": 0.07, "stamen_radius": 0.015, "pistil_length": 0.4,
        "thorn_on": True, "leaf_serration": 8, "leaf_length": 4.5, "leaf_width": 2.4,
    },
}


def preset_values(index):
    """Full value dict for a preset index (0 = Custom returns None)."""
    if index <= 0 or index >= len(params.PRESET_NAMES):
        return None
    vals = params.defaults()
    vals.update(_PRESETS.get(params.PRESET_NAMES[index], {}))
    vals["preset"] = index
    return vals
