---
name: excrtx-memory-mvexport
description: Export a microverso as a portable, self-contained .mvpkg package (manifest excrtx/v1,
  bundled skills, dependency pins, integrations) for sharing, migration, or backup.
version: 1.0.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - memory
    - microverso
    - export
    - package
    - portability
    related_skills:
    - excrtx-memory-mvinstall
    - excrtx-memory-manager
    calibration:
    - feature_id: EX-58
      calibration_prompt: Você empacota um microverso existente num pacote .mvpkg portátil e autossuficiente
        (Docker-like) com manifesto excrtx/v1, skills embutidas, pins de dependências e configs de integração.
        Gera microverso.yaml automaticamente, valida o gate OKF, aplica clean-portable (remove estado de
        runtime) e produz MANIFEST.sum para integridade.
      test_prompt: Exporte o microverso 'estudio-criativo' como um tarball portátil para /tmp.
      acceptance_criteria: '1. Gera/atualiza microverso.yaml (excrtx/v1) com detecção de dependências

        2. Roda o gate OKF (validate_frontmatter) e aborta se houver erro

        3. Aplica clean-portable: exclui quarantine/_archive/raw, remove last_accessed_at, descarta deprecated

        4. Embute skills excrtx-* referenciadas e gera MANIFEST.sum'
      remediation_tip: 'FALHA: export sem gate OKF ou sem manifesto válido. Rode
        microverso_package.py que valida o manifesto (excrtx/v1) e o frontmatter OKF antes de empacotar.'
compiled_rules: |
  - Export de microverso é via acervo/global/tools/microverso_package.py — nunca cópia manual de diretório.
  - Sempre valide o gate OKF antes de empacotar; aborte o export se algum .md falhar.
  - Pacote é clean-portable: remova last_accessed_at, exclua .quarantine/_archive/raw, descarte deprecated.
  - Segredos nunca entram no pacote — apenas nomes de env vars em env.example.
---
# Microverso Package Exporter

> A contraparte do mvinstall: transforma um microverso vivo num pacote portátil e instalável.

## When to Use

Ativar quando:
- Executivo pede "exporte/empacote o microverso X", "quero compartilhar/migrar o microverso Y"
- Backup portátil de um microverso
- Comando `/xc mvexport <slug>` executado

**Don't use for:** Criar microverso novo (use `excrtx-memory-newmicro`). Instalar pacote (use `excrtx-memory-mvinstall`).

## Procedure

Executar a ferramenta determinística:

```bash
python3 $ACERVO/global/tools/microverso_package.py --microverso <slug> --out <dir> --tar
```

Etapas (automatizadas pela ferramenta):
1. **Manifesto** — carrega `microverso.yaml` existente (base curada) e auto-preenche `tree`, `compat`, `requires.system`, `provenance`; detecta skills `excrtx-*` referenciadas e imports Python.
2. **Validação** — valida o manifesto contra `excrtx/v1` (`microverso_schema.py`).
3. **Gate OKF** — roda `validate_frontmatter.py` na fonte; **aborta** se houver erro.
4. **Cópia clean-portable** — exclui `.quarantine/`,`_archive/`,`raw/`(salvo `--include-raw`),`__pycache__`,`.git`; remove `last_accessed_at`; descarta `deprecated: true` (salvo `--include-deprecated`).
5. **Embute** skills referenciadas (`--bundle-skills auto|all|none`), `deps/`, `integrations/mcps.yaml`, `env.example`, `INSTALL.md`.
6. **Integridade** — gera `MANIFEST.sum`; saída em diretório ou `.tar.gz` (`--tar`).

Manifesto gerado é **revisável** (Draft-First) antes de distribuir.

## Pitfalls

- Se o gate OKF falhar, corrija o frontmatter na fonte antes de re-exportar.
- `last_accessed_at` é removido (estado por instância); demais campos de frontmatter são preservados.
- Skills referenciadas mas não encontradas são apenas **declaradas** (não embutidas) — reportadas como WARN.
- Pins de dependência vêm do `microverso.yaml` curado; módulos detectados nos scripts são só sugestão (revisar).

## Verification

- [ ] Manifesto `microverso.yaml` gerado e válido (`excrtx/v1`)
- [ ] Gate OKF passou (0 erros) antes do empacotamento
- [ ] Clean-portable aplicado (exclusões + `last_accessed_at` removido)
- [ ] Skills embutidas conforme `--bundle-skills`
- [ ] `MANIFEST.sum` gerado; round-trip com `microverso_install.py` instala sem intervenção
