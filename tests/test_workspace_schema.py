from __future__ import annotations

import copy
import importlib.util
import os
import sys
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO / "scripts" / "workspace_schema.py"


def _load_module():
    assert MODULE_PATH.is_file(), "workspace_schema.py ainda não existe"
    spec = importlib.util.spec_from_file_location("workspace_schema_test", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _valid_manifest() -> str:
    return """\
apiVersion: excrtx-workspace/v1
kind: Workspace
metadata:
  id: ws_example
  created_at: 2026-08-15T00:00:00Z
project:
  title: Projeto Exemplo
  objective: Resultado verificável do projeto.
  status: proposed
  status_changed_at: 2026-08-15T00:00:00Z
  status_reason: Manifesto criado.
cognitive_binding:
  primary_microverso: exocortex-ops
  related_microversos: []
"""


def _valid_manifest_data() -> dict:
    return {
        "apiVersion": "excrtx-workspace/v1",
        "kind": "Workspace",
        "metadata": {"id": "ws_example", "created_at": "2026-08-15T00:00:00Z"},
        "project": {
            "title": "Projeto Exemplo",
            "objective": "Resultado verificável.",
            "status": "proposed",
            "status_changed_at": "2026-08-15T00:00:00Z",
            "status_reason": "Manifesto criado.",
        },
        "cognitive_binding": {
            "primary_microverso": "exocortex-ops",
            "related_microversos": [],
        },
    }


def _set_nested(data: dict, dotted_path: str, value: object) -> None:
    parts = dotted_path.split(".")
    current = data
    for part in parts[:-1]:
        current = current[part]
    current[parts[-1]] = value


def _write_workspace(tmp_path: Path, text: str | None = None) -> Path:
    root = tmp_path / "workspace"
    control = root / ".exocortex"
    control.mkdir(parents=True)
    (control / "workspace.yaml").write_text(text or _valid_manifest(), encoding="utf-8")
    return root


def test_load_manifest_accepts_the_minimal_v1_contract_from_workspace_root(tmp_path: Path) -> None:
    schema = _load_module()
    root = _write_workspace(tmp_path)

    parsed = schema.load_manifest(root)

    assert parsed["apiVersion"] == "excrtx-workspace/v1"
    assert parsed["metadata"]["id"] == "ws_example"
    assert parsed["metadata"]["created_at"] == "2026-08-15T00:00:00Z"
    assert isinstance(parsed["metadata"]["created_at"], str)
    assert parsed["project"]["status"] == "proposed"


def test_load_manifest_classifies_missing_control_directory_as_missing(tmp_path: Path) -> None:
    schema = _load_module()
    root = tmp_path / "workspace"
    root.mkdir()

    with pytest.raises(schema.WorkspaceManifestError) as caught:
        schema.load_manifest(root)

    assert caught.value.code == "missing"


def test_validate_manifest_rejects_unknown_fields() -> None:
    schema = _load_module()
    manifest = _valid_manifest_data()
    manifest["commands"] = ["make deploy"]

    with pytest.raises(schema.WorkspaceManifestError) as caught:
        schema.validate_manifest(manifest)

    assert caught.value.field == "manifesto"
    assert "commands" not in str(caught.value)


def test_validate_manifest_rejects_non_string_mapping_keys() -> None:
    schema = _load_module()
    manifest = _valid_manifest_data()
    manifest["project"][1] = "valor"

    with pytest.raises(schema.WorkspaceManifestError, match="project.*chaves devem ser strings"):
        schema.validate_manifest(manifest)


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("apiVersion", "excrtx-workspace/v2", "apiVersion"),
        ("kind", "Project", "kind"),
        ("metadata.id", "ws_Invalid", "metadata.id"),
        ("metadata.created_at", "2026-08-15", "metadata.created_at"),
        ("project.title", "", "project.title"),
        ("project.objective", "", "project.objective"),
        ("project.status", "paused", "project.status"),
        ("project.status", ["proposed"], "project.status"),
        ("project.status_changed_at", "agora", "project.status_changed_at"),
        ("project.status_reason", "", "project.status_reason"),
        ("cognitive_binding.primary_microverso", "Exocortex Ops", "primary_microverso"),
        ("cognitive_binding.related_microversos", ["sales-ai", "sales-ai"], "duplicados"),
        ("cognitive_binding.related_microversos", ["exocortex-ops"], "microverso principal"),
    ],
)
def test_validate_manifest_rejects_invalid_field_values(field: str, value: object, expected: str) -> None:
    schema = _load_module()
    manifest = copy.deepcopy(_valid_manifest_data())
    _set_nested(manifest, field, value)

    with pytest.raises(schema.WorkspaceManifestError, match=expected):
        schema.validate_manifest(manifest)


