#!/usr/bin/env python3
"""
canvas_schema.py — Canvas JSON Schema Definition

Defines the structured Canvas output schema for validation.
Used by auditor_canvas_validator.py to check Canvas block emissions.
"""

CANVAS_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Exocórtex Canvas v0.5",
    "description": "Structured intent analysis for complex executive inputs",
    "type": "object",
    "required": ["focus", "vetor", "intent_type"],
    "properties": {
        "focus": {
            "type": "string",
            "minLength": 3,
            "description": "Core topic or objective extracted from the input",
        },
        "vetor": {
            "type": "string",
            "enum": ["execucao", "evolucao", "manutencao", "ambiguo"],
            "description": "Classified operational vector",
        },
        "intent_type": {
            "type": "string",
            "enum": ["explorar", "decidir", "produzir", "revisar", "manter",
                     "publicar", "ingestao", "outro"],
            "description": "Type of intent behind the input",
        },
        "macroverso_status": {
            "type": "string",
            "enum": ["resolved", "partial", "placeholder", "missing"],
            "description": "State of the Macroverso for this session",
        },
        "microverso_primary": {
            "type": ["string", "null"],
            "description": "Primary microverso anchoring this task",
        },
        "gaps": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Information gaps detected in the input",
        },
        "urgency": {
            "type": "string",
            "enum": ["alta", "media", "baixa"],
            "description": "Urgency level of the request",
        },
        "shape": {
            "type": "string",
            "enum": ["pergunta", "plano-primeiro", "tarefa"],
            "description": "Shape of the ask (fable-method): question, plan-first or task",
        },
        "done_criteria": {
            "type": "string",
            "description": "What 'done' looks like for this task, in one sentence",
        },
        "verification": {
            "type": "string",
            "description": "Named verification proving done_criteria (observable check)",
        },
    },
    "additionalProperties": False,
}


def get_schema():
    """Return the Canvas schema dict."""
    return CANVAS_SCHEMA


if __name__ == "__main__":
    import json
    print(json.dumps(CANVAS_SCHEMA, indent=2, ensure_ascii=False))
