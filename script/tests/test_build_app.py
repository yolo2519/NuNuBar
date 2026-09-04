from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILD_APP = ROOT / "script" / "build_app.sh"


class BuildAppScriptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = BUILD_APP.read_text(encoding="utf-8")

    def test_bundle_copies_drop_mac_metadata(self) -> None:
        self.assertIn("ditto --norsrc --noextattr --noqtn --noacl", self.source)
        self.assertNotRegex(
            self.source,
            r"(?m)^\s*cp(\s+-R)?\s+",
            "build_app.sh must not copy bundle files with cp; cp preserves FinderInfo",
        )

    def test_codesign_clears_detritus_before_signing_the_app(self) -> None:
        clear_at = self.source.index("xattr -cr \"$OUTPUT_APP\"")
        app_sign_at = self.source.index("codesign --force --sign - --requirements")
        self.assertLess(clear_at, app_sign_at)


if __name__ == "__main__":
    unittest.main()