def test_validate_manifest_accepts_the_complete_v1_shape() -> None:
    schema = _load_module()
    manifest = _valid_manifest_data()

    assert schema.validate_manifest(manifest) == manifest


@pytest.mark.parametrize(
    ("field", "maximum"),
    [
        ("project.title", 200),
        ("project.objective", 2_000),
        ("project.status_reason", 500),
    ],
)
def test_validate_manifest_enforces_text_boundaries(field: str, maximum: int) -> None:
    schema = _load_module()
    accepted = copy.deepcopy(_valid_manifest_data())
    _set_nested(accepted, field, "x" * maximum)
    assert schema.validate_manifest(accepted) == accepted

    rejected = copy.deepcopy(_valid_manifest_data())
    _set_nested(rejected, field, "x" * (maximum + 1))
    with pytest.raises(schema.WorkspaceManifestError, match=field):
        schema.validate_manifest(rejected)


def test_validate_manifest_enforces_workspace_id_and_slug_boundaries() -> None:
    schema = _load_module()
    accepted = copy.deepcopy(_valid_manifest_data())
    accepted["metadata"]["id"] = "ws_" + "a" * 60
    accepted["cognitive_binding"]["primary_microverso"] = "a" * 60
    assert schema.validate_manifest(accepted) == accepted

    too_long_id = copy.deepcopy(accepted)
    too_long_id["metadata"]["id"] = "ws_" + "a" * 61
    with pytest.raises(schema.WorkspaceManifestError, match="metadata.id"):
        schema.validate_manifest(too_long_id)

    too_long_slug = copy.deepcopy(accepted)
    too_long_slug["cognitive_binding"]["primary_microverso"] = "a" * 61
    with pytest.raises(schema.WorkspaceManifestError, match="primary_microverso"):
        schema.validate_manifest(too_long_slug)


def test_load_manifest_rejects_unknown_nested_fields(tmp_path: Path) -> None:
    schema = _load_module()
    text = _valid_manifest().replace("  status: proposed\n", "  status: proposed\n  command: deploy\n")
    root = _write_workspace(tmp_path, text)

    with pytest.raises(schema.WorkspaceManifestError) as caught:
        schema.load_manifest(root)

    assert caught.value.field == "project"
    assert "command" not in str(caught.value)


def test_load_manifest_rejects_duplicate_yaml_keys(tmp_path: Path) -> None:
    schema = _load_module()
    text = _valid_manifest().replace(
        "  title: Projeto Exemplo\n",
        "  title: Projeto Exemplo\n  title: Outro título\n",
    )
    root = _write_workspace(tmp_path, text)

    with pytest.raises(schema.WorkspaceManifestError, match="manifesto inválido") as caught:
        schema.load_manifest(root)

    assert caught.value.code == "invalid-manifest"
    assert "title" not in str(caught.value)


@pytest.mark.parametrize(
    "fragment",
    [
        "  title: &titulo Projeto Exemplo\n",
        "  title: *titulo\n",
        "  <<: {title: Projeto Exemplo}\n",
    ],
)
def test_load_manifest_rejects_yaml_composition(tmp_path: Path, fragment: str) -> None:
    schema = _load_module()
    text = _valid_manifest().replace("  title: Projeto Exemplo\n", fragment)
    root = _write_workspace(tmp_path, text)

    with pytest.raises(schema.WorkspaceManifestError, match="anchor|alias|manifesto inválido"):
        schema.load_manifest(root)


def test_load_manifest_rejects_unsafe_python_tag(tmp_path: Path) -> None:
    schema = _load_module()
    text = _valid_manifest().replace("  title: Projeto Exemplo\n", "  title: !!python/object:builtins.str {}\n")
    root = _write_workspace(tmp_path, text)

    with pytest.raises(schema.WorkspaceManifestError, match="manifesto inválido"):
        schema.load_manifest(root)


