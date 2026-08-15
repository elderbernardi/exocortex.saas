#!/usr/bin/env python3
"""Schema e I/O seguro do manifesto ``excrtx-workspace/v1``."""

from __future__ import annotations

import errno
import os
import re
import secrets
import stat
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from yaml.tokens import (
    AliasToken,
    AnchorToken,
    BlockEndToken,
    BlockMappingStartToken,
    BlockSequenceStartToken,
    FlowMappingEndToken,
    FlowMappingStartToken,
    FlowSequenceEndToken,
    FlowSequenceStartToken,
)


MANIFEST_RELATIVE_PATH = Path(".exocortex/workspace.yaml")
MAX_MANIFEST_BYTES = 64 * 1024
MAX_YAML_DEPTH = 32
_SECURE_DIR_FD_SUPPORTED = all(
    function in getattr(os, "supports_dir_fd", set())
    for function in (os.open, os.stat, os.mkdir, os.unlink, os.rename)
)
_SECURE_NOFOLLOW_STAT_SUPPORTED = os.stat in getattr(
    os,
    "supports_follow_symlinks",
    set(),
)
_API_VERSION = "excrtx-workspace/v1"
_KIND = "Workspace"
_ID_RE = re.compile(r"^ws_[a-z0-9][a-z0-9-]{2,59}$")
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{2,59}$")
_TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
_STATUSES = frozenset({"proposed", "active", "archived"})
_SECRET_PATTERNS = (
    ("OpenAI-style API key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("GitHub token", re.compile(r"ghp_[A-Za-z0-9]{30,}")),
    ("AWS access key ID", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Slack token", re.compile(r"xox[bpars]-[A-Za-z0-9-]{10,}")),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("Telegram bot token", re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")),
)


