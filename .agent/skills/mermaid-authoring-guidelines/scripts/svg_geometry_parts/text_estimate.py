"""Text estimate of the SVG geometry: the width of a text with no browser measure
(TASK 125)."""

from __future__ import annotations


# Helvetica advance widths (1/1000 em) for ASCII 32..126. Used only where the SVG carries no
# width and no browser measurement was supplied: sequence and gantt <text>. Error up to ~16 %.
_HELVETICA = [278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278,
              556, 556, 556, 556, 556, 556, 556, 556, 556, 556, 278, 278, 584, 584, 584, 556,
              1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833, 722, 778,
              667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469, 556,
              333, 556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556,
              556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500, 334, 260, 334, 584]


def estimate_text_width(text: str, font_px: float) -> float:
    """Approximate advance width of *text* in px (Helvetica metrics; no browser)."""
    units = 0
    for ch in text:
        o = ord(ch)
        if 32 <= o <= 126:
            units += _HELVETICA[o - 32]
        elif o >= 0x2E80:
            units += 1000      # CJK and other full-width scripts
        elif o in (0x2014, 0x2026, 0x2192):
            units += 1000      # em dash, ellipsis, arrow
        else:
            units += 600       # Cyrillic, Greek, Latin-1 and other letters, rough average
    return units * font_px / 1000.0


