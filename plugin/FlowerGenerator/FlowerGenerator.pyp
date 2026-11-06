"""Flower Generator for Cinema 4D: registers the Flower object.

All behaviour lives in flowergen_c4d.py and the flowergen core next to this file.
"""

import os
import sys

import c4d

# Permanent plugin ID registered with Maxon. Scenes store the object by this ID: never change it.
PLUGIN_ID = 1073482

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import flowergen_c4d as bridge  # noqa: E402


class FlowerObject(c4d.plugins.ObjectData):
    def __init__(self):
        self.state = {}

    def Init(self, node, *args):
        return bridge.init(node)

    def GetDDescription(self, node, description, flags):
        return bridge.get_ddescription(node, description, flags)

    def GetDEnabling(self, node, id, t_data, flags, itemdesc):
        return bridge.get_denabling(node, id, flags)

    def Message(self, node, type, data):
        return bridge.message(node, type, data)

    def GetVirtualObjects(self, op, hh):
        return bridge.get_virtual_objects(self.state, op, hh)


def _icon():
    path = os.path.join(HERE, "res", "flower.png")
    bmp = c4d.bitmaps.BaseBitmap()
    if os.path.exists(path) and bmp.InitWith(path)[0] == c4d.IMAGERESULT_OK:
        return bmp
    return None


if __name__ == "__main__":
    c4d.plugins.RegisterObjectPlugin(id=PLUGIN_ID, str="Flower", g=FlowerObject, description="Oflowergen",
                                     icon=_icon(), info=c4d.OBJECT_GENERATOR)
