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

    def test_codesign_happens_on_a_tmp_stage_before_copying_to_output(self) -> None:
        self.assertIn("nunubar-appbuild", self.source)
        self.assertIn("COPYFILE_DISABLE=1", self.source)
        clear_at = self.source.index('xattr -cr "$app"')
        app_sign_at = self.source.index("codesign --force --sign - --requirements")
        copy_out_at = self.source.index(
            'copy_without_mac_metadata "$STAGE_APP" "$OUTPUT_APP"'
        )
        self.assertLess(clear_at, app_sign_at)
        self.assertLess(app_sign_at, copy_out_at)
        self.assertLess(
            self.source.index('codesign --verify --deep --strict "$STAGE_APP"'),
            copy_out_at,
        )


if __name__ == "__main__":
    unittest.main()
