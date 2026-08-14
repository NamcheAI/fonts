import json
from pathlib import Path
import tempfile
import unittest

from scripts.check_language_shaping import validate_report


def report(
    message: str,
    soft_dotted_status: str = "PASS",
    font_path: str = "fonts/NamcheShadowSans/ttf/NamcheShadowSans-Regular.ttf",
) -> dict:
    return {
        "results": {
            font_path: {
                "Google Fonts": [
                    {
                        "check_id": "soft_dotted",
                        "worst_status": soft_dotted_status,
                    },
                    {
                        "check_id": "googlefonts/glyphsets/shape_languages",
                        "worst_status": "WARN",
                        "subresults": [{"message": message}],
                    },
                ]
            }
        }
    }


class LanguageShapingReportTest(unittest.TestCase):
    def validate(self, data: dict) -> tuple[int, list[str]]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text(json.dumps(data))
            return validate_report(path)

    def test_accepts_documented_auxiliary_omissions(self) -> None:
        message = "\n".join(
            [
                "Warning language shaping:",
                "| Auxiliary orthography codepoints: | * da_Latn (Danish) |",
                "| The following auxiliary characters are missing from the font: Ǿ | |",
                "| The following auxiliary characters are missing from the font: ǿ | |",
            ]
        )

        checked, errors = self.validate(report(message))

        self.assertEqual(checked, 1)
        self.assertEqual(errors, [])

    def test_rejects_undocumented_auxiliary_omission(self) -> None:
        message = (
            "The following auxiliary characters are missing from the font: Å |"
        )

        _, errors = self.validate(report(message))

        self.assertEqual(
            errors,
            [
                "fonts/NamcheShadowSans/ttf/NamcheShadowSans-Regular.ttf: "
                "undocumented auxiliary omissions: Å"
            ],
        )

    def test_allows_parked_yus_only_in_sans_variable(self) -> None:
        message = (
            "The following auxiliary characters are missing from the font: ѫ |"
        )
        variable_path = (
            "fonts/NamcheShadowSans/variable/NamcheShadowSans[wght].ttf"
        )

        _, variable_errors = self.validate(
            report(message, font_path=variable_path)
        )
        _, static_errors = self.validate(report(message))

        self.assertEqual(variable_errors, [])
        self.assertEqual(len(static_errors), 1)
        self.assertIn("undocumented auxiliary omissions: ѫ", static_errors[0])

    def test_rejects_real_shaping_warning(self) -> None:
        _, errors = self.validate(report("Shaper failed to attach acutecomb"))

        self.assertEqual(len(errors), 1)
        self.assertIn("retained real shaping warning: Shaper ", errors[0])

    def test_rejects_soft_dotted_failure(self) -> None:
        _, errors = self.validate(report("", soft_dotted_status="WARN"))

        self.assertEqual(len(errors), 1)
        self.assertIn("soft_dotted is WARN instead of PASS", errors[0])


if __name__ == "__main__":
    unittest.main()
