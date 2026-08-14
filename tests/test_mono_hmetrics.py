from pathlib import Path
import unittest

from scripts.check_mono_hmetrics import minimum_metric_count, validate_font


ROOT = Path(__file__).resolve().parent.parent
MONO_TTF = ROOT / "fonts" / "NamcheShadowMono" / "ttf"


class MonoHorizontalMetricTest(unittest.TestCase):
    def testMinimumCountUsesOnlyTheTrailingSharedAdvance(self) -> None:
        self.assertEqual(minimum_metric_count([500, 0, 0, 600, 600]), 4)
        self.assertEqual(minimum_metric_count([600, 600, 600]), 1)

    def testTrackedUprightAndItalicMatchTheReviewedMinimum(self) -> None:
        self.assertEqual(validate_font(MONO_TTF / "NamcheShadowMono-Regular.ttf"), [])
        self.assertEqual(validate_font(MONO_TTF / "NamcheShadowMono-Italic.ttf"), [])


if __name__ == "__main__":
    unittest.main()