def test_load_manifest_wraps_non_scalar_yaml_keys(tmp_path: Path) -> None:
    schema = _load_module()
    root = _write_workspace(tmp_path, "? [a, b]\n: value\n")

    with pytest.raises(schema.WorkspaceManifestError, match="manifesto inválido"):
        schema.load_manifest(root)


def test_load_manifest_uses_yaml_1_2_boolean_semantics(tmp_path: Path) -> None:
    schema = _load_module()
    text = _valid_manifest().replace("  title: Projeto Exemplo\n", "  title: yes\n")
    root = _write_workspace(tmp_path, text)

    assert schema.load_manifest(root)["project"]["title"] == "yes"


@pytest.mark.parametrize("surface", ["unknown", "duplicate", "syntax"])
def test_load_manifest_never_echoes_secret_shaped_yaml_in_errors(
    tmp_path: Path,
    surface: str,
) -> None:
    schema = _load_module()
    secret = "ghp_" + "z" * 36
    if surface == "unknown":
        text = _valid_manifest() + f"{secret}: value\n"
    elif surface == "duplicate":
        text = _valid_manifest().replace(
            "  title: Projeto Exemplo\n",
            f"  {secret}: one\n  {secret}: two\n",
        )
    else:
        text = _valid_manifest() + f"broken: [{secret}\n"
    root = _write_workspace(tmp_path, text)

    with pytest.raises(schema.WorkspaceManifestError) as caught:
        schema.load_manifest(root)

    assert secret not in str(caught.value)


def test_load_manifest_rejects_oversized_yaml_before_parsing(tmp_path: Path) -> None:
    schema = _load_module()
    root = _write_workspace(
        tmp_path,
        _valid_manifest() + "#" + "x" * schema.MAX_MANIFEST_BYTES,
    )

    with pytest.raises(schema.WorkspaceManifestError) as caught:
        schema.load_manifest(root)

    assert caught.value.code == "manifest-too-large"


def test_dump_manifest_refuses_to_generate_an_oversized_manifest() -> None:
    schema = _load_module()
    manifest = _valid_manifest_data()
    manifest["cognitive_binding"]["related_microversos"] = [
        f"micro-{index:05d}" for index in range(7_000)
    ]

    with pytest.raises(schema.WorkspaceManifestError) as caught:
        schema.dump_manifest(manifest)

    assert caught.value.code == "manifest-too-large"


def test_dump_manifest_rejects_str_subclass_without_raw_representer_error() -> None:
    schema = _load_module()

    class UserString(str):
        pass

    manifest = _valid_manifest_data()
    manifest["project"]["title"] = UserString("titulo-controlado")

    with pytest.raises(schema.WorkspaceManifestError) as caught:
        schema.dump_manifest(manifest)

    assert "titulo-controlado" not in str(caught.value)
    assert caught.value.__cause__ is None
    assert caught.value.__context__ is None


def test_write_manifest_atomic_rejects_str_subclass_without_raw_error(
    tmp_path: Path,
) -> None:
    schema = _load_module()
    root = tmp_path / "workspace"
    root.mkdir()

    class UserString(str):
        pass

    manifest = _valid_manifest_data()
    manifest["project"]["title"] = UserString("titulo-controlado")

    with pytest.raises(schema.WorkspaceManifestError) as caught:
        schema.write_manifest_atomic(root, manifest)

    assert "titulo-controlado" not in str(caught.value)
    assert not (root / ".exocortex" / "workspace.yaml").exists()


def test_load_manifest_rejects_excessive_yaml_depth_without_recursion_error(
    tmp_path: Path,
) -> None:
    schema = _load_module()
    nested = "leaf: value"
    for _ in range(schema.MAX_YAML_DEPTH + 2):
        nested = f"node: {{{nested}}}"
    root = _write_workspace(tmp_path, nested + "\n")

    with pytest.raises(schema.WorkspaceManifestError) as caught:
        schema.load_manifest(root)

    assert caught.value.code == "manifest-too-complex"


