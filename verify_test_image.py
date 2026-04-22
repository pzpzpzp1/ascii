"""
Verify round-trip fidelity: render_character_to_array → PNG → greedy_iou_white_weighted_method.

Expected result: 0 mismatches. Any failure indicates a bug in alignment,
thresholding, or character-matching logic.
"""
import numpy as np
from PIL import Image
import characters
from methods import render_character_to_array, greedy_iou_white_weighted_method

CW, CH = 7, 15

# Load reference
ref_path = 'test images/random_test_reference.txt'
with open(ref_path, encoding='utf-8') as f:
    ref_rows = [list(line.rstrip('\n')) for line in f if line.strip()]

# Detect duplicate binary patterns in the character set — if two chars render
# identically we can only distinguish them by pattern, not character identity.
char_list = characters.get_character_list('insta_tutorial')
pattern_to_chars: dict[bytes, list[str]] = {}
for char in char_list:
    key = render_character_to_array(char, CW, CH).tobytes()
    pattern_to_chars.setdefault(key, []).append(char)

dups = {k: v for k, v in pattern_to_chars.items() if len(v) > 1}
if dups:
    print(f"WARNING: {len(dups)} duplicate binary pattern(s) in character set:")
    for chars in dups.values():
        print(f"  {chars} share identical {CW}×{CH} pattern")
    print("Mismatches will be checked by pattern, not character identity.\n")
else:
    print(f"All {len(char_list)} characters have unique {CW}×{CH} binary patterns.\n")

# Convert PNG back to ASCII
img = Image.open('test images/random_test.png').convert('RGB')
print(f"Image size: {img.size}")

result = greedy_iou_white_weighted_method(
    img, scale=1.0, percentile=50,
    char_set='insta_tutorial', char_width=CW, char_height=CH, white_weight=0
)

rows, cols = result.shape
print(f"Result grid: {rows}×{cols}  (expected {len(ref_rows)}×{len(ref_rows[0])})\n")

mismatches = 0
for r in range(rows):
    for c in range(cols):
        got      = result[r, c]
        expected = ref_rows[r][c]
        if got == expected:
            continue
        # Allow match if binary patterns are identical (degenerate pair)
        got_pat = render_character_to_array(got,      CW, CH).tobytes()
        exp_pat = render_character_to_array(expected, CW, CH).tobytes()
        if got_pat == exp_pat:
            continue  # same pattern, different canonical name — not a real mismatch
        mismatches += 1
        print(f"  MISMATCH ({r},{c}): expected {expected!r}  got {got!r}")

total = rows * cols
print(f"Total cells : {total}")
print(f"Mismatches  : {mismatches}")
if mismatches == 0:
    print("PASS ✓  0 discrepancy")
else:
    print(f"FAIL ✗  {mismatches}/{total} mismatches")
