# me2_insta2_50_crop

This note documents the parameterization and processing used for the preferred `me2` ASCII result with the `insta2` character set at `50` percentile and center-crop alignment.

## Configuration Used

- input image: `test images/me2.png` now renamed to me.png
- method: `greedy_iou_white_weighted`
- method preset: `insta2_ww3_p50` (closest matching config name in `methods_config.yaml`)
- scale: `0.5`
- char set: `insta2` (from `characters/insta2.txt`)
- char cell size: `7 x 15` pixels
- threshold percentile: `50`
- white weight: `3`
- sidecar image config (`test images/me2.json`):
  - `scale: 1.0`
  - `percentile: 50`
  - `disable: false`

Note: method-level `percentile` in `methods_config.yaml` is applied directly, and in this case it matches the sidecar value (`50`).

## Processing Pipeline

1. Open image and convert to RGB if needed.
2. Resize by global method scale (`0.5`).
3. Center-crop to exact multiples of the character cell size (`7 x 15`) so each ASCII cell maps to a fixed pixel block with no remainder.
4. Convert to grayscale.
5. Compute threshold at grayscale percentile `50` (using non-extreme pixels), then binarize:
   - black/ink pixel if `gray < threshold`
   - white/background otherwise
6. Split the binary image into `7 x 15` patches (one patch per ASCII character position).
7. For each patch, score every candidate character rendered in `7 x 15`, then choose the highest-scoring character greedily.
8. Assemble the selected characters into the final ASCII grid and render/export outputs.

## Optimization Objective (Per Patch)

Character selection maximizes a white-weighted IOU score:

- `iou = intersection_black / union_black`
- `white_acc = both_white / total_pixels`
- `alpha = white_weight / (1 + white_weight)`
- `score = (1 - alpha) * iou + alpha * white_acc`

With `white_weight = 3`:

- `alpha = 3 / 4 = 0.75`
- Objective becomes:
  - `score = 0.25 * iou + 0.75 * white_acc`

Interpretation: the matcher strongly favors preserving background/negative space while still rewarding foreground (ink) overlap.

## Output Artifact

Primary rendered comparison output for this setup:

- `output/insta2_ww3_p50/me2_visualization.png`

