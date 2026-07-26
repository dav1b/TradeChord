import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOKEN_PATH = ROOT / "tokens" / "dj-design.css"
GUIDANCE_PATH = ROOT / "guidance" / "02-color-system.md"
RENDERER_PATH = ROOT / "carousel" / "renderer" / "slides.js"


def relative_luminance(hex_color):
    channels = [int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [
        value / 12.92
        if value <= 0.04045
        else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(first, second):
    high, low = sorted(
        (relative_luminance(first), relative_luminance(second)), reverse=True
    )
    return (high + 0.05) / (low + 0.05)


def root_variables(css):
    root = re.search(r":root\s*\{(.*?)\n\}", css, re.DOTALL)
    if not root:
        raise AssertionError("token file has no :root block")
    return dict(
        re.findall(r"--([\w-]+)\s*:\s*([^;]+);", root.group(1))
    )


class ColorSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = TOKEN_PATH.read_text()
        cls.guidance = GUIDANCE_PATH.read_text()
        cls.renderer = RENDERER_PATH.read_text()
        cls.tokens = root_variables(cls.css)

    def resolve(self, token, seen=None):
        seen = set() if seen is None else seen
        self.assertNotIn(token, seen, f"circular token reference at --{token}")
        seen.add(token)
        value = self.tokens[token].strip()
        reference = re.fullmatch(r"var\(--([\w-]+)\)", value)
        return self.resolve(reference.group(1), seen) if reference else value

    def test_parchment_mark_variants_clear_normal_text_contrast(self):
        parchment = self.resolve("dj-parchment")
        mark_tokens = (
            "dj-honey-bronze-mark",
            "dj-lagoon-teal-mark",
            "dj-ember-copper-mark",
            "dj-fern-green-mark",
        )
        for token in mark_tokens:
            with self.subTest(token=token):
                ratio = contrast_ratio(self.resolve(token), parchment)
                self.assertGreaterEqual(ratio, 4.5)

    def test_plum_base_is_its_own_parchment_safe_mark(self):
        ratio = contrast_ratio(
            self.resolve("dj-plum-violet"), self.resolve("dj-parchment")
        )
        self.assertGreaterEqual(ratio, 4.5)
        self.assertEqual(self.tokens["re-mark"], "var(--dj-plum-violet)")

    def test_semantic_fill_and_mark_roles_stay_paired(self):
        expected = {
            "delta-pos": "var(--dj-lagoon-teal)",
            "delta-pos-mark": "var(--dj-lagoon-teal-mark)",
            "delta-neg": "var(--dj-ember-copper)",
            "delta-neg-mark": "var(--dj-ember-copper-mark)",
            "new": "var(--dj-lagoon-teal)",
            "new-mark": "var(--dj-lagoon-teal-mark)",
            "renewed": "var(--dj-fern-green)",
            "renewed-mark": "var(--dj-fern-green-mark)",
            "op": "var(--dj-honey-bronze)",
            "op-mark": "var(--dj-honey-bronze-mark)",
            "re": "var(--dj-plum-violet)",
            "re-mark": "var(--dj-plum-violet)",
            "cash": "var(--dj-lagoon-teal)",
            "cash-mark": "var(--dj-lagoon-teal-mark)",
        }
        for token, value in expected.items():
            with self.subTest(token=token):
                self.assertEqual(self.tokens[token], value)

    def test_light_fills_use_carbon_ink(self):
        self.assertEqual(self.tokens["new-text"], "var(--dj-carbon)")
        self.assertEqual(self.tokens["renewed-text"], "var(--dj-carbon)")
        self.assertEqual(self.tokens["cash-text"], "var(--dj-carbon)")
        self.assertEqual(self.tokens["offplan-text"], "var(--dj-carbon)")

    def test_honey_mark_is_surface_aware(self):
        for theme in ("navy", "carbon"):
            block = re.search(
                rf"\.dj-theme-{theme}\s*\{{(.*?)\n\}}", self.css, re.DOTALL
            )
            self.assertIsNotNone(block)
            self.assertIn(
                "--accent-highlight-mark: var(--dj-honey-bronze);",
                block.group(1),
            )
        self.assertIn("var(--accent-highlight-mark)", self.renderer)

    def test_old_palette_names_are_gone(self):
        old_names = (
            "rosy-copper",
            "dark-cyan",
            "muted-teal",
            "midnight-violet",
            "Rosy Copper",
            "Dark Cyan",
            "Muted Teal",
            "Midnight Violet",
        )
        combined = self.css + self.guidance
        for name in old_names:
            with self.subTest(name=name):
                self.assertNotIn(name, combined)


if __name__ == "__main__":
    unittest.main()

