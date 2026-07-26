import copy
import sys
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "carousel"))

import generate  # noqa: E402


class GeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.example_path = ROOT / "carousel" / "briefs" / "example-brief.yaml"
        cls.example = yaml.safe_load(cls.example_path.read_text())

    def test_every_bundled_brief_validates(self):
        briefs = sorted((ROOT / "carousel" / "briefs").glob("*.yaml"))
        self.assertTrue(briefs)
        for path in briefs:
            with self.subTest(path=path.name):
                generate.validate(yaml.safe_load(path.read_text()))

    def test_structured_output_name(self):
        self.assertEqual(
            generate.output_name(self.example),
            "market-signals-housing-c01-demand-shifted-not-disappeared.pdf",
        )

    def test_old_brief_without_carousel_keeps_simple_name(self):
        brief = copy.deepcopy(self.example)
        brief.pop("carousel")
        self.assertEqual(
            generate.output_name(brief),
            "demand-shifted-not-disappeared.pdf",
        )

    def test_script_json_cannot_close_script_element(self):
        payload = {"headline": "</script><script>alert('x')</script>"}
        encoded = generate.script_safe_json(payload)
        self.assertNotIn("</script", encoded.lower())
        self.assertIn("\\u003c", encoded)

    def test_string_hook_is_rejected(self):
        brief = copy.deepcopy(self.example)
        brief["hook"] = "A statement without a number"
        with self.assertRaises(SystemExit) as raised:
            generate.validate(brief)
        self.assertIn("hook needs a number", str(raised.exception))


if __name__ == "__main__":
    unittest.main()