@pytest.mark.parametrize("path", ["bad\x00path", "~exocortex-user-that-does-not-exist"])
def test_resolve_workspace_root_wraps_malformed_paths(path: str) -> None:
    schema = _load_module()

    with pytest.raises(schema.WorkspaceManifestError) as caught:
        schema.resolve_workspace_root(path)

    assert caught.value.code == "invalid-workspace-root"


def test_resolve_workspace_root_wraps_symlink_loop(tmp_path: Path) -> None:
    schema = _load_module()
    left = tmp_path / "left"
    right = tmp_path / "right"
    left.symlink_to(right)
    right.symlink_to(left)

    with pytest.raises(schema.WorkspaceManifestError):
        schema.resolve_workspace_root(left)


def test_load_manifest_wraps_stat_permission_error(tmp_path: Path, monkeypatch) -> None:
    schema = _load_module()
    root = _write_workspace(tmp_path)
    real_stat = schema.os.stat

    def fail_manifest_stat(path, *args, **kwargs):
        if path == "workspace.yaml" and kwargs.get("dir_fd") is not None:
            raise PermissionError("secret-shaped-os-payload")
        return real_stat(path, *args, **kwargs)

    monkeypatch.setattr(schema.os, "stat", fail_manifest_stat)

    with pytest.raises(schema.WorkspaceManifestError) as caught:
        schema.load_manifest(root)

    assert caught.value.code == "invalid-manifest"
    assert "secret-shaped-os-payload" not in str(caught.value)


def test_open_control_closes_descriptor_when_fstat_fails(tmp_path: Path, monkeypatch) -> None:
    schema = _load_module()
    root = _write_workspace(tmp_path)
    real_fstat = schema.os.fstat
    calls = 0
    opened_control: list[int] = []
    real_open = schema.os.open

    def capture_open(path, *args, **kwargs):
        descriptor = real_open(path, *args, **kwargs)
        if path == ".exocortex":
            opened_control.append(descriptor)
        return descriptor

    def fail_control_fstat(descriptor: int):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("fstat injected payload")
        return real_fstat(descriptor)

    monkeypatch.setattr(schema.os, "open", capture_open)
    monkeypatch.setattr(schema.os, "fstat", fail_control_fstat)

    with pytest.raises(schema.WorkspaceManifestError):
        schema.load_manifest(root)

    assert opened_control
    with pytest.raises(OSError):
        os.fstat(opened_control[0])


@pytest.mark.parametrize(
    ("field", "secret"),
    [
        ("project.title", "sk-" + "a" * 30),
        ("project.title", "ghp_" + "a" * 36),
        ("project.objective", "AKIA" + "A" * 16),
        ("project.objective", "xoxb-" + "a" * 20),
        ("project.objective", "-----BEGIN PRIVATE KEY-----"),
        ("project.status_reason", "12345678:" + "a" * 35),
    ],
)
def test_validate_manifest_rejects_secret_literals(field: str, secret: str) -> None:
    schema = _load_module()
    manifest = copy.deepcopy(_valid_manifest_data())
    _set_nested(manifest, field, secret)

    with pytest.raises(schema.WorkspaceManifestError, match="secret detectado"):
        schema.validate_manifest(manifest)


def test_validate_manifest_allows_secret_variable_names() -> None:
    schema = _load_module()
    manifest = _valid_manifest_data()
    manifest["project"]["objective"] = "Usar OPENAI_API_KEY no runtime, sem gravar o valor."

    assert schema.validate_manifest(manifest) == manifest


@pytest.mark.parametrize(
    ("field", "secret"),
    [
        ("metadata.id", "ws_sk-" + "a" * 30),
        ("cognitive_binding.primary_microverso", "sk-" + "a" * 30),
    ],
)
def test_validate_manifest_rejects_secret_literals_in_binding_fields(
    field: str,
    secret: str,
) -> None:
    schema = _load_module()
    manifest = copy.deepcopy(_valid_manifest_data())
    _set_nested(manifest, field, secret)

    with pytest.raises(schema.WorkspaceManifestError, match="secret detectado"):
        schema.validate_manifest(manifest)


def test_validate_manifest_rejects_secret_literals_in_related_microversos() -> None:
    schema = _load_module()
    manifest = copy.deepcopy(_valid_manifest_data())
    manifest["cognitive_binding"]["related_microversos"] = ["xoxb-" + "a" * 20]

    with pytest.raises(schema.WorkspaceManifestError, match="secret detectado"):
        schema.validate_manifest(manifest)


