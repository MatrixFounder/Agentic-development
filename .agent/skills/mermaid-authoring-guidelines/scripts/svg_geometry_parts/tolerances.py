"""Instrument tolerances of the SVG geometry: stroke width, flattening error, text
overhang and the like. They are not thresholds (TASK 125)."""

from __future__ import annotations


FLATTEN_TOL_PX = 0.3          # maximum distance of a flattened Bezier from the true curve
SAMPLE_STEP_PX = 1.0          # step when an edge is sampled inside a node outline
SHARED_END_MARGIN_PX = 10.0   # an intersection this close to a node both edges touch is a join
DEDUPE_RADIUS_PX = 4.0        # intersection points closer than this are one crossing
END_SNAP_PX = 12.0            # an edge end this close to a node box attaches to that node
THROUGH_NOISE_PX = 2.0        # a stroke within this distance of a node border runs along it
THROUGH_MIN_RUN_PX = 3.0      # a run inside a node shorter than this is a corner touch
TITLE_MIN_INSIDE_PX = 2.0     # edge length inside a title box that counts as a crossing
TITLE_NEAR_MARGIN_PX = 4.0    # margin around a reserved title box that makes a near miss
OVERLAP_MIN_AREA_PX2 = 4.0    # overlap area below this is anti-aliasing
EDGE_IN_LABEL_MIN_PX = 3.0    # edge length inside another edge's label box that counts
CLIP_TOL_PX = 2.0             # text overhang allowed past the box of an HTML label (reserved
                              # space inside a padded shape) or past the figure's edge, whatever
                              # the box width. Measured 2026-10-03 on the 147 reference renders:
                              # 0 px on every positive figure, 1.17 px on the one drawn in a
                              # fallback font (renderer-facts.md, MA-SET-03)
PAINTED_CLIP_TOL_PX = 0.5     # text overhang allowed past the box of SVG text that is the drawn
                              # outline around it (PAINTED_BOX_KINDS): half a 1 px outline. A
                              # note line 1.82 px past its box shows ink past the border in the
                              # PNG (TASK 108 calibration, 2026-10-03)
PAINTED_BOX_KINDS = ("note", "actor", "task")  # SVG text measured against its drawn rectangle
GANTT_EDGE_TOL_PX = 0.5       # a gantt label this far past the chart edge is cut off
MESSAGE_END_SNAP_PX = 25.0    # a message end this close to a lifeline belongs to it (activation
                              # bars move the end 5 px per nesting level)
LIFELINE_LABEL_MARGIN_PX = 2.0  # a lifeline this far inside a label's glyph box strikes it

