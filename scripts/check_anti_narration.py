"""F5 slice A — detecta narração do método fable nas respostas do agente (promove o grep C0 do F3-GATE-PROOF)."""
import json, re, sys

# 7 fases fable em PT-BR (acentuadas) + tokens EN — narração é declarar a fase em prosa em vez de escrever conduct.jsonl.
_PATTERNS = [
    r"Classifica[çc][ãa]o\s*:", r"Defini[çc][ãa]o de pronto\s*:", r"Evid[êe]ncia\s*:",
    r"Decis[ãa]o\s*:", r"A[çc][ãa]o\s*:", r"Verifica[çc][ãa]o\s*:", r"Relat[óo]rio\s*:",
    r"^\s*Fase\s*:", r"\bClassification\s*:", r"\bDefinition of done\s*:",
]
_RE = re.compile("|".join(_PATTERNS), re.IGNORECASE | re.MULTILINE)

def check_narration(messages: list) -> list:
    """Retorna os trechos narrados encontrados nas respostas do agente (role=assistant). Vazio = limpo."""
    hits = []
    for m in messages:
        if m.get("role") != "assistant":
            continue
        for mt in _RE.finditer(m.get("content", "") or ""):
            hits.append(mt.group(0).strip())
    return hits

def main(argv):
    if len(argv) != 2:
        print("uso: check_anti_narration.py <session.json>", file=sys.stderr); return 2
    data = json.loads(open(argv[1], encoding="utf-8").read())
    hits = check_narration(data.get("messages", []))
    if hits:
        print("NARRAÇÃO DETECTADA:", hits, file=sys.stderr); return 1
    print("OK — sem narração do método"); return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
