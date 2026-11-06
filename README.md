# Flower Generator

One Flower object for Cinema 4D. Pick a preset, tweak it, and keyframe a single Bloom slider: the stem grows,
the leaves unroll, the bud swells and the petals open. Petals are layered so they never pass through each
other, on every frame, without a simulation. Everything is procedural and animatable, and it builds real polygon
objects with UVs, vertex maps and material slots, ready for any renderer.

[![Flower Generator demo: presets and the Bloom animation in Cinema 4D](docs/media/flower-demo-poster.png)](docs/media/flower-demo.mp4)

## Features

- Presets: Rose, Tulip, Daisy, Lily, Poppy, Lotus, Cherry Blossom, Wild Rose. Editing any shape control
  switches the menu to Custom.
- One Bloom control: a 0-100% slider you can keyframe, or a frame range, with timing for stem growth, leaf
  unfurl, bud swell, petal opening and stagger.
- No intersecting petals at any Bloom value.
- Stem: length, radius, taper, bend, wiggle, head nod, and an unfurling coil while it grows.
- Leaves: count, arrangement (alternate, opposite, spiral, whorled), outline, teeth, midrib fold, droop,
  twist, ruffle, petiole. Thorns: count, range, size, tilt, hook.
- Petals: spiral or whorls, outline, cup, curl, tip curl, twist, ruffle, open angles from outer to inner,
  per-petal randomness.
- Center: calyx and sepals, stamens with anthers, pistil, or daisy-style disc florets.
- Output: one polygon object per part with UVs, a "Base to Tip" vertex map and part selections.

## Requirements

- Cinema 4D 2027 (Python 3.11 or newer, no extra packages)
- Windows

Built and tested on Cinema 4D 2027 only. Nothing else has been tested.

## Install

1. Download the release from [GitHub Releases](https://github.com/KyleSullivan321/FlowerGenerator-C4D/releases)
   and unzip it.
2. Put the `FlowerGenerator` folder in Cinema 4D's `plugins` folder.
   Or choose **Edit > Preferences > Plugins > Add Folder** and pick the folder that contains `FlowerGenerator`.
3. Restart Cinema 4D.
4. Choose **Extensions > Flower**. The Flower object appears in the scene.

## Using it

Select the Flower object and open the Attribute Manager. The main tabs:

- **Flower**: the Preset menu, Seed and New Seed (a different random variation), the Bloom slider, Scale, and
  the Animate mode (Bloom Slider or Frame Range) with its start and end frames.
- **Bloom**: when each stage happens: stem growth, leaf unfurl, bud swell, petal opening and stagger.
- **Stem**, **Leaves**, **Thorns**: the plant body.
- **Petals**: arrangement, outline, cup, curl, twist, ruffle and open angles.
- **Calyx** and **Center**: sepals, stamens, pistil and disc florets.
- **Materials**: a link for each part, and a button that creates default materials.
- **Quality**: mesh resolution, smooth shading, and the petal intersection switch.

## Licence

Flower Generator is source-available under the [PolyForm Small Business License 1.0.0](LICENSE). It is free for
any use, commercial included, by individuals and by companies with fewer than 100 people and less than
1,000,000 USD (2019, adjusted for inflation) in revenue in the prior tax year. Larger companies need a
commercial licence: contact Kyle Sullivan at [kylesullivandesign.com](https://kylesullivandesign.com).

Source and releases: [github.com/KyleSullivan321/FlowerGenerator-C4D](https://github.com/KyleSullivan321/FlowerGenerator-C4D).
