"""
Character Set Enumeration for ASCII Art

This module defines the valid characters that can be used for ASCII art generation.

RATIONALE FOR CHARACTER SELECTION:
1. Basic ASCII printable characters (space through ~) provide a good baseline, ordered
   roughly by visual density/darkness when rendered in monospace fonts.

2. Extended ASCII and Unicode box-drawing characters (─│┌┐└┘├┤┬┴┼) provide useful
   structural elements for line-based art.

3. Unicode block elements (░▒▓█▀▄) provide gradient shading capabilities that
   standard ASCII lacks, offering better tonal range.

4. Special symbols (•◦○●◘◙) provide circular elements useful for organic shapes.

5. Japanese katakana characters (シツノ etc.) are included as they can provide unique
   textures and patterns. However, their rendering depends on font support.

ORDERING:
Characters are roughly ordered from lightest (space, dot) to darkest (█, @, #)
based on their visual density. This ordering helps with brightness-based character
selection algorithms.

EXCLUSIONS:
- Whitespace characters other than space (tabs, newlines) are excluded
- Characters that don't render consistently across fonts are excluded
- Characters that are too similar visually may be excluded to avoid redundancy
"""

# Core ASCII characters ordered roughly by visual density (light to dark)
ASCII_LIGHT = " .`'-,~"
ASCII_MID_LIGHT = "^:;\"!><"
ASCII_MID = "+=*irlctsz"
ASCII_MID_DARK = "vxojnuyf"
ASCII_DARK = "kJCae{}[]()/|\\1?-IYL"
ASCII_VERY_DARK = "VT7wmUOQ0Z"
ASCII_DARKEST = "MWB8%&#@"

# Box drawing characters (useful for structured patterns)
BOX_DRAWING = "─│┌┐└┘├┤┬┴┼"

# Block elements (gradient shading)
BLOCKS = "░▒▓█▀▄▌▐"

# Special symbols
SYMBOLS = "•◦○●◘◙"

# Japanese katakana (texture elements - requires font support)
KATAKANA = "シツノリエワサキユナモセスン"

# Combined character set - can be configured based on needs
ALL_CHARACTERS = ASCII_LIGHT + ASCII_MID_LIGHT + ASCII_MID + ASCII_MID_DARK + ASCII_DARK + ASCII_VERY_DARK + ASCII_DARKEST + BOX_DRAWING + BLOCKS + SYMBOLS + KATAKANA

# Standard ASCII-only set (most compatible)
STANDARD_ASCII = ASCII_LIGHT + ASCII_MID_LIGHT + ASCII_MID + ASCII_MID_DARK + ASCII_DARK + ASCII_VERY_DARK + ASCII_DARKEST

# Extended set with Unicode (better visual quality)
EXTENDED_SET = STANDARD_ASCII + BOX_DRAWING + BLOCKS + SYMBOLS

# Minimal set for testing (just basic density range)
MINIMAL_SET = " .:-=+*#%@"


def get_character_set(mode='extended'):
    """
    Get a character set based on the specified mode.

    Args:
        mode (str): One of 'minimal', 'standard', 'extended', 'all'

    Returns:
        str: String containing all valid characters for the mode
    """
    modes = {
        'minimal': MINIMAL_SET,
        'standard': STANDARD_ASCII,
        'extended': EXTENDED_SET,
        'all': ALL_CHARACTERS
    }

    if mode not in modes:
        raise ValueError(f"Invalid mode '{mode}'. Choose from: {list(modes.keys())}")

    return modes[mode]


def get_character_list(mode='extended'):
    """
    Get a list of individual characters.

    Args:
        mode (str): One of 'minimal', 'standard', 'extended', 'all'

    Returns:
        list: List of individual character strings
    """
    return list(get_character_set(mode))