class WorkspaceManifestError(ValueError):
    """Erro determinístico no contrato ou no I/O seguro do manifesto."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "invalid-manifest",
        field: str | None = None,
        path: Path | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.field = field
        self.path = path


class _WorkspaceLoader(yaml.SafeLoader):
    """SafeLoader estrito que preserva timestamps como strings."""


_WorkspaceLoader.yaml_implicit_resolvers = {
    key: [
        (tag, expression)
        for tag, expression in resolvers
        if tag not in {"tag:yaml.org,2002:timestamp", "tag:yaml.org,2002:bool"}
    ]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
_WorkspaceLoader.add_implicit_resolver(
    "tag:yaml.org,2002:bool",
    re.compile(r"^(?:true|True|TRUE|false|False|FALSE)$"),
    list("tTfF"),
)


def _construct_unique_mapping(
    loader: _WorkspaceLoader,
    node: yaml.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        if key_node.tag == "tag:yaml.org,2002:merge":
            raise yaml.constructor.ConstructorError(
                "ao construir mapa",
                node.start_mark,
                "merge key YAML não permitida",
                key_node.start_mark,
            )
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise yaml.constructor.ConstructorError(
                "ao construir mapa",
                node.start_mark,
                "chave YAML deve ser string",
                key_node.start_mark,
            )
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "ao construir mapa",
                node.start_mark,
                "chave YAML duplicada não permitida",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_WorkspaceLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def _assert_keys(
    mapping: object,
    *,
    allowed: set[str],
    required: set[str],
    location: str,
) -> dict[str, Any]:
    if not isinstance(mapping, dict):
        raise WorkspaceManifestError(f"{location} deve ser um mapa YAML", field=location)
    if not all(isinstance(key, str) for key in mapping):
        raise WorkspaceManifestError(
            f"{location}: chaves devem ser strings",
            field=location,
        )
    unknown = sorted(set(mapping) - allowed)
    if unknown:
        raise WorkspaceManifestError(
            f"{location}: campos desconhecidos não permitidos",
            field=location,
        )
    missing = sorted(required - set(mapping))
    if missing:
        raise WorkspaceManifestError(
            f"{location}: campos obrigatórios ausentes",
            field=location,
        )
    return mapping


def _assert_string(value: object, *, location: str, maximum: int) -> str:
    if type(value) is not str or not value.strip():
        raise WorkspaceManifestError(
            f"{location} deve ser string não vazia",
            field=location,
        )
    if len(value) > maximum:
        raise WorkspaceManifestError(
            f"{location} excede {maximum} caracteres",
            field=location,
        )
    return value


def _assert_timestamp(value: object, *, location: str) -> str:
    if not isinstance(value, str) or not _TIMESTAMP_RE.fullmatch(value):
        raise WorkspaceManifestError(
            f"{location} deve ser timestamp UTC ISO 8601 terminado em Z",
            field=location,
        )
    timestamp_failed = False
    try:
        datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError:
        timestamp_failed = True
    if timestamp_failed:
        raise WorkspaceManifestError(
            f"{location} contém timestamp inválido",
            field=location,
        )
    return value


def _assert_no_secret(value: str, *, location: str) -> None:
    for label, pattern in _SECRET_PATTERNS:
        if pattern.search(value):
            raise WorkspaceManifestError(
                f"{location}: secret detectado ({label})",
                code="secret-detected",
                field=location,
            )


def validate_manifest(data: object) -> dict[str, Any]:
    """Valida o contrato V1 sem normalizar ou executar conteúdo."""

    manifest = _assert_keys(
        data,
        allowed={"apiVersion", "kind", "metadata", "project", "cognitive_binding"},
        required={"apiVersion", "kind", "metadata", "project", "cognitive_binding"},
        location="manifesto",
    )
    if manifest["apiVersion"] != _API_VERSION:
        raise WorkspaceManifestError(f"apiVersion deve ser {_API_VERSION}", field="apiVersion")
    if manifest["kind"] != _KIND:
        raise WorkspaceManifestError(f"kind deve ser {_KIND}", field="kind")

    metadata = _assert_keys(
        manifest["metadata"],
        allowed={"id", "created_at"},
        required={"id", "created_at"},
        location="metadata",
    )
    workspace_id = metadata["id"]
    if type(workspace_id) is not str or not _ID_RE.fullmatch(workspace_id):
        raise WorkspaceManifestError(
            "metadata.id não segue ^ws_[a-z0-9][a-z0-9-]{2,59}$",
            field="metadata.id",
        )
    _assert_no_secret(workspace_id, location="metadata.id")
    _assert_timestamp(metadata["created_at"], location="metadata.created_at")

    project = _assert_keys(
        manifest["project"],
        allowed={"title", "objective", "status", "status_changed_at", "status_reason"},
        required={"title", "objective", "status", "status_changed_at", "status_reason"},
        location="project",
    )
    title = _assert_string(project["title"], location="project.title", maximum=200)
    objective = _assert_string(
        project["objective"],
        location="project.objective",
        maximum=2_000,
    )
    status_value = project["status"]
    if not isinstance(status_value, str) or status_value not in _STATUSES:
        raise WorkspaceManifestError(
            f"project.status deve ser um de {sorted(_STATUSES)}",
            field="project.status",
        )
    _assert_timestamp(
        project["status_changed_at"],
        location="project.status_changed_at",
    )
    status_reason = _assert_string(
        project["status_reason"],
        location="project.status_reason",
        maximum=500,
    )
    _assert_no_secret(title, location="project.title")
    _assert_no_secret(objective, location="project.objective")
    _assert_no_secret(status_reason, location="project.status_reason")

    binding = _assert_keys(
        manifest["cognitive_binding"],
        allowed={"primary_microverso", "related_microversos"},
        required={"primary_microverso"},
        location="cognitive_binding",
    )
    primary = binding["primary_microverso"]
    if type(primary) is not str or not _SLUG_RE.fullmatch(primary):
        raise WorkspaceManifestError(
            "cognitive_binding.primary_microverso não é slug válido",
            field="cognitive_binding.primary_microverso",
        )
    _assert_no_secret(primary, location="cognitive_binding.primary_microverso")
    related = binding.get("related_microversos", [])
    if not isinstance(related, list) or not all(
        type(item) is str and _SLUG_RE.fullmatch(item)
        for item in related
    ):
        raise WorkspaceManifestError(
            "cognitive_binding.related_microversos deve conter apenas slugs válidos",
            field="cognitive_binding.related_microversos",
        )
    for item in related:
        _assert_no_secret(item, location="cognitive_binding.related_microversos")
    if len(set(related)) != len(related):
        raise WorkspaceManifestError(
            "cognitive_binding.related_microversos contém duplicados",
            field="cognitive_binding.related_microversos",
        )
    if primary in related:
        raise WorkspaceManifestError(
            "cognitive_binding.related_microversos repete o microverso principal",
            field="cognitive_binding.related_microversos",
        )

    return manifest


def resolve_workspace_root(
    path: str | Path,
    *,
    cwd: str | Path | None = None,
) -> Path:
    """Retorna o root real absoluto de um workspace existente."""

    try:
        candidate = Path(path).expanduser()
        if not candidate.is_absolute():
            base = Path(cwd).expanduser() if cwd is not None else Path.cwd()
            candidate = base / candidate
        root = candidate.resolve(strict=True)
    except FileNotFoundError as exc:
        raise WorkspaceManifestError(
            "workspace indisponível",
            code="missing",
            path=locals().get("candidate"),
        ) from exc
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        raise WorkspaceManifestError(
            "path do workspace é inválido ou inseguro",
            code="invalid-workspace-root",
            path=locals().get("candidate"),
        ) from exc
    stat_failed = False
    try:
        is_directory = root.is_dir()
    except OSError:
        stat_failed = True
        is_directory = False
    if stat_failed:
        raise WorkspaceManifestError(
            "workspace não pôde ser verificado como diretório",
            code="invalid-workspace-root",
            path=root,
        )
    if not is_directory:
        raise WorkspaceManifestError(
            "workspace deve ser um diretório",
            code="invalid-workspace-root",
            path=root,
        )
    return root


def _parse_manifest_text(text: str, *, path: Path | None = None) -> dict[str, Any]:
    try:
        encoded_size = len(text.encode("utf-8"))
    except UnicodeError as exc:
        raise WorkspaceManifestError(
            "manifesto não está em UTF-8 válido",
            path=path,
        ) from exc
    if encoded_size > MAX_MANIFEST_BYTES:
        raise WorkspaceManifestError(
            "workspace.yaml excede o tamanho permitido",
            code="manifest-too-large",
            path=path,
        )

    depth = 0
    start_tokens = (
        BlockMappingStartToken,
        BlockSequenceStartToken,
        FlowMappingStartToken,
        FlowSequenceStartToken,
    )
    end_tokens = (BlockEndToken, FlowMappingEndToken, FlowSequenceEndToken)
    recursion_failed = False
    yaml_failed = False
    data: Any = None
    try:
        for token in yaml.scan(text):
            if isinstance(token, AnchorToken):
                raise WorkspaceManifestError(
                    "anchor YAML não permitido",
                    path=path,
                )
            if isinstance(token, AliasToken):
                raise WorkspaceManifestError(
                    "alias YAML não permitido",
                    path=path,
                )
            if isinstance(token, start_tokens):
                depth += 1
                if depth > MAX_YAML_DEPTH:
                    raise WorkspaceManifestError(
                        "manifesto YAML excede a profundidade permitida",
                        code="manifest-too-complex",
                        path=path,
                    )
            elif isinstance(token, end_tokens):
                depth = max(0, depth - 1)
        data = yaml.load(text, Loader=_WorkspaceLoader)
    except WorkspaceManifestError:
        raise
    except RecursionError:
        recursion_failed = True
    except yaml.YAMLError:
        yaml_failed = True
    if recursion_failed:
        raise WorkspaceManifestError(
            "manifesto YAML excede a complexidade permitida",
            code="manifest-too-complex",
            path=path,
        )
    if yaml_failed:
        raise WorkspaceManifestError(
            "manifesto inválido",
            path=path,
        )
    return validate_manifest(data)


def _require_secure_platform(*, path: Path) -> None:
    required_flags = ("O_DIRECTORY", "O_NOFOLLOW", "O_CLOEXEC")
    supported = (
        os.name == "posix"
        and all(hasattr(os, name) for name in required_flags)
        and _SECURE_DIR_FD_SUPPORTED
        and _SECURE_NOFOLLOW_STAT_SUPPORTED
    )
    if not supported:
        raise WorkspaceManifestError(
            "plataforma sem primitivas POSIX exigidas para I/O seguro",
            code="unsupported-platform",
            path=path,
        )


def _open_workspace_root(root: Path) -> int:
    """Abre cada componente do root real sem seguir symlinks durante a operação."""

    _require_secure_platform(path=root)
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    descriptor: int | None = None
    try:
        descriptor = os.open(root.anchor or os.sep, flags)
        for component in root.parts[1:]:
            previous_descriptor = descriptor
            descriptor = os.open(
                component,
                flags,
                dir_fd=previous_descriptor,
            )
            os.close(previous_descriptor)
        opened = os.fstat(descriptor)
        if not stat.S_ISDIR(opened.st_mode):
            raise WorkspaceManifestError(
                "workspace deve ser um diretório regular",
                code="invalid-workspace-root",
                path=root,
            )
        return descriptor
    except WorkspaceManifestError:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
        raise
    except OSError as exc:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
        if exc.errno in {errno.ELOOP, errno.ENOTDIR}:
            message = "workspace contém symlink ou componente de path inseguro"
        else:
            message = "workspace indisponível durante abertura segura"
        raise WorkspaceManifestError(
            message,
            code="unsafe-path",
            path=root,
        ) from exc


def _open_control_directory(
    root_descriptor: int,
    root: Path,
    *,
    create: bool,
) -> int:
    control_name = MANIFEST_RELATIVE_PATH.parent.name
    control = root / MANIFEST_RELATIVE_PATH.parent
    created = False
    if create:
        try:
            os.mkdir(control_name, mode=0o700, dir_fd=root_descriptor)
            created = True
        except FileExistsError:
            pass
        except OSError as exc:
            raise WorkspaceManifestError(
                "não foi possível criar .exocortex",
                code="write-failed",
                path=control,
            ) from exc
        if created:
            try:
                os.fsync(root_descriptor)
            except OSError as exc:
                raise WorkspaceManifestError(
                    ".exocortex criada, mas a durabilidade do workspace não foi confirmada",
                    code="partial-failure",
                    path=control,
                ) from exc

    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    try:
        descriptor = os.open(control_name, flags, dir_fd=root_descriptor)
    except FileNotFoundError as exc:
        raise WorkspaceManifestError(
            ".exocortex ausente",
            code="missing",
            path=control,
        ) from exc
    except OSError as exc:
        if exc.errno in {errno.ELOOP, errno.ENOTDIR}:
            message = ".exocortex não pode ser symlink"
        else:
            message = ".exocortex indisponível"
        raise WorkspaceManifestError(
            message,
            code="unsafe-path",
            path=control,
        ) from exc
    try:
        opened = os.fstat(descriptor)
    except OSError as exc:
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise WorkspaceManifestError(
            ".exocortex indisponível",
            code="unsafe-path",
            path=control,
        ) from exc
    if not stat.S_ISDIR(opened.st_mode):
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise WorkspaceManifestError(
            ".exocortex deve ser diretório regular",
            path=control,
        )
    return descriptor


def _open_workspace_descriptors(root: Path, *, create: bool) -> tuple[int, int]:
    """Abre e devolve descriptors ancorados do root e de .exocortex."""

    root_descriptor = _open_workspace_root(root)
    try:
        control_descriptor = _open_control_directory(
            root_descriptor,
            root,
            create=create,
        )
    except BaseException as exc:
        try:
            os.close(root_descriptor)
        except OSError:
            exc.add_note("fechamento do descriptor do workspace também falhou")
        raise
    return root_descriptor, control_descriptor


def _verify_workspace_binding(
    root: Path,
    root_descriptor: int,
    control_descriptor: int,
) -> None:
    """Confirma que os descriptors ainda correspondem ao path canonicalizado."""

    current_root_descriptor: int | None = None
    primary_error: BaseException | None = None
    try:
        try:
            current_root_descriptor = _open_workspace_root(root)
            pinned_root = os.fstat(root_descriptor)
            current_root = os.fstat(current_root_descriptor)
            if (pinned_root.st_dev, pinned_root.st_ino) != (
                current_root.st_dev,
                current_root.st_ino,
            ):
                raise WorkspaceManifestError(
                    "workspace mudou durante a operação",
                    code="unsafe-path",
                    path=root,
                )

            control_name = MANIFEST_RELATIVE_PATH.parent.name
            current_control = os.stat(
                control_name,
                dir_fd=root_descriptor,
                follow_symlinks=False,
            )
            pinned_control = os.fstat(control_descriptor)
            if not stat.S_ISDIR(current_control.st_mode) or (
                current_control.st_dev,
                current_control.st_ino,
            ) != (pinned_control.st_dev, pinned_control.st_ino):
                raise WorkspaceManifestError(
                    "workspace mudou durante a operação",
                    code="unsafe-path",
                    path=root,
                )
        except WorkspaceManifestError as exc:
            raise WorkspaceManifestError(
                "workspace mudou durante a operação",
                code="unsafe-path",
                path=root,
            ) from exc
        except OSError as exc:
            raise WorkspaceManifestError(
                "workspace mudou durante a operação",
                code="unsafe-path",
                path=root,
            ) from exc
    except BaseException as exc:
        primary_error = exc
        raise
    finally:
        if current_root_descriptor is not None:
            try:
                os.close(current_root_descriptor)
            except OSError as exc:
                message = "fechamento da verificação do workspace falhou"
                if primary_error is not None:
                    primary_error.add_note(message)
                else:
                    raise WorkspaceManifestError(
                        message,
                        code="cleanup-failed",
                        path=root,
                    ) from exc


def _close_operation_descriptors(
    root_descriptor: int,
    control_descriptor: int,
    *,
    primary_error: BaseException | None,
    path: Path,
) -> None:
    cleanup_errors: list[str] = []
    for label, descriptor in (
        (".exocortex", control_descriptor),
        ("workspace", root_descriptor),
    ):
        try:
            os.close(descriptor)
        except OSError:
            cleanup_errors.append(f"fechamento de {label}")
    if not cleanup_errors:
        return
    cleanup_message = "cleanup de descriptors falhou: " + "; ".join(cleanup_errors)
    if primary_error is not None:
        primary_error.add_note(cleanup_message)
        return
    raise WorkspaceManifestError(
        cleanup_message,
        code="cleanup-failed",
        path=path,
    )


def _read_manifest_text(control_descriptor: int, *, manifest_path: Path) -> str:
    name = MANIFEST_RELATIVE_PATH.name
    try:
        metadata = os.stat(
            name,
            dir_fd=control_descriptor,
            follow_symlinks=False,
        )
    except FileNotFoundError as exc:
        raise WorkspaceManifestError(
            "workspace.yaml ausente",
            code="missing",
            path=manifest_path,
        ) from exc
    except OSError as exc:
        raise WorkspaceManifestError(
            "workspace.yaml indisponível",
            code="invalid-manifest",
            path=manifest_path,
        ) from exc
    if stat.S_ISLNK(metadata.st_mode):
        raise WorkspaceManifestError(
            "workspace.yaml não pode ser symlink",
            code="unsafe-path",
            path=manifest_path,
        )
    if not stat.S_ISREG(metadata.st_mode):
        raise WorkspaceManifestError(
            "workspace.yaml deve ser arquivo regular",
            path=manifest_path,
        )
    if metadata.st_size > MAX_MANIFEST_BYTES:
        raise WorkspaceManifestError(
            "workspace.yaml excede o tamanho permitido",
            code="manifest-too-large",
            path=manifest_path,
        )

    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC
    descriptor: int | None = None
    primary_error: BaseException | None = None
    try:
        try:
            descriptor = os.open(name, flags, dir_fd=control_descriptor)
            opened = os.fstat(descriptor)
            if not stat.S_ISREG(opened.st_mode):
                raise WorkspaceManifestError(
                    "workspace.yaml deve ser arquivo regular",
                    path=manifest_path,
                )
            if opened.st_size > MAX_MANIFEST_BYTES:
                raise WorkspaceManifestError(
                    "workspace.yaml excede o tamanho permitido",
                    code="manifest-too-large",
                    path=manifest_path,
                )
            with os.fdopen(descriptor, "rb") as handle:
                descriptor = None
                payload = handle.read(MAX_MANIFEST_BYTES + 1)
            if len(payload) > MAX_MANIFEST_BYTES:
                raise WorkspaceManifestError(
                    "workspace.yaml excede o tamanho permitido",
                    code="manifest-too-large",
                    path=manifest_path,
                )
            try:
                return payload.decode("utf-8")
            except UnicodeError as exc:
                raise WorkspaceManifestError(
                    "manifesto não está em UTF-8 válido",
                    path=manifest_path,
                ) from exc
        except WorkspaceManifestError:
            raise
        except OSError as exc:
            if exc.errno == errno.ELOOP:
                message = "workspace.yaml não pode ser symlink"
                code = "unsafe-path"
            else:
                message = "workspace.yaml indisponível"
                code = "invalid-manifest"
            raise WorkspaceManifestError(
                message,
                code=code,
                path=manifest_path,
            ) from exc
    except BaseException as exc:
        primary_error = exc
        raise
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError as exc:
                if primary_error is not None:
                    primary_error.add_note("fechamento de workspace.yaml também falhou")
                else:
                    raise WorkspaceManifestError(
                        "fechamento de workspace.yaml falhou",
                        code="cleanup-failed",
                        path=manifest_path,
                    ) from exc


def load_manifest(
    workspace_root: str | Path,
    *,
    cwd: str | Path | None = None,
) -> dict[str, Any]:
    """Entrada segura única: root → path → YAML estrito → schema → secrets."""

    root = resolve_workspace_root(workspace_root, cwd=cwd)
    manifest_path = root / MANIFEST_RELATIVE_PATH
    root_descriptor, control_descriptor = _open_workspace_descriptors(
        root,
        create=False,
    )
    primary_error: BaseException | None = None
    try:
        try:
            text = _read_manifest_text(
                control_descriptor,
                manifest_path=manifest_path,
            )
            _verify_workspace_binding(
                root,
                root_descriptor,
                control_descriptor,
            )
        except BaseException as exc:
            primary_error = exc
            raise
    finally:
        _close_operation_descriptors(
            root_descriptor,
            control_descriptor,
            primary_error=primary_error,
            path=manifest_path,
        )
    return _parse_manifest_text(text, path=manifest_path)


def dump_manifest(data: object) -> str:
    """Serializa o contrato em ordem determinística e valida o round-trip."""

    manifest = validate_manifest(data)
    binding = manifest["cognitive_binding"]
    canonical = {
        "apiVersion": manifest["apiVersion"],
        "kind": manifest["kind"],
        "metadata": {
            "id": manifest["metadata"]["id"],
            "created_at": manifest["metadata"]["created_at"],
        },
        "project": {
            "title": manifest["project"]["title"],
            "objective": manifest["project"]["objective"],
            "status": manifest["project"]["status"],
            "status_changed_at": manifest["project"]["status_changed_at"],
            "status_reason": manifest["project"]["status_reason"],
        },
        "cognitive_binding": {
            "primary_microverso": binding["primary_microverso"],
            "related_microversos": list(binding.get("related_microversos", [])),
        },
    }
    dump_failed = False
    text = ""
    try:
        text = yaml.safe_dump(
            canonical,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            width=120,
        )
    except yaml.YAMLError:
        dump_failed = True
    if dump_failed:
        raise WorkspaceManifestError(
            "serialização do manifesto falhou",
            path=None,
        )
    _parse_manifest_text(text)
    return text


def _check_manifest_target(control_descriptor: int, *, manifest_path: Path) -> None:
    try:
        metadata = os.stat(
            MANIFEST_RELATIVE_PATH.name,
            dir_fd=control_descriptor,
            follow_symlinks=False,
        )
    except FileNotFoundError:
        return
    except OSError as exc:
        raise WorkspaceManifestError(
            "workspace.yaml indisponível",
            code="write-failed",
            path=manifest_path,
        ) from exc
    if stat.S_ISLNK(metadata.st_mode):
        raise WorkspaceManifestError(
            "workspace.yaml não pode ser symlink",
            code="unsafe-path",
            path=manifest_path,
        )
    if not stat.S_ISREG(metadata.st_mode):
        raise WorkspaceManifestError(
            "workspace.yaml deve ser arquivo regular",
            path=manifest_path,
        )


def write_manifest_atomic(
    workspace_root: str | Path,
    data: object,
    *,
    cwd: str | Path | None = None,
) -> Path:
    """Valida antes de escrever e substitui o manifesto com durabilidade local."""

    text = dump_manifest(data)
    root = resolve_workspace_root(workspace_root, cwd=cwd)
    manifest_path = root / MANIFEST_RELATIVE_PATH
    root_descriptor, control_descriptor = _open_workspace_descriptors(
        root,
        create=True,
    )

    temp_name: str | None = None
    temp_descriptor: int | None = None
    published = False
    primary_error: BaseException | None = None
    try:
        try:
            _verify_workspace_binding(
                root,
                root_descriptor,
                control_descriptor,
            )
            _check_manifest_target(
                control_descriptor,
                manifest_path=manifest_path,
            )
            temp_name = f".workspace.yaml.tmp.{os.getpid()}.{secrets.token_hex(8)}"
            flags = (
                os.O_WRONLY
                | os.O_CREAT
                | os.O_EXCL
                | os.O_NOFOLLOW
                | os.O_CLOEXEC
            )
            temp_descriptor = os.open(
                temp_name,
                flags,
                0o600,
                dir_fd=control_descriptor,
            )
            with os.fdopen(temp_descriptor, "w", encoding="utf-8", newline="\n") as handle:
                temp_descriptor = None
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
            _verify_workspace_binding(
                root,
                root_descriptor,
                control_descriptor,
            )
            os.replace(
                temp_name,
                MANIFEST_RELATIVE_PATH.name,
                src_dir_fd=control_descriptor,
                dst_dir_fd=control_descriptor,
            )
            published = True
            temp_name = None
            try:
                os.fsync(control_descriptor)
            except OSError as exc:
                raise WorkspaceManifestError(
                    "manifesto publicado, mas a confirmação de durabilidade do diretório falhou",
                    code="partial-failure",
                    path=manifest_path,
                ) from exc
            try:
                _verify_workspace_binding(
                    root,
                    root_descriptor,
                    control_descriptor,
                )
            except WorkspaceManifestError as exc:
                raise WorkspaceManifestError(
                    "manifesto publicado, mas o workspace mudou durante a operação",
                    code="partial-failure",
                    path=manifest_path,
                ) from exc
        except WorkspaceManifestError:
            raise
        except (OSError, UnicodeError) as exc:
            if published:
                message = "manifesto publicado, mas a finalização da escrita falhou"
                code = "partial-failure"
            else:
                message = "escrita atômica do manifesto falhou"
                code = "write-failed"
            raise WorkspaceManifestError(
                message,
                code=code,
                path=manifest_path,
            ) from exc
    except BaseException as exc:
        primary_error = exc
        raise
    finally:
        cleanup_errors: list[str] = []
        if temp_descriptor is not None:
            try:
                os.close(temp_descriptor)
            except OSError:
                cleanup_errors.append("fechamento do temporário")
        if temp_name is not None:
            try:
                os.unlink(temp_name, dir_fd=control_descriptor)
            except FileNotFoundError:
                pass
            except OSError:
                cleanup_errors.append("remoção do temporário")
        try:
            os.close(control_descriptor)
        except OSError:
            cleanup_errors.append("fechamento de .exocortex")
        try:
            os.close(root_descriptor)
        except OSError:
            cleanup_errors.append("fechamento do workspace")

        if cleanup_errors:
            cleanup_message = "cleanup da escrita falhou: " + "; ".join(cleanup_errors)
            if primary_error is not None:
                primary_error.add_note(cleanup_message)
            else:
                if published:
                    raise WorkspaceManifestError(
                        "manifesto publicado, mas a finalização da escrita falhou: "
                        + "; ".join(cleanup_errors),
                        code="partial-failure",
                        path=manifest_path,
                    )
                raise WorkspaceManifestError(
                    cleanup_message,
                    code="cleanup-failed",
                    path=manifest_path,
                )
    return manifest_path
