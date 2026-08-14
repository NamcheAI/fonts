from pathlib import Path
import tempfile
import unittest

from fontTools.ttLib import TTFont

from scripts.check_pixel_ligature_carets import validate_font
from scripts.finalize_pixel_statics import finalize_font, source_ligature_carets


ROOT = Path(__file__).resolve().parent.parent
PIXEL_FIXTURES = (
    ROOT / "fonts" / "NamcheShadowPixel" / "otf" / "NamcheShadowPixel-Circle.otf",
    ROOT / "fonts" / "NamcheShadowPixel" / "ttf" / "NamcheShadowPixel-Circle.ttf",
    ROOT
    / "fonts"
    / "NamcheShadowPixel"
    / "webfonts"
    / "NamcheShadowPixel-Circle.woff2",
)


def remove_ligature_carets(source: Path, output: Path) -> None:
    font = TTFont(source, recalcTimestamp=False)
    font["GDEF"].table.LigCaretList = None
    font.save(output, reorderTables=False)
    font.close()


class PixelLigatureCaretTest(unittest.TestCase):
    def testMissingCaretsAreRejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing-carets.ttf"
            remove_ligature_carets(PIXEL_FIXTURES[1], path)
            errors = validate_font(path)

        self.assertEqual(len(errors), len(source_ligature_carets()))
        self.assertTrue(all("caret coordinates" in error for error in errors))

    def testFinalizerRestoresEveryStaticFormatIdempotently(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for source in PIXEL_FIXTURES:
                with self.subTest(suffix=source.suffix):
                    path = Path(directory) / source.name
                    remove_ligature_carets(source, path)
                    self.assertEqual(
                        len(validate_font(path)), len(source_ligature_carets())
                    )

                    self.assertTrue(finalize_font(path))
                    self.assertEqual(validate_font(path), [])
                    first_result = path.read_bytes()

                    self.assertFalse(finalize_font(path))
                    self.assertEqual(path.read_bytes(), first_result)


if __name__ == "__main__":
    unittest.main()
