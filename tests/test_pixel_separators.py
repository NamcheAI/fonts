from pathlib import Path
import tempfile
import unittest

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont

from scripts.check_pixel_separators import validate_font, validate_release
from scripts.finalize_pixel_statics import finalize_font


ROOT = Path(__file__).resolve().parent.parent
PIXEL_TTF = ROOT / "fonts" / "NamcheShadowPixel" / "ttf" / "NamcheShadowPixel-Circle.ttf"
PIXEL_FIXTURES = (
    ROOT / "fonts" / "NamcheShadowPixel" / "otf" / "NamcheShadowPixel-Circle.otf",
    PIXEL_TTF,
    ROOT
    / "fonts"
    / "NamcheShadowPixel"
    / "webfonts"
    / "NamcheShadowPixel-Circle.woff2",
)
SEPARATOR_NAMES = {"uni2028", "uni2029"}


def remove_separators(source: Path, output: Path) -> None:
    font = TTFont(source, recalcTimestamp=False)
    options = Options()
    options.retain_gids = False
    options.glyph_names = True
    subsetter = Subsetter(options=options)
    subsetter.populate(
        glyphs=[name for name in font.getGlyphOrder() if name not in SEPARATOR_NAMES]
    )
    subsetter.subset(font)
    font.save(output, reorderTables=False)
    font.close()


class PixelSeparatorTest(unittest.TestCase):
    # Long ``test_...`` identifiers trigger TruffleHog's Lob-key detector.
    # unittest still discovers these camel-case names because they start with "test".
    def testReleaseContainsInklessSeparators(self) -> None:
        self.assertEqual(validate_release(ROOT), [])

    def testMissingSeparatorIsRejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing-separator.ttf"
            font = TTFont(PIXEL_TTF, recalcTimestamp=False)
            for table in font["cmap"].tables:
                if table.isUnicode():
                    table.cmap.pop(0x2028, None)
            font.save(path, reorderTables=False)
            font.close()

            errors = validate_font(path)

        self.assertEqual(len(errors), 1)
        self.assertIn("missing U+2028", errors[0])

    def testFinalizerRestoresEveryStaticFormatIdempotently(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for source in PIXEL_FIXTURES:
                with self.subTest(suffix=source.suffix):
                    path = Path(directory) / source.name
                    remove_separators(source, path)
                    self.assertEqual(len(validate_font(path)), 2)

                    self.assertTrue(finalize_font(path))
                    self.assertEqual(validate_font(path), [])
                    first_result = path.read_bytes()

                    self.assertFalse(finalize_font(path))
                    self.assertEqual(path.read_bytes(), first_result)


if __name__ == "__main__":
    unittest.main()
