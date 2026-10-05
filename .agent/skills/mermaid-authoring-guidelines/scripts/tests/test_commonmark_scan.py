"""Tests for the CommonMark block scan of `mermaid_model` (TASK 110, R4 and R5).

1. Each branch of the scan that no other test takes has a test of its own (R5.1). The scan reaches
   every one of them; `_list_item` leaves the line at a column no output of the scan shows, so its
   test calls the function (R5.2).
2. The scan reads a document in time linear in its size (R4.4). The two shapes are the ones that
   took 1.88 s and 1.76 s before TASK 110.
3. The scan's output over seeded generated documents equals the output recorded before TASK 110
   changed the scan (R4.3). The digest covers the spans, the comment lines, the plain lines and the
   answer of `code_line_reader` for every line.
"""
import dataclasses
import hashlib
import random
import sys
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import mermaid_model as mm  # noqa: E402


def spans(lines):
    """`(open, close, info, indent, closed, body)` of each fenced block `_scan` finds."""
    return [(s.open, s.close, s.info, s.indent, s.closed, s.body) for s in mm._scan(lines)[0]]


class TestBranches(unittest.TestCase):
    """R5.1: one test per branch that the skill's suite did not take before TASK 110."""

    def test_a_tab_after_a_quote_marker_keeps_its_columns_as_spaces(self):
        # `>` ends at column 1 and the tab at column 4. The marker takes one column of the tab;
        # the plain line keeps the other two as spaces, and the fence stands at column 4.
        self.assertEqual(mm._quote_strip(">\tx"), (1, "  x"))
        self.assertEqual(spans([">\t```mermaid", ">\ta", ">\t```"]),
                         [(0, 2, "mermaid", 4, True, ["a"])])

    def test_an_empty_item_cannot_interrupt_a_paragraph(self):
        # CommonMark §5.2: `*` alone continues the paragraph, so the indented fence below is
        # paragraph text, not a fence inside an item.
        self.assertEqual(spans(["text", "*", "    ```mermaid", "    a", "    ```"]), [])

    def test_content_that_starts_as_indented_code_sits_one_column_after_the_marker(self):
        ln = mm._Line("-      code")
        self.assertEqual(mm._list_item(ln, False), 2)
        self.assertEqual((ln.offset, ln.column), (2, 2))

    def test_a_comment_that_its_blockquote_ends_is_a_comment(self):
        # The HTML block of kind 2 opens in the quote; the line without `>` ends the quote, and
        # with it the comment, before any `-->`.
        _spans, comments, _plain = mm._scan(["> <!--", "> a", "b"])
        self.assertEqual(comments, {0, 1})

    def test_a_quote_marker_without_a_space_takes_no_column_of_the_fence(self):
        self.assertEqual(spans([">```mermaid", ">a", ">```"]), [(0, 2, "mermaid", 1, True, ["a"])])

    def test_a_backtick_in_the_info_string_makes_no_fence(self):
        found = spans(["```a`b", "x", "```"])
        self.assertEqual([s[0] for s in found], [2])


class TestLinearTime(unittest.TestCase):
    """R4.4: both shapes measured 1.88 s and 1.76 s before TASK 110, and 0.04 s and 0.01 s after."""

    @staticmethod
    def _best_of_two(lines):
        best = None
        for _ in range(2):
            t0 = time.perf_counter()
            mm._scan(lines)
            took = time.perf_counter() - t0
            best = took if best is None else min(best, took)
        return best

    def test_a_staircase_of_nested_items(self):
        lines = [("  " * k) + "- x" for k in range(500)]
        took = self._best_of_two(lines)
        self.assertLess(took, 0.5, f"{took:.3f} s for 500 nested items")

    def test_nested_markers_then_blank_lines(self):
        lines = ["- " * 4000 + "x"] + [""] * 4000
        took = self._best_of_two(lines)
        self.assertLess(took, 0.25, f"{took:.3f} s for 4000 markers and 4000 blank lines")


#: Pieces of a generated line: indents and tabs, list and quote markers, fences, HTML block
#: starts and ends, headings, thematic breaks and text.
PIECES = ("", " ", "  ", "   ", "    ", "\t", " \t", "\t\t", "- ", "* ", "+ ", "1. ", "2) ", "10. ",
          "-", "1.", "> ", ">", "> > ", ">\t", "  > ", "```", "````", "~~~", "```mermaid",
          "```text figure", "``` `x`", "~~~ a`b", "<!--", "-->", "<div>", "</div>", "<pre>",
          "</pre>", "<x-y a=1>", "# ", "## h", "---", "***", "___", "- - -", "===", "para", "x",
          "code", "`y`", "<?", "?>", "<![CDATA[", "]]>", "<!X", ">")
SEED, DOCUMENTS = 110, 2000
#: sha256 of the scan output over the generated documents, recorded with the scan of the base
#: revision 6ae772b, before TASK 110 changed it.
BASE_DIGEST = "c7be4f52dcab8f83c9ce272ee5caedf1c34b0410807dc2160922e47335c58397"


def generated():
    rng = random.Random(SEED)
    for _ in range(DOCUMENTS):
        yield ["".join(rng.choice(PIECES) for _ in range(rng.randint(0, 9)))
               for _ in range(rng.randint(1, 60))]


def scan_digest():
    h = hashlib.sha256()
    for doc in generated():
        found, comments, plain = mm._scan(doc)
        read = mm.code_line_reader(doc)
        h.update(repr(([dataclasses.astuple(s) for s in found], sorted(comments), plain,
                       [read(i) for i in range(len(doc))])).encode("utf-8"))
    return h.hexdigest()


class TestUnchangedOutput(unittest.TestCase):
    """R4.3: the faster scan reads every generated document as the base scan did."""

    def test_the_scan_of_generated_documents_matches_the_base_scan(self):
        self.assertEqual(scan_digest(), BASE_DIGEST)


if __name__ == "__main__":
    unittest.main()
