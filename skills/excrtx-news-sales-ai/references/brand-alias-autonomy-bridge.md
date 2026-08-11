# Brand alias bridge for autonomous micro-news matching

## When this matters

Use this pattern when the deterministic micro-news pipeline finds a real retail-network signal, but the roster only carries legal names or channel-labeled fantasy names such as:
- `SUPERMERCADO BRUDA LTDA`
- `CD BRUDA`
- `COMERCIAL ZAFFARI`
- `A. ANGELONI E CIA. LTDA`

In these cases, the public signal often names only the retail brand (`Bruda`, `Zaffari`, `Angeloni`). Without a brand-level alias, the matcher can fall back to `matched_probable` or `needs_review` even when the network link is commercially obvious.

## Durable fix

Derive `brand_aliases` during roster freeze, not during editorial review.

Rule:
1. Start from `nome_fantasia` and `nome`.
2. Normalize accents and punctuation to lowercase ASCII tokens.
3. Remove legal/channel stopwords such as `cd`, `supermercado`, `comercial`, `grupo`, `ltda`, `cia`, `distribuidora`, `industria`.
4. Require the remaining meaningful token set to be the same in legal name and fantasy name; divergent surfaces do not produce a strong brand alias.
5. Preserve a distinct multiword brand as one phrase (`mais papeis`), not as broad individual tokens.
6. Reject ambiguous single-token survivors such as `ideal`, `porto`, `ilha`, `brasil`, `paulo`, `uniao`, `geracao`, `produtos`.
7. Persist accepted aliases in both:
   - `brand_aliases[]` (explicit strong brand evidence)
   - `aliases[]` (for broad traceability)

Example:
- `SUPERMERCADO BRUDA LTDA` + `CD BRUDA` -> `brand_aliases: ["bruda"]`
- `SUPERMERCADO PORTAL LTDA` + `SUPERMERCADO FRONTAL` -> no strong brand alias

## Matcher policy

Treat `brand_aliases` as stronger than ordinary alias hits only under title-prefix evidence.

Recommended scoring behavior:
- require the normalized title to start with the brand alias, or with an allowed commercial prefix followed by it (`rede`, `grupo`, `supermercado`, `comercial`, `atacado`, `mercado`);
- use word-boundary matching; never substring matching (`ilha` must not match `bilhão`);
- exclude source name and URL domain from semantic identity matching;
- only then promote to exact-strength evidence (`matched_exact`);
- still preserve the normal active/retired lookup guard by `(url_normalized, cliente_id)` before publication.

## Why this belongs before the LLM

This is not editorial judgment. It is deterministic identity resolution.

If the network identity is already recoverable from the roster itself, capture it in the frozen manifest so the pipeline can:
- match deterministically
- dedupe deterministically
- hit the exact lookup guard deterministically
- reserve the low-cost model for the final editorial classification only

## Verified session outcome

After adding `brand_aliases` and teaching the matcher to score them as exact-strength evidence:
- the Bruda signal no longer required manual promotion to the editorial boundary
- it moved directly into `matched_exact`
- after publication, rerunning the same signal produced `skip_active`, proving the autonomous path now sees the item correctly before the LLM

## Scope guard

Do not derive brand aliases aggressively from every fantasy name.

This technique is for distinct network brands. If the surviving token is generic, ambiguous, or person-like, blacklist it and keep the item in review rather than widening false positives across the whole base.
