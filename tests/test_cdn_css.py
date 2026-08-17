from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
CSS = ROOT / "documentation/cdn/fonts.css"


class CdnCssTests(unittest.TestCase):
    def test_every_local_source_exists_in_the_release_tree(self) -> None:
        sources = re.findall(r'url\("\./([^"?]+)"\)', CSS.read_text())
        self.assertGreater(len(sources), 0)
        missing = [source for source in sources if not (ROOT / "fonts" / source).is_file()]
        self.assertEqual(missing, [])

    def test_all_faces_define_display_policy(self) -> None:
        css = CSS.read_text()
        self.assertEqual(css.count("@font-face"), css.count("font-display: swap"))


if __name__ == "__main__":
    unittest.main()