def test_load_manifest_invalid_yaml_does_not_chain_user_content(tmp_path: Path) -> None:
    schema = _load_module()
    text = _valid_manifest() + "broken: [USER-CONTENT-XYZ\n"
    root = _write_workspace(tmp_path, text)

    with pytest.raises(schema.WorkspaceManifestError) as caught:
        schema.load_manifest(root)

    assert caught.value.__cause__ is None
    assert caught.value.__context__ is None
    assert "USER-CONTENT-XYZ" not in str(caught.value)


def test_validate_manifest_invalid_timestamp_does_not_chain_user_content() -> None:
    schema = _load_module()
    manifest = _valid_manifest_data()
    manifest["metadata"]["created_at"] = "2026-13-45T99:99:99Z"

    with pytest.raises(schema.WorkspaceManifestError) as caught:
        schema.validate_manifest(manifest)

    assert caught.value.__cause__ is None
    assert caught.value.__context__ is None
    assert "2026-13-45" not in str(caught.value)


def test_load_manifest_rejects_symlinked_control_directory(tmp_path: Path) -> None:
    schema = _load_module()
    workspace = tmp_path / "workspace"
    outside = tmp_path / "outside"
    workspace.mkdir()
    outside.mkdir()
    (outside / "workspace.yaml").write_text(_valid_manifest(), encoding="utf-8")
    (workspace / ".exocortex").symlink_to(outside, target_is_directory=True)

    with pytest.raises(schema.WorkspaceManifestError, match=".exocortex.*symlink"):
        schema.load_manifest(workspace)


def test_load_manifest_rejects_symlinked_manifest(tmp_path: Path) -> None:
    schema = _load_module()
    workspace = tmp_path / "workspace"
    control = workspace / ".exocortex"
    outside = tmp_path / "outside.yaml"
    control.mkdir(parents=True)
    outside.write_text(_valid_manifest(), encoding="utf-8")
    (control / "workspace.yaml").symlink_to(outside)

    with pytest.raises(schema.WorkspaceManifestError, match="workspace.yaml.*symlink"):
        schema.load_manifest(workspace)


def test_resolve_workspace_root_accepts_user_symlink_and_relative_path(tmp_path: Path) -> None:
    schema = _load_module()
    real = tmp_path / "real"
    alias = tmp_path / "alias"
    real.mkdir()
    alias.symlink_to(real, target_is_directory=True)

    assert schema.resolve_workspace_root("alias", cwd=tmp_path) == real.resolve()


def test_resolve_workspace_root_wraps_final_directory_stat_error(
    tmp_path: Path,
    monkeypatch,
) -> None:
    schema = _load_module()
    root = tmp_path / "workspace"
    root.mkdir()
    canonical = root.resolve()
    real_stat = Path.stat

    def fail_final_stat(self: Path, *args, **kwargs):
        if self == canonical:
            raise PermissionError("INJECT_PATH_STAT")
        return real_stat(self, *args, **kwargs)

    monkeypatch.setattr(Path, "stat", fail_final_stat)

    with pytest.raises(schema.WorkspaceManifestError) as caught:
        schema.resolve_workspace_root(root)

    assert caught.value.code == "invalid-workspace-root"
    assert "INJECT_PATH_STAT" not in str(caught.value)
    assert caught.value.__cause__ is None
    assert caught.value.__context__ is None
    assert getattr(caught.value, "__notes__", []) == []


def test_load_manifest_fails_closed_without_required_posix_flags(
    tmp_path: Path,
    monkeypatch,
) -> None:
    schema = _load_module()
    root = _write_workspace(tmp_path)
    monkeypatch.delattr(schema.os, "O_NOFOLLOW")

    with pytest.raises(schema.WorkspaceManifestError) as caught:
        schema.load_manifest(root)

    assert caught.value.code == "unsupported-platform"


