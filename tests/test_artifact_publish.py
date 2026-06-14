import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PUBLISH_PATH = REPO_ROOT / "acervo" / "global" / "tools" / "artifact_publish.py"
INIT_PACKAGE_PATH = REPO_ROOT / "acervo" / "global" / "tools" / "harness" / "init_artifact_package.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class ArtifactPublishPolicyTest(unittest.TestCase):
    def test_resolve_drive_target_prefers_explicit_destination(self):
        mod = load_module(ARTIFACT_PUBLISH_PATH, "artifact_publish_test_explicit")
        manifest = {
            "primary_microverso": "ensino",
            "drive_target": {"folder_path": "exocortex/ensino/2026/listas"},
        }
        self.assertEqual(
            mod.resolve_drive_target(manifest, explicit_drive_path="exocortex/gabinete/2026/oficios"),
            "exocortex/gabinete/2026/oficios",
        )

    def test_resolve_drive_target_uses_manifest_before_fallback(self):
        mod = load_module(ARTIFACT_PUBLISH_PATH, "artifact_publish_test_manifest")
        manifest = {
            "primary_microverso": "ensino",
            "drive_target": {"folder_path": "exocortex/ensino/2026/listas"},
        }
        self.assertEqual(mod.resolve_drive_target(manifest), "exocortex/ensino/2026/listas")

    def test_resolve_drive_target_defaults_to_inbox_without_inference_from_filesystem_context(self):
        mod = load_module(ARTIFACT_PUBLISH_PATH, "artifact_publish_test_inbox")
        manifest = {
            "primary_microverso": "ensino",
            "title": "Lista de revisão",
        }
        self.assertEqual(mod.resolve_drive_target(manifest), "exocortex/inbox")

    def test_multiple_interdependent_files_force_publication_subfolder(self):
        mod = load_module(ARTIFACT_PUBLISH_PATH, "artifact_publish_test_group")
        items = [
            mod.UploadItem(Path("/tmp/a.pdf"), "a.pdf", "pdf", "application/pdf", "exports/a.pdf"),
            mod.UploadItem(Path("/tmp/a.zip"), "a.zip", "zip", "application/zip", "exports/a.zip"),
        ]
        manifest = {"canonical_slug": "deck-premium"}
        self.assertEqual(
            mod.resolve_publication_folder("exocortex/inbox", manifest, items),
            "exocortex/inbox/deck-premium",
        )

    def test_single_file_keeps_base_folder_without_extra_subfolder(self):
        mod = load_module(ARTIFACT_PUBLISH_PATH, "artifact_publish_test_single")
        items = [
            mod.UploadItem(Path("/tmp/a.pdf"), "a.pdf", "pdf", "application/pdf", "exports/a.pdf"),
        ]
        manifest = {"canonical_slug": "deck-premium"}
        self.assertEqual(mod.resolve_publication_folder("exocortex/inbox", manifest, items), "exocortex/inbox")

    def test_init_manifest_contains_drive_target_defaulting_to_inbox(self):
        mod = load_module(INIT_PACKAGE_PATH, "init_artifact_package_test")
        manifest = mod.build_manifest(
            artifact_id="art_20260614_120000_demo",
            title="Demo",
            task_id=None,
            primary_microverso="ensino",
            related_microversos=[],
            artifact_type="document",
            source_type="markdown",
            scope="micro",
        )
        self.assertEqual(manifest["drive_target"]["provider"], "google_drive")
        self.assertEqual(manifest["drive_target"]["folder_path"], "exocortex/inbox")
        self.assertEqual(manifest["drive_target"]["visibility"], "private")


if __name__ == "__main__":
    unittest.main()
