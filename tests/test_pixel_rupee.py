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
                    remove_rupee_mapping(source, path)
                    self.assertEqual(len(validate_font(path)), 1)

                    self.assertTrue(finalize_font(path, source))
                    self.assertEqual(validate_font(path), [])
                    first_result = path.read_bytes()

                    self.assertFalse(finalize_font(path, source))
                    self.assertEqual(path.read_bytes(), first_result)


if __name__ == "__main__":
    unittest.main()
