from pathlib import Path
import unittest

from scripts.check_mono_hmetrics import (
    EXPECTED_EXCEPTIONAL_ADVANCES,
    exceptional_advances,
    minimum_metric_count,
    validate_font,
    variable_locations,
)


ROOT = Path(__file__).resolve().parent.parent
MONO_TTF = ROOT / "fonts" / "NamcheShadowMono" / "ttf"
MONO_VF = ROOT / "fonts" / "NamcheShadowMono" / "variable"


class MonoHorizontalMetricTest(unittest.TestCase):
    def testMinimumCountUsesOnlyTheTrailingSharedAdvance(self) -> None:
        self.assertEqual(minimum_metric_count([500, 0, 0, 600, 600]), 4)
        self.assertEqual(minimum_metric_count([600, 600, 600]), 1)

    def testTrackedUprightAndItalicMatchTheReviewedMinimum(self) -> None:
        self.assertEqual(validate_font(MONO_TTF / "NamcheShadowMono-Regular.ttf"), [])
        self.assertEqual(validate_font(MONO_TTF / "NamcheShadowMono-Italic.ttf"), [])

    def testExceptionalAdvancesArePinnedToGlyphNames(self) -> None:
        self.assertEqual(EXPECTED_EXCEPTIONAL_ADVANCES[".notdef"], 500)
        self.assertEqual(EXPECTED_EXCEPTIONAL_ADVANCES["acutecomb"], 0)
        self.assertEqual(len(EXPECTED_EXCEPTIONAL_ADVANCES), 40)

    def testVariableLocationsIncludeInstancesAndAxisExtremes(self) -> None:
        from fontTools.ttLib import TTFont

        font = TTFont(MONO_VF / "NamcheShadowMono[wght].ttf")
        try:
            locations = variable_locations(font)
            weights = {location["wght"] for location in locations}
            self.assertEqual(weights, {100, 200, 300, 400, 500, 600, 700, 800, 900})
            order = font.getGlyphOrder()
            for location in locations:
                self.assertEqual(
                    exceptional_advances(font, order, location),
                    EXPECTED_EXCEPTIONAL_ADVANCES,
                )
        finally:
            font.close()


if __name__ == "__main__":
    unittest.main()
