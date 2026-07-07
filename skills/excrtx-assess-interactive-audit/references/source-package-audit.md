# Source package audit — interactive-audit v2026.07.07

## Source inventory

```text
interactive-audit/
├── SKILL.md
├── PROMPT_TEMPLATE.md
├── README.md
├── CHANGELOG.md
└── evals/
    ├── EVALS.md
    ├── RESULTS.md
    └── gates.sh
```

## Original gate result

`evals/gates.sh` returned `G0 PASS` on 2026-07-07 in this environment.

## Exocórtex adaptation decision

Preserve:

- owner-in-the-loop audit protocol;
- two-persona model;
- finding-time confirmation;
- evidence discipline;
- required coordination files;
- issue backlog and GO/NO-GO deliverables;
- prior-art / successor audit behavior.

Change:

- rename to `excrtx-assess-interactive-audit`;
- add Exocórtex/Hermes canonical frontmatter;
- add Vetor classification;
- add Draft-First and mutation policy in Exocórtex terms;
- add Acervo promotion boundary;
- require `excrtx-quality-skilljudge` for skill audits;
- move the prompt into `references/prompt-template.md`.
