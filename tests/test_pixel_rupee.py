from pathlib import Path
import tempfile
import unittest

from fontTools.ttLib import TTFont

from scripts.check_pixel_rupee import validate_font, validate_source
from scripts.finalize_pixel_statics import finalize_font


ROOT = Path(__file__).resolve().parent.parent
PIXEL_SOURCE = ROOT / "sources" / "NamcheShadowPixel.glyphspackage"
PIXEL_FIXTURES = (
    ROOT / "fonts" / "NamcheShadowPixel" / "otf" / "NamcheShadowPixel-Circle.otf",
    ROOT / "fonts" / "NamcheShadowPixel" / "ttf" / "NamcheShadowPixel-Circle.ttf",
    ROOT
    / "fonts"
    / "NamcheShadowPixel"
    / "webfonts"
    / "NamcheShadowPixel-Circle.woff2",
)


def remove_rupee_mapping(source: Path, output: Path) -> None:
    font = TTFont(source, recalcTimestamp=False)
    for table in font["cmap"].tables:
        if table.isUnicode():
            table.cmap.pop(0x20B9, None)
    font.save(output, reorderTables=False)
    font.close()


def remove_rupee_glyph(source: Path, output: Path) -> None:
    font = TTFont(source, recalcTimestamp=False)
    glyph_name = (font.getBestCmap() or {})[0x20B9]
    for table in font["cmap"].tables:
        if table.isUnicode():
            table.cmap.pop(0x20B9, None)

    glyf = font["glyf"] if "glyf" in font else None
    top_dict = font["CFF "].cff.topDictIndex[0] if "CFF " in font else None
    charstrings = top_dict.CharStrings if top_dict is not None else None
    if charstrings is not None:
        _ = charstrings.charStrings[glyph_name]
    hmtx = font["hmtx"]
    post = font["post"]
    order = font.getGlyphOrder()
    if order[-1] != glyph_name:
        raise AssertionError("rupee fixture must be the final glyph")
    order.pop()
    if glyf is not None:
        glyf.glyphs.pop(glyph_name)
    else:
        assert top_dict is not None
        assert charstrings is not None
        index = charstrings.charStrings.pop(glyph_name)
        if index != len(charstrings.charStringsIndex) - 1:
            raise AssertionError("rupee CFF fixture must use the final charstring")
        charstrings.charStringsIndex.items.pop()
        if glyph_name in top_dict.charset:
            top_dict.charset.remove(glyph_name)
    hmtx.metrics.pop(glyph_name)
    if post.formatType == 2.0 and glyph_name in post.extraNames:
        post.extraNames.remove(glyph_name)
        post.mapping.pop(glyph_name, None)
    font.setGlyphOrder(order)
    font["maxp"].numGlyphs = len(order)
    font.save(output, reorderTables=False)
    font.close()


class PixelRupeeTest(unittest.TestCase):
    def testSourceUsesReviewedPixelRecipe(self) -> None:
        self.assertEqual(validate_source(PIXEL_SOURCE), [])

    def testMissingRupeeIsRejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing-rupee.ttf"
            remove_rupee_mapping(PIXEL_FIXTURES[1], path)
            errors = validate_font(path)

        self.assertEqual(len(errors), 1)
        self.assertIn("missing U+20B9 ₹", errors[0])

    def testFinalizerRestoresEveryStaticFormatIdempotently(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for source in PIXEL_FIXTURES:
                with self.subTest(suffix=source.suffix):
                    path = Path(directory) / source.name
                    remove_rupee_glyph(source, path)
                    self.assertEqual(len(validate_font(path)), 1)

                    self.assertTrue(finalize_font(path, source))
                    self.assertEqual(validate_font(path), [])
                    restored = TTFont(path, recalcTimestamp=False)
                    if "CFF " in restored:
                        top_dict = restored["CFF "].cff.topDictIndex[0]
                        self.assertEqual(restored.getGlyphOrder(), top_dict.charset)
                    restored.close()
                    first_result = path.read_bytes()

                    self.assertFalse(finalize_font(path, source))
                    self.assertEqual(path.read_bytes(), first_result)


if __name__ == "__main__":
    unittest.main()