def test_load_manifest_rejects_root_swapped_to_symlink_after_resolution(
    tmp_path: Path,
    monkeypatch,
) -> None:
    schema = _load_module()
    root = _write_workspace(tmp_path)
    original = tmp_path / "workspace-original"
    victim = tmp_path / "victim"
    victim_control = victim / ".exocortex"
    victim_control.mkdir(parents=True)
    (victim_control / "workspace.yaml").write_text(_valid_manifest(), encoding="utf-8")
    real_resolve = schema.resolve_workspace_root

    def resolve_then_swap(*args, **kwargs):
        resolved = real_resolve(*args, **kwargs)
        root.rename(original)
        root.symlink_to(victim, target_is_directory=True)
        return resolved

    monkeypatch.setattr(schema, "resolve_workspace_root", resolve_then_swap)

    with pytest.raises(schema.WorkspaceManifestError, match="workspace.*symlink"):
        schema.load_manifest(root)


def test_write_manifest_rejects_root_swapped_to_symlink_after_resolution(
    tmp_path: Path,
    monkeypatch,
) -> None:
    schema = _load_module()
    root = _write_workspace(tmp_path)
    original = tmp_path / "workspace-original"
    victim = tmp_path / "victim"
    victim_control = victim / ".exocortex"
    victim_control.mkdir(parents=True)
    victim_manifest = victim_control / "workspace.yaml"
    victim_manifest.write_text("preservar\n", encoding="utf-8")
    real_resolve = schema.resolve_workspace_root

    def resolve_then_swap(*args, **kwargs):
        resolved = real_resolve(*args, **kwargs)
        root.rename(original)
        root.symlink_to(victim, target_is_directory=True)
        return resolved

    monkeypatch.setattr(schema, "resolve_workspace_root", resolve_then_swap)

    with pytest.raises(schema.WorkspaceManifestError, match="workspace.*symlink"):
        schema.write_manifest_atomic(root, _valid_manifest_data())

    assert victim_manifest.read_text(encoding="utf-8") == "preservar\n"


def test_write_manifest_rejects_intermediate_component_swapped_to_symlink(
    tmp_path: Path,
    monkeypatch,
) -> None:
    schema = _load_module()
    parent = tmp_path / "projects"
    root = parent / "workspace"
    control = root / ".exocortex"
    control.mkdir(parents=True)
    (control / "workspace.yaml").write_text(_valid_manifest(), encoding="utf-8")
    original_parent = tmp_path / "projects-original"
    victim_parent = tmp_path / "victim-projects"
    victim_root = victim_parent / "workspace"
    victim_control = victim_root / ".exocortex"
    victim_control.mkdir(parents=True)
    victim_manifest = victim_control / "workspace.yaml"
    victim_manifest.write_text("preservar\n", encoding="utf-8")
    real_resolve = schema.resolve_workspace_root

    def resolve_then_swap(*args, **kwargs):
        resolved = real_resolve(*args, **kwargs)
        parent.rename(original_parent)
        parent.symlink_to(victim_parent, target_is_directory=True)
        return resolved

    monkeypatch.setattr(schema, "resolve_workspace_root", resolve_then_swap)

    with pytest.raises(schema.WorkspaceManifestError, match="workspace.*symlink"):
        schema.write_manifest_atomic(root, _valid_manifest_data())

    assert victim_manifest.read_text(encoding="utf-8") == "preservar\n"


def test_load_manifest_detects_root_swap_after_descriptors_are_open(
    tmp_path: Path,
    monkeypatch,
) -> None:
    schema = _load_module()
    root = _write_workspace(tmp_path)
    original = tmp_path / "workspace-original"
    victim = tmp_path / "victim"
    victim_control = victim / ".exocortex"
    victim_control.mkdir(parents=True)
    (victim_control / "workspace.yaml").write_text(_valid_manifest(), encoding="utf-8")
    real_open_control = schema._open_control_directory

    def open_then_swap(*args, **kwargs):
        descriptor = real_open_control(*args, **kwargs)
        root.rename(original)
        root.symlink_to(victim, target_is_directory=True)
        return descriptor

    monkeypatch.setattr(schema, "_open_control_directory", open_then_swap)

    with pytest.raises(schema.WorkspaceManifestError, match="workspace.*mudou"):
        schema.load_manifest(root)


