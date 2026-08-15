from pathlib import Path
import json
import tempfile
import unittest

from fontTools.ttLib import TTFont

from scripts.check_pixel_shaping import (
    validate_font,
    validate_fontspector,
    validate_source,
)
from scripts.finalize_pixel_statics import finalize_font


ROOT = Path(__file__).resolve().parent.parent
PIXEL_SOURCE = ROOT / "sources" / "NamcheShadowPixel.glyphspackage"
PIXEL_FIXTURE = (
    ROOT / "fonts" / "NamcheShadowPixel" / "ttf" / "NamcheShadowPixel-Circle.ttf"
)


def remove_dotted_circle_and_layout(source: Path, output: Path) -> None:
    font = TTFont(source, recalcTimestamp=False)
    # Resolve every glyph name before shortening the glyph order. Otherwise
    # lazy glyf decompilation can no longer name the final glyph reliably.
    font.ensureDecompiled()
    glyph_name = (font.getBestCmap() or {})[0x25CC]
    for tag in ("GDEF", "GSUB", "GPOS"):
        del font[tag]
    for table in font["cmap"].tables:
        if table.isUnicode():
            table.cmap.pop(0x25CC, None)
    order = font.getGlyphOrder()
    if order[-1] != glyph_name:
        raise AssertionError("dotted-circle fixture must be the final glyph")
    order.pop()
    font["glyf"].glyphs.pop(glyph_name)
    font["hmtx"].metrics.pop(glyph_name)
    post = font["post"]
    if post.formatType == 2.0 and glyph_name in post.extraNames:
        post.extraNames.remove(glyph_name)
        post.mapping.pop(glyph_name, None)
    font.setGlyphOrder(order)
    font["maxp"].numGlyphs = len(order)
    font.save(output, reorderTables=False)
    font.close()


def fontspector_result(status: str = "PASS") -> dict:
    results = {}
    for style in ("Circle", "Grid", "Line", "Square", "Triangle"):
        results[f"fonts/NamcheShadowPixel/ttf/NamcheShadowPixel-{style}.ttf"] = {
            "Shaping Checks": [
                {"check_id": "dotted_circle", "worst_status": status},
                {"check_id": "soft_dotted", "worst_status": status},
            ]
        }
    return {"results": results}


class PixelShapingTest(unittest.TestCase):
    def test_source_uses_reviewed_dotted_circle(self) -> None:
        self.assertEqual(validate_source(PIXEL_SOURCE), [])

    def test_release_fixture_shapes_all_review_sequences(self) -> None:
        self.assertEqual(validate_font(PIXEL_FIXTURE), [])

    def test_finalizer_restores_glyph_and_layout_idempotently(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / PIXEL_FIXTURE.name
            remove_dotted_circle_and_layout(PIXEL_FIXTURE, path)
            self.assertTrue(finalize_font(path, PIXEL_FIXTURE))
            self.assertEqual(validate_font(path), [])
            first_result = path.read_bytes()
            self.assertFalse(finalize_font(path, PIXEL_FIXTURE))
            self.assertEqual(path.read_bytes(), first_result)

    def test_fontspector_gate_requires_both_checks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text(json.dumps(fontspector_result()))
            self.assertEqual(validate_fontspector(path), [])
            path.write_text(json.dumps(fontspector_result("WARN")))
            errors = validate_fontspector(path)
            self.assertEqual(len(errors), 10)
            self.assertIn("Circle dotted_circle", errors[0])


if __name__ == "__main__":
    unittest.main()
