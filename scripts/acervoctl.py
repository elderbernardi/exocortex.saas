#!/usr/bin/env python3
"""CLI operacional do Acervo Control Plane.

Superfície local oficial para provar o contrato prepare/commit antes da camada MCP.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from acervo_semantic_core import (
    apply_supersede,
    commit_write,
    conflict_check,
    distill_episode,
    export_microverso,
    list_microversos,
    mark_intention,
    new_object,
    open_dispute,
    prepare_write,
    refresh_entity,
    resolve_acervo_root,
    search_acervo,
    slugify,
    validate_entry,
)


def print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def write_receipt_if_needed(payload: dict[str, Any], receipt_out: str | None) -> None:
    if not receipt_out:
        return
    Path(receipt_out).expanduser().write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_receipt(raw: str) -> dict[str, Any]:
    candidate = Path(raw).expanduser()
    if candidate.exists():
        return json.loads(candidate.read_text(encoding="utf-8"))
    return json.loads(raw)


def command_list_microversos(args: argparse.Namespace) -> dict[str, Any]:
    microversos = list_microversos(args.acervo_root)
    return {"ok": True, "microversos": microversos, "count": len(microversos)}


def command_search(args: argparse.Namespace) -> dict[str, Any]:
    matches = search_acervo(args.acervo_root, args.query, limit=args.limit)
    return {"ok": True, "query": args.query, "count": len(matches), "matches": matches}


def command_prepare_write(args: argparse.Namespace) -> dict[str, Any]:
    filename = args.filename or f"{slugify(args.title)}.md"
    payload = prepare_write(
        acervo_root=args.acervo_root,
        microverso=args.microverso,
        nature=args.nature,
        filename=filename,
        active_microverso=args.active_microverso or args.microverso,
    )
    write_receipt_if_needed(payload, args.receipt_out)
    return payload


def command_commit_write(args: argparse.Namespace) -> dict[str, Any]:
    prepared = load_receipt(args.receipt)
    if args.content_file:
        content = Path(args.content_file).expanduser().read_text(encoding="utf-8")
    elif args.content is not None:
        content = args.content
    else:
        raise RuntimeError("Informe --content-file ou --content para commit-write.")

    return commit_write(
        prepared,
        content=content,
        entry_type=args.entry_type,
        description=args.description,
        class_name=args.class_name,
    )


def command_validate_frontmatter(args: argparse.Namespace) -> dict[str, Any]:
    validate_entry(args.path)
    return {"ok": True, "path": str(Path(args.path).expanduser().resolve())}


def load_tool_module(acervo_root: Path, name: str):
    """Load a Plane-2 tool from acervo/global/tools (tools live inside the Acervo)."""
    candidates = [
        acervo_root / "global" / "tools" / f"{name}.py",
        Path(__file__).resolve().parents[1] / "acervo" / "global" / "tools" / f"{name}.py",
    ]
    for candidate in candidates:
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location(name, candidate)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise RuntimeError(f"{name}.py não encontrado em global/tools.")


def load_catalog_module(acervo_root: Path):
    return load_tool_module(acervo_root, "acervo_catalog")


def command_reindex(args: argparse.Namespace) -> dict[str, Any]:
    root = resolve_acervo_root(args.acervo_root)
    catalog = load_catalog_module(root)
    payload: dict[str, Any] = {"ok": True, "catalog_build": catalog.build_catalog(root)}
    if args.with_hindsight:
        indexer = root / "global" / "tools" / "acervo_hindsight_index.py"
        proc = subprocess.run(
            [sys.executable, str(indexer), "scan", "--all"],
            capture_output=True, text=True, env={**os.environ, "ACERVO": str(root)},
        )
        payload["hindsight_scan"] = {
            "exit_code": proc.returncode,
            "output": proc.stdout.strip()[-4000:],
            "stderr": proc.stderr.strip()[-2000:],
        }
        if proc.returncode != 0:
            payload["ok"] = False
    return payload


def command_retrieve(args: argparse.Namespace) -> dict[str, Any]:
    root = resolve_acervo_root(args.acervo_root)
    retrieve_mod = load_tool_module(root, "acervo_retrieve")
    payload = retrieve_mod.retrieve(
        args.query,
        args.scope,
        budget_tokens=args.budget,
        acervo_root=root,
        k=args.k,
        allow_scopes=args.allow_scope,
        with_hindsight=args.with_hindsight,
    )
    # Abstenção não é erro: found=False com ok=True e mensagem explícita (07 §5).
    payload["ok"] = True
    return payload


def command_briefing(args: argparse.Namespace) -> dict[str, Any]:
    root = resolve_acervo_root(args.acervo_root)
    interface = load_tool_module(root, "acervo_interface")
    return interface.briefing(
        root, today=args.today, scopes=args.scope, compact=args.mode == "compact",
        budget_tokens=args.budget, since_hours=args.since_hours,
        calendar_file=args.calendar_file,
    )


def command_posture(args: argparse.Namespace) -> dict[str, Any]:
    root = resolve_acervo_root(args.acervo_root)
    interface = load_tool_module(root, "acervo_interface")
    return interface.posture(
        root, mode=args.mode, query=args.query, scope=args.scope,
        allow_scopes=args.allow_scope, budget_tokens=args.budget, k=args.k,
    )


def command_doctor(args: argparse.Namespace) -> dict[str, Any]:
    root = resolve_acervo_root(args.acervo_root)
    catalog = load_catalog_module(root)
    return catalog.doctor(root)


def command_consolidation_scan(args: argparse.Namespace) -> dict[str, Any]:
    root = resolve_acervo_root(args.acervo_root)
    consolidation = load_tool_module(root, "acervo_consolidation")
    payload = consolidation.scan(
        root,
        today=args.today,
        stale_days=args.stale_days,
        upcoming_days=args.upcoming_days,
        use_decay_days=args.use_decay_days,
    )
    if args.format == "markdown":
        payload["markdown"] = consolidation.render_markdown(payload)
    elif args.format == "digest":
        payload["digest"] = consolidation.render_digest(payload)
    return payload


def command_conflict_check(args: argparse.Namespace) -> dict[str, Any]:
    text = sys.stdin.read() if args.stdin else None
    return conflict_check(
        acervo_root=args.acervo_root,
        candidate_path=None if args.stdin else args.file,
        candidate_text=text,
        scope=args.scope,
    )


def command_apply_supersede(args: argparse.Namespace) -> dict[str, Any]:
    return apply_supersede(
        acervo_root=args.acervo_root, new_path=args.new, old_path=args.old
    )


def command_open_dispute(args: argparse.Namespace) -> dict[str, Any]:
    return open_dispute(
        acervo_root=args.acervo_root,
        a_path=args.a,
        b_path=args.b,
        title=args.title,
        scope=args.scope,
    )


def command_new_object(args: argparse.Namespace) -> dict[str, Any]:
    body = None
    if args.body_file:
        body = Path(args.body_file).expanduser().read_text(encoding="utf-8")
    return new_object(
        acervo_root=args.acervo_root,
        type_=args.type,
        scope=args.scope,
        title=args.title,
        description=args.description,
        aliases=_split_csv(args.aliases),
        due=args.due,
        trigger=args.trigger,
        owed_to=args.owed_to,
        tags=_split_csv(args.tags),
        entities=_split_csv(args.entities),
        body=body,
        draft=args.draft,
        source_trust=args.source_trust,
    )


def command_mark_intention(args: argparse.Namespace) -> dict[str, Any]:
    return mark_intention(
        acervo_root=args.acervo_root,
        path=args.path,
        state=args.state,
        reason=args.reason,
        today=args.today,
    )


def command_distill_episode(args: argparse.Namespace) -> dict[str, Any]:
    summary = args.summary
    if args.summary_file:
        summary = Path(args.summary_file).expanduser().read_text(encoding="utf-8")
    return distill_episode(
        acervo_root=args.acervo_root,
        scope=args.scope,
        title=args.title,
        summary=summary,
        signals=_split_csv(args.signals),
        participants=_split_csv(args.participants),
        decisions=args.decision,
        open_loops=args.open_loop,
        session_ref=args.session_ref,
        tags=_split_csv(args.tags),
        source_trust=args.source_trust,
    )


def command_refresh_entity(args: argparse.Namespace) -> dict[str, Any]:
    return refresh_entity(
        acervo_root=args.acervo_root,
        path=args.path,
        note=args.note,
        date=args.date,
        add_aliases=_split_csv(args.add_aliases),
    )


def command_sweep_intentions(args: argparse.Namespace) -> dict[str, Any]:
    """Daily prospective-memory sweep (08 §6): auto-expire overdue active
    intentions through the governed verb. Read-only by default; --apply writes.
    done/dropped need agent/executive judgment and are never auto-applied."""
    root = resolve_acervo_root(args.acervo_root)
    consolidation = load_tool_module(root, "acervo_consolidation")
    scan = consolidation.scan(root, today=args.today)
    as_of = scan["as_of"]
    overdue = [it for it in scan["buckets"]["intentions_due"] if it.get("days_overdue")]
    result: dict[str, Any] = {
        "ok": True,
        "operation": "sweep_intentions",
        "as_of": as_of,
        "applied": bool(args.apply),
        "candidates": len(overdue),
        "expired": [],
        "skipped": [],
    }
    for it in overdue:
        entry = {
            "path": it["path"],
            "title": it.get("title"),
            "due": it.get("due"),
            "days_overdue": it.get("days_overdue"),
        }
        if not args.apply:
            result["expired"].append({**entry, "would_expire": True})
            continue
        try:
            outcome = mark_intention(
                acervo_root=root,
                path=root / it["path"],
                state="expired",
                reason=f"varredura automática: vencida em {it.get('due')}, sem resolução até {as_of}",
                today=as_of,
            )
            result["expired"].append({**entry, "unchanged": outcome.get("unchanged", False)})
        except Exception as exc:  # governed write refused — surface, don't abort the batch
            result["ok"] = False
            result["skipped"].append({**entry, "error": str(exc)})
    return result


def _split_csv(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def command_export_microverso(args: argparse.Namespace) -> dict[str, Any]:
    return export_microverso(
        acervo_root=args.acervo_root,
        slug=args.slug,
        out_dir=args.out,
        tar=args.tar,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Acervo Control Plane CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    list_cmd = sub.add_parser("list-microversos", help="Lista microversos disponíveis")
    list_cmd.add_argument("--acervo-root", help="Raiz do Acervo")
    list_cmd.set_defaults(handler=command_list_microversos)

    search_cmd = sub.add_parser("search", help="Busca simples em markdown do Acervo")
    search_cmd.add_argument("--acervo-root", help="Raiz do Acervo")
    search_cmd.add_argument("--query", required=True)
    search_cmd.add_argument("--limit", type=int, default=20)
    search_cmd.set_defaults(handler=command_search)

    prepare_cmd = sub.add_parser("prepare-write", help="Prepara uma mutação semântica")
    prepare_cmd.add_argument("--acervo-root", help="Raiz do Acervo")
    prepare_cmd.add_argument("--microverso", required=True)
    prepare_cmd.add_argument("--nature", required=True)
    prepare_cmd.add_argument("--title", required=True)
    prepare_cmd.add_argument("--filename", help="Override explícito do nome do arquivo")
    prepare_cmd.add_argument("--active-microverso", help="Override do microverso ativo")
    prepare_cmd.add_argument("--receipt-out", help="Arquivo para gravar o receipt JSON")
    prepare_cmd.set_defaults(handler=command_prepare_write)

    commit_cmd = sub.add_parser("commit-write", help="Efetiva uma mutação semântica preparada")
    commit_cmd.add_argument("--receipt", required=True, help="JSON inline ou caminho para receipt")
    commit_cmd.add_argument("--content-file", help="Arquivo markdown a gravar")
    commit_cmd.add_argument("--content", help="Conteúdo inline markdown")
    commit_cmd.add_argument("--entry-type", default="CREATED")
    commit_cmd.add_argument("--description", required=True)
    commit_cmd.add_argument("--class-name", default="volátil")
    commit_cmd.set_defaults(handler=command_commit_write)

    validate_cmd = sub.add_parser("validate-frontmatter", help="Valida frontmatter de um arquivo")
    validate_cmd.add_argument("--path", required=True)
    validate_cmd.set_defaults(handler=command_validate_frontmatter)

    reindex_cmd = sub.add_parser("reindex", help="Reconstrói o catálogo derivado (catalog.sqlite)")
    reindex_cmd.add_argument("--acervo-root", help="Raiz do Acervo")
    reindex_cmd.add_argument("--with-hindsight", action="store_true", help="Também roda o indexer Hindsight (scan --all)")
    reindex_cmd.set_defaults(handler=command_reindex)

    retrieve_cmd = sub.add_parser("retrieve", help="Recuperação híbrida com empacotamento de contexto (07-retrieval-policy)")
    retrieve_cmd.add_argument("--acervo-root", help="Raiz do Acervo")
    retrieve_cmd.add_argument("--query", required=True, help="Pergunta/tarefa a rotear")
    retrieve_cmd.add_argument("--scope", required=True, help="Microverso primário (ou 'global')")
    retrieve_cmd.add_argument("--budget", type=int, default=6000, help="Orçamento de tokens do pacote (default: 6000)")
    retrieve_cmd.add_argument("--k", type=int, default=5, help="Máximo de arquivos canônicos (default: 5)")
    retrieve_cmd.add_argument("--allow-scope", action="append", default=[],
                              help="Escopo extra explícito para consulta cross-microverso (repetível)")
    retrieve_cmd.add_argument("--with-hindsight", action="store_true",
                              help="Liga o suplemento semântico opcional (H2: OFF por padrão)")
    retrieve_cmd.add_argument("--json", action="store_true",
                              help="Saída JSON (já é o padrão; aceito por compatibilidade de contrato)")
    retrieve_cmd.set_defaults(handler=command_retrieve)

    briefing_cmd = sub.add_parser("briefing", help="Briefing v2: intenções, disputas, episódios, drafts, contexto e agenda")
    briefing_cmd.add_argument("--acervo-root", help="Raiz do Acervo")
    briefing_cmd.add_argument("--scope", action="append", help="Limita a um microverso (repetível; default: todos)")
    briefing_cmd.add_argument("--mode", choices=["compact", "detailed"], default="detailed")
    briefing_cmd.add_argument("--today", help="Data de corte YYYY-MM-DD")
    briefing_cmd.add_argument("--since-hours", type=int, default=24, help="Janela de episódios recentes")
    briefing_cmd.add_argument("--budget", type=int, default=4000, help="Orçamento máximo em tokens estimados")
    briefing_cmd.add_argument("--calendar-file", help="JSON opcional com eventos do dia")
    briefing_cmd.set_defaults(handler=command_briefing)

    posture_cmd = sub.add_parser("posture", help="Pacote tipado para modo decisão ou modo pesquisa")
    posture_cmd.add_argument("--acervo-root", help="Raiz do Acervo")
    posture_cmd.add_argument("--mode", choices=["decision", "research"], required=True)
    posture_cmd.add_argument("--query", required=True)
    posture_cmd.add_argument("--scope", required=True)
    posture_cmd.add_argument("--allow-scope", action="append", default=[])
    posture_cmd.add_argument("--budget", type=int, default=12000)
    posture_cmd.add_argument("--k", type=int, default=8)
    posture_cmd.set_defaults(handler=command_posture)

    doctor_cmd = sub.add_parser("doctor", help="Relatório de integridade do Acervo (links, drift, lifecycle)")
    doctor_cmd.add_argument("--acervo-root", help="Raiz do Acervo")
    doctor_cmd.set_defaults(handler=command_doctor)

    cons_cmd = sub.add_parser("consolidation-scan", help="Varredura read-only da fila de consolidação/lifecycle v2 (Phase 4)")
    cons_cmd.add_argument("--acervo-root", help="Raiz do Acervo")
    cons_cmd.add_argument("--today", help="Data de corte YYYY-MM-DD")
    cons_cmd.add_argument("--stale-days", type=int, default=90, help="Dias sem acesso para sinalizar volátil stale")
    cons_cmd.add_argument("--upcoming-days", type=int, default=7, help="Janela de intenções próximas")
    cons_cmd.add_argument("--use-decay-days", type=int, default=180, help="Dias sem retrieval para sinal use-decay (H12)")
    cons_cmd.add_argument("--format", choices=["json", "markdown", "digest"], default="json", help="Inclui markdown/digest renderizado quando solicitado")
    cons_cmd.set_defaults(handler=command_consolidation_scan)

    export_cmd = sub.add_parser("export-microverso", help="Empacota um microverso")
    export_cmd.add_argument("--acervo-root", help="Raiz do Acervo")
    export_cmd.add_argument("--slug", required=True)
    export_cmd.add_argument("--out", required=True)
    export_cmd.add_argument("--tar", action="store_true")
    export_cmd.set_defaults(handler=command_export_microverso)

    # ── Write pipeline: conflict protocol + new-object (08-write-policy) ──────
    cc_cmd = sub.add_parser("conflict-check", help="Detecta overlap determinístico de um candidato (08 §4)")
    cc_cmd.add_argument("--acervo-root", help="Raiz do Acervo")
    cc_cmd.add_argument("--file", help="Caminho do candidato .md")
    cc_cmd.add_argument("--stdin", action="store_true", help="Ler frontmatter+corpo do candidato via stdin")
    cc_cmd.add_argument("--scope", help="Microverso ou 'global' (derivado do path se ausente)")
    cc_cmd.set_defaults(handler=command_conflict_check)

    sup_cmd = sub.add_parser("apply-supersede", help="Pareamento atômico de supersessão (08 §3, verbo 2)")
    sup_cmd.add_argument("--acervo-root", help="Raiz do Acervo")
    sup_cmd.add_argument("--new", required=True, help="Arquivo novo (fica active)")
    sup_cmd.add_argument("--old", required=True, help="Arquivo antigo (vira superseded)")
    sup_cmd.set_defaults(handler=command_apply_supersede)

    disp_cmd = sub.add_parser("open-dispute", help="Cria objeto conflict e estampa disputed_by (08 §4)")
    disp_cmd.add_argument("--acervo-root", help="Raiz do Acervo")
    disp_cmd.add_argument("--a", required=True, help="Arquivo do lado A")
    disp_cmd.add_argument("--b", required=True, help="Arquivo do lado B")
    disp_cmd.add_argument("--title", required=True, help="Título da disputa")
    disp_cmd.add_argument("--scope", required=True, help="Escopo do objeto conflict (micro slug ou 'global')")
    disp_cmd.set_defaults(handler=command_open_dispute)

    no_cmd = sub.add_parser("new-object", help="Scaffold v0.2 de episode/entity/intention (05 §3)")
    no_cmd.add_argument("--acervo-root", help="Raiz do Acervo")
    no_cmd.add_argument("--type", required=True, choices=["episode", "entity", "intention"])
    no_cmd.add_argument("--scope", required=True, help="Microverso ou 'global'/'shared'")
    no_cmd.add_argument("--title", required=True)
    no_cmd.add_argument("--description")
    no_cmd.add_argument("--aliases", help="Lista separada por vírgula (entity: obrigatório)")
    no_cmd.add_argument("--due", help="intention: data ISO YYYY-MM-DD")
    no_cmd.add_argument("--trigger", help="intention: condição de gatilho")
    no_cmd.add_argument("--owed-to", dest="owed_to", help="intention: slug da entidade credora")
    no_cmd.add_argument("--tags", help="Lista separada por vírgula")
    no_cmd.add_argument("--entities", help="Lista separada por vírgula (slugs)")
    no_cmd.add_argument("--body-file", dest="body_file", help="Arquivo com o corpo markdown")
    no_cmd.add_argument("--draft", action="store_true", help="Força status: draft")
    no_cmd.add_argument("--source-trust", dest="source_trust", default="agent",
                        choices=["executive", "agent", "untrusted"],
                        help="untrusted força draft (trust gate, 08 §2)")
    no_cmd.set_defaults(handler=command_new_object)

    mi_cmd = sub.add_parser("mark-intention", help="Encerra uma intenção: active/draft → done|dropped|expired (05 §3)")
    mi_cmd.add_argument("--acervo-root", help="Raiz do Acervo")
    mi_cmd.add_argument("--path", required=True, help="Caminho do arquivo da intenção")
    mi_cmd.add_argument("--state", required=True, choices=["done", "dropped", "expired"])
    mi_cmd.add_argument("--reason", required=True, help="Por que a intenção encerrou (uma linha)")
    mi_cmd.add_argument("--today", help="Data de resolução YYYY-MM-DD (default: hoje UTC)")
    mi_cmd.set_defaults(handler=command_mark_intention)

    de_cmd = sub.add_parser("distill-episode", help="Distila uma sessão significativa em episódio; exige gate H9 (04 §4.1)")
    de_cmd.add_argument("--acervo-root", help="Raiz do Acervo")
    de_cmd.add_argument("--scope", required=True, help="Microverso ou 'global'")
    de_cmd.add_argument("--title", required=True)
    de_cmd.add_argument("--summary", help="Resumo do que a sessão produziu")
    de_cmd.add_argument("--summary-file", dest="summary_file", help="Arquivo com o resumo (alternativa a --summary)")
    de_cmd.add_argument("--signals", required=True,
                        help="Sinais de significância H9 (vírgula): decision,commitment,artifact,executive_flag")
    de_cmd.add_argument("--participants", help="Slugs de entidades participantes (vírgula)")
    de_cmd.add_argument("--decision", action="append", help="Decisão extraída (repetível)")
    de_cmd.add_argument("--open-loop", dest="open_loop", action="append", help="Loop aberto (repetível)")
    de_cmd.add_argument("--session-ref", dest="session_ref", help="Ponteiro session:// da transcrição")
    de_cmd.add_argument("--tags", help="Lista separada por vírgula")
    de_cmd.add_argument("--source-trust", dest="source_trust", default="agent",
                        choices=["executive", "agent", "untrusted"])
    de_cmd.set_defaults(handler=command_distill_episode)

    re_cmd = sub.add_parser("refresh-entity", help="Acumula uma menção em página de entidade: interação + last_interaction + aliases (04 §4.3)")
    re_cmd.add_argument("--acervo-root", help="Raiz do Acervo")
    re_cmd.add_argument("--path", required=True, help="Caminho do arquivo da entidade")
    re_cmd.add_argument("--note", required=True, help="O que foi a interação (uma linha)")
    re_cmd.add_argument("--date", help="Data da interação YYYY-MM-DD (default: hoje UTC)")
    re_cmd.add_argument("--add-aliases", dest="add_aliases", help="Novos aliases (separados por vírgula)")
    re_cmd.set_defaults(handler=command_refresh_entity)

    sweep_cmd = sub.add_parser("sweep-intentions", help="Varredura de expiração de intenções vencidas (08 §6). Read-only sem --apply")
    sweep_cmd.add_argument("--acervo-root", help="Raiz do Acervo")
    sweep_cmd.add_argument("--today", help="Data de corte YYYY-MM-DD (default: hoje UTC)")
    sweep_cmd.add_argument("--apply", action="store_true", help="Efetiva a expiração (sem isso, apenas relata)")
    sweep_cmd.set_defaults(handler=command_sweep_intentions)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        payload = args.handler(args)
    except Exception as exc:
        print_json({"ok": False, "error": str(exc)})
        return 1
    print_json(payload)
    return 0 if payload.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
