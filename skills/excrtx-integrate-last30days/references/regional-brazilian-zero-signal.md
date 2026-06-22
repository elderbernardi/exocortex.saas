# Regional Brazilian Company — Zero Signal Case Study

**Session:** Zaffari (Companhia Zaffari, Brazilian supermarket chain, south region)
**Date:** 2026-06-17
**Engine output:** 3 Reddit threads, zero mentioning the company. YouTube found 8 videos, 0 transcripts.

## What was attempted

Full last30days protocol was followed:

- **Step 0.45:** Passed — "companhia Zaffari" is a named entity, not a keyword trap.
- **Step 0.5:** Resolved `--x-handle=zaffari` (via NotebookLM subagents). Confirmed official handle @zaffari.
- **Step 0.55:** Resolved subreddits: `portoalegre,riograndedosul,curitiba,brasil`. r/portoalegre is the most active community for Zaffari discussions historically (6 threads found in pre-resolution), but zero posts within the 30-day window.
- **Step 0.75:** Generated 3-subquery plan (primary, consumidores, expansao) with search queries in Portuguese.
- **Engine execution:** 55.5s. RedditKeyless scored 155 cards, ranked to 3, all false positives (political posts from r/brasil that matched keywords but never mentioned Zaffari). YouTube transcripts all failed (no captions on any video). X not configured. TikTok/Instagram not configured (no ScrapeCreators key).

## What the engine returned

```
Research quality: 4/5 core sources. Missing: X/Twitter.
Evidence is thin for this topic.
Top evidence is highly concentrated in one source.
- Total evidence: 3 items across 1 source (Reddit)
- All 3 items flagged: "Why: No mention of Zaffari"
```

The three "evidence clusters" were:
1. Political post about Pix/fakenews (r/brasil, 6,563 pts)
2. Ultra-processed food discussion (r/brasil, 4,149 pts)
3. Political commentary about "patriotas" (r/brasil, 3,148 pts)

None were about Zaffari. This is a **false-positive cluster**: the engine's keyword matching returned high-engagement posts that happened to collide on Brazilian Portuguese tokens but were completely unrelated to the target company.

## Synthesis pattern

The correct synthesis for this scenario (per Procedure §4):

1. **Acknowledge the gap explicitly:** "A Zaffari é essencialmente invisível nas plataformas sociais internacionais nos últimos 30 dias."
2. **Explain WHY, not just THAT:** Regional supermarket chain, conversation lives on platforms the engine doesn't cover (Instagram, TikTok, WhatsApp groups, local press).
3. **Show what WAS tried:** Mention the subreddits searched, the handle resolved, the plan generated — demonstrate effort.
4. **Offer concrete next steps:** Enable X (AUTH_TOKEN or XAI_API_KEY), get ScrapeCreators key for TikTok/Instagram, supplement with Google News RSS (per references/google-news-rss-fallback.md).

## Anti-pattern: synthesizing from false-positive evidence

Do NOT attempt to build a "What I learned:" narrative from engine output when all evidence clusters carry `Why: No mention of [topic]`. The correct action is to say "there's nothing to synthesize" and route to the fallback pipeline. Building prose from zero-relevance items fabricates insight from noise.

## Root cause classification

This is a **"low social surface area"** topic — the company exists and operates daily, but its conversation ecosystem (local Instagram, regional WhatsApp groups, GaúchaZH/Zero Hora news) is orthogonal to the engine's source set (English-centric social media + Reddit in Portuguese dominated by national politics).

This pattern repeats for:
- Regional Brazilian companies (supermarkets, construction firms, agribusiness, local manufacturers)
- B2B industrial companies anywhere
- Companies whose primary audience is non-English-speaking and non-Reddit-using