def test_write_manifest_detects_root_swap_after_descriptors_are_open(
    tmp_path: Path,
    monkeypatch,
) -> None:
    schema = _load_module()
    root = _write_workspace(tmp_path)
    original = tmp_path / "workspace-original"
    victim = tmp_path / "victim"
    victim_control = victim / ".exocortex"
    victim_control.mkdir(parents=True)
    victim_manifest = victim_control / "workspace.yaml"
    victim_manifest.write_text("preservar\n", encoding="utf-8")
    real_open_control = schema._open_control_directory

    def open_then_swap(*args, **kwargs):
        descriptor = real_open_control(*args, **kwargs)
        root.rename(original)
        root.symlink_to(victim, target_is_directory=True)
        return descriptor

    monkeypatch.setattr(schema, "_open_control_directory", open_then_swap)

    with pytest.raises(schema.WorkspaceManifestError, match="workspace.*mudou"):
        schema.write_manifest_atomic(root, _valid_manifest_data())

    assert victim_manifest.read_text(encoding="utf-8") == "preservar\n"


def test_write_manifest_atomic_round_trips_and_leaves_no_temp(tmp_path: Path) -> None:
    schema = _load_module()
    root = tmp_path / "workspace"
    root.mkdir()

    manifest_path = schema.write_manifest_atomic(root, _valid_manifest_data())

    assert manifest_path == root.resolve() / ".exocortex" / "workspace.yaml"
    assert schema.load_manifest(root) == _valid_manifest_data()
    assert stat_mode(manifest_path) == 0o600
    assert list(manifest_path.parent.glob(".workspace.yaml.tmp.*")) == []


def test_write_manifest_atomic_preserves_old_bytes_when_replace_fails(tmp_path: Path, monkeypatch) -> None:
    schema = _load_module()
    root = _write_workspace(tmp_path)
    manifest_path = root / ".exocortex" / "workspace.yaml"
    old_bytes = manifest_path.read_bytes()
    updated = copy.deepcopy(_valid_manifest_data())
    updated["project"]["title"] = "Título atualizado"

    def fail_replace(*args, **kwargs):
        raise OSError("falha injetada")

    monkeypatch.setattr(schema.os, "replace", fail_replace)

    with pytest.raises(schema.WorkspaceManifestError, match="escrita atômica"):
        schema.write_manifest_atomic(root, updated)

    assert manifest_path.read_bytes() == old_bytes
    assert list(manifest_path.parent.glob(".workspace.yaml.tmp.*")) == []


def test_write_manifest_reports_partial_failure_after_replace_if_directory_fsync_fails(
    tmp_path: Path,
    monkeypatch,
) -> None:
    schema = _load_module()
    root = _write_workspace(tmp_path)
    updated = copy.deepcopy(_valid_manifest_data())
    updated["project"]["title"] = "Título já publicado"
    real_fsync = schema.os.fsync
    calls = 0

    def fail_second_fsync(descriptor: int) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("fsync do diretório falhou")
        real_fsync(descriptor)

    monkeypatch.setattr(schema.os, "fsync", fail_second_fsync)

    with pytest.raises(schema.WorkspaceManifestError) as caught:
        schema.write_manifest_atomic(root, updated)

    assert caught.value.code == "partial-failure"
    assert "publicado" in str(caught.value)
    assert schema.load_manifest(root)["project"]["title"] == "Título já publicado"
    assert list((root / ".exocortex").glob(".workspace.yaml.tmp.*")) == []


def test_write_manifest_cleanup_preserves_primary_error_and_closes_control_descriptor(
    tmp_path: Path,
    monkeypatch,
) -> None:
    schema = _load_module()
    root = _write_workspace(tmp_path)
    opened: list[int] = []
    real_open_control = schema._open_control_directory

    def capture_control_descriptor(*args, **kwargs):
        descriptor = real_open_control(*args, **kwargs)
        opened.append(descriptor)
        return descriptor

    def fail_replace(*args, **kwargs):
        raise OSError("erro primário do replace")

    def fail_unlink(*args, **kwargs):
        raise OSError("erro secundário do cleanup")

    monkeypatch.setattr(schema, "_open_control_directory", capture_control_descriptor)
    monkeypatch.setattr(schema.os, "replace", fail_replace)
    monkeypatch.setattr(schema.os, "unlink", fail_unlink)

    with pytest.raises(schema.WorkspaceManifestError) as caught:
        schema.write_manifest_atomic(root, _valid_manifest_data())

    assert opened
    with pytest.raises(OSError):
        os.fstat(opened[0])
    assert "erro primário do replace" not in str(caught.value)
    notes = getattr(caught.value, "__notes__", [])
    assert notes
    assert all("erro secundário do cleanup" not in note for note in notes)