def process_character_dumps():
    """
    Process characters/characterdump.txt and characters/uniquecharacterdump.txt to create a unique set
    of characters not already in the predefined character sets.

    Reads both files, combines characters, removes duplicates, excludes any
    characters already defined in ALL_CHARACTERS, detects irregular characters
    (fullwidth, modifiers, etc.), and writes results to appropriate files.
    """
    import os
    import unicodedata

    def is_irregular(char):
        """
        Detect irregular characters that may cause rendering issues.

        Returns True for:
        - Fullwidth characters (U+FF00-FFEF)
        - Halfwidth characters (U+FF61-FFDC)
        - Modifier letters (U+02B0-02FF)
        - Combining diacritical marks (U+0300-036F)
        - Ideographic space (U+3000)
        - Other confusable characters
        """
        code = ord(char)

        # Fullwidth and halfwidth forms
        if 0xFF00 <= code <= 0xFFEF:
            return True

        # Modifier letters
        if 0x02B0 <= code <= 0x02FF:
            return True

        # Combining diacritical marks
        if 0x0300 <= code <= 0x036F:
            return True

        # Ideographic space
        if code == 0x3000:
            return True

        # Check Unicode category for other problematic types
        category = unicodedata.category(char)
        if category in ('Mn', 'Mc', 'Me'):  # Mark categories
            return True

        return False

    # Get all currently defined characters
    existing_chars = set(ALL_CHARACTERS)

    # Collect all characters from dump files
    all_dump_chars = set()

    # Read characterdump.txt if it exists
    if os.path.exists('characters/characterdump.txt'):
        with open('characters/characterdump.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            all_dump_chars.update(content)
        print(f"Read {len(content)} characters from characters/characterdump.txt")
    else:
        print("characters/characterdump.txt not found")

    # Read uniquecharacterdump.txt if it exists
    if os.path.exists('characters/uniquecharacterdump.txt'):
        with open('characters/uniquecharacterdump.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            all_dump_chars.update(content)
        print(f"Read {len(content)} characters from characters/uniquecharacterdump.txt")
    else:
        print("characters/uniquecharacterdump.txt not found")

    # Remove whitespace control characters except space
    all_dump_chars.discard('\n')
    all_dump_chars.discard('\r')
    all_dump_chars.discard('\t')
    all_dump_chars.discard('\x0b')  # vertical tab
    all_dump_chars.discard('\x0c')  # form feed

    # Separate irregular characters
    irregular_chars = set()
    regular_chars = set()

    for char in all_dump_chars:
        if is_irregular(char):
            irregular_chars.add(char)
        else:
            regular_chars.add(char)

    # Get unique characters not in existing sets
    new_chars = regular_chars - existing_chars
    new_irregular = irregular_chars - existing_chars

    print(f"\nTotal unique characters in dumps: {len(all_dump_chars)}")
    print(f"  Regular: {len(regular_chars)}")
    print(f"  Irregular: {len(irregular_chars)}")
    print(f"Characters already in characters.py: {len((regular_chars | irregular_chars) - (new_chars | new_irregular))}")
    print(f"New unique regular characters: {len(new_chars)}")
    print(f"New unique irregular characters: {len(new_irregular)}")

    # Write unique new regular characters to uniquecharacterdump.txt
    with open('characters/uniquecharacterdump.txt', 'w', encoding='utf-8') as f:
        # Sort characters for consistency (by Unicode code point)
        sorted_chars = sorted(new_chars)
        f.write(''.join(sorted_chars))

    print(f"\nWrote {len(new_chars)} regular characters to characters/uniquecharacterdump.txt")

    # Write irregular characters to irregulars.txt
    if new_irregular or irregular_chars:
        # Read existing irregulars if file exists
        existing_irregulars = set()
        if os.path.exists('characters/irregulars.txt'):
            with open('characters/irregulars.txt', 'r', encoding='utf-8') as f:
                existing_irregulars.update(f.read())

        # Combine with new irregulars
        all_irregulars = existing_irregulars | irregular_chars
        sorted_irregulars = sorted(all_irregulars)

        with open('characters/irregulars.txt', 'w', encoding='utf-8') as f:
            f.write(''.join(sorted_irregulars))

        print(f"Wrote {len(all_irregulars)} irregular characters to characters/irregulars.txt")

    # Replace characterdump.txt with placeholder message
    with open('characters/characterdump.txt', 'w', encoding='utf-8') as f:
        f.write('dump characters here for collection')

    print("Reset characters/characterdump.txt to placeholder")

    # Print a sample of the new characters
    if new_chars:
        sample = list(sorted_chars)[:50]
        print(f"\nSample of new regular characters (first 50):")
        print(''.join(sample))
        print(f"Character codes: {[hex(ord(c)) for c in sample[:10]]}")

    if new_irregular:
        import unicodedata
        sample_irreg = list(sorted(new_irregular))[:20]
        print(f"\nNew irregular characters detected:")
        for char in sample_irreg:
            print(f"  '{char}' - U+{ord(char):04X} - {unicodedata.name(char, 'UNKNOWN')}")

    return new_chars, new_irregular


if __name__ == "__main__":
    # Process character dumps to find new unique characters
    print("Processing Character Dumps\n" + "="*60)
    process_character_dumps()

    # Print information about available character sets
    print("\n\n" + "ASCII Art Character Sets\n" + "="*60)

    for mode in ['minimal', 'standard', 'extended', 'all']:
        chars = get_character_set(mode)
        print(f"\n{mode.upper()} ({len(chars)} characters):")
        print(f"  {repr(chars)}")
        print(f"  Sample: {chars[:20]}")