def test_write_manifest_reports_partial_failure_if_descriptor_close_fails_after_publish(
    tmp_path: Path,
    monkeypatch,
) -> None:
    schema = _load_module()
    root = tmp_path / "workspace"
    root.mkdir()
    control_fd: int | None = None
    real_open_descriptors = schema._open_workspace_descriptors
    real_close = schema.os.close

    def capture_descriptors(*args, **kwargs):
        nonlocal control_fd
        opened = real_open_descriptors(*args, **kwargs)
        control_fd = opened[1]
        return opened

    def fail_control_close(fd: int):
        if fd == control_fd:
            raise OSError("fechamento injetado do .exocortex")
        real_close(fd)

    monkeypatch.setattr(schema, "_open_workspace_descriptors", capture_descriptors)
    monkeypatch.setattr(schema.os, "close", fail_control_close)

    with pytest.raises(schema.WorkspaceManifestError) as caught:
        schema.write_manifest_atomic(root, _valid_manifest_data())

    assert caught.value.code == "partial-failure"
    assert (root / ".exocortex" / "workspace.yaml").exists()


def test_write_manifest_fsyncs_root_when_control_directory_is_created(
    tmp_path: Path,
    monkeypatch,
) -> None:
    schema = _load_module()
    root = tmp_path / "workspace"
    root.mkdir()
    real_fsync = schema.os.fsync
    calls: list[int] = []

    def capture_fsync(descriptor: int) -> None:
        calls.append(descriptor)
        real_fsync(descriptor)

    monkeypatch.setattr(schema.os, "fsync", capture_fsync)

    schema.write_manifest_atomic(root, _valid_manifest_data())

    assert len(calls) == 3


def test_write_manifest_reports_partial_failure_if_root_fsync_fails(
    tmp_path: Path,
    monkeypatch,
) -> None:
    schema = _load_module()
    root = tmp_path / "workspace"
    root.mkdir()

    def fail_root_fsync(descriptor: int) -> None:
        raise OSError("secret-shaped-fsync-payload")

    monkeypatch.setattr(schema.os, "fsync", fail_root_fsync)

    with pytest.raises(schema.WorkspaceManifestError) as caught:
        schema.write_manifest_atomic(root, _valid_manifest_data())

    assert caught.value.code == "partial-failure"
    assert "secret-shaped-fsync-payload" not in str(caught.value)
    assert (root / ".exocortex").is_dir()
    assert not (root / ".exocortex" / "workspace.yaml").exists()


def test_write_manifest_atomic_runs_secret_gate_before_writing(tmp_path: Path) -> None:
    schema = _load_module()
    root = _write_workspace(tmp_path)
    manifest_path = root / ".exocortex" / "workspace.yaml"
    old_bytes = manifest_path.read_bytes()
    updated = copy.deepcopy(_valid_manifest_data())
    updated["project"]["objective"] = "sk-" + "a" * 30

    with pytest.raises(schema.WorkspaceManifestError, match="secret detectado"):
        schema.write_manifest_atomic(root, updated)

    assert manifest_path.read_bytes() == old_bytes
    assert list(manifest_path.parent.glob(".workspace.yaml.tmp.*")) == []


def test_write_manifest_atomic_rejects_symlinked_target_without_touching_it(tmp_path: Path) -> None:
    schema = _load_module()
    root = _write_workspace(tmp_path)
    manifest_path = root / ".exocortex" / "workspace.yaml"
    outside = tmp_path / "outside.yaml"
    outside.write_text("preservar\n", encoding="utf-8")
    manifest_path.unlink()
    manifest_path.symlink_to(outside)

    with pytest.raises(schema.WorkspaceManifestError, match="workspace.yaml.*symlink"):
        schema.write_manifest_atomic(root, _valid_manifest_data())

    assert outside.read_text(encoding="utf-8") == "preservar\n"
    assert manifest_path.is_symlink()
    assert list(manifest_path.parent.glob(".workspace.yaml.tmp.*")) == []


def stat_mode(path: Path) -> int:
    return os.stat(path, follow_symlinks=False).st_mode & 0o777
