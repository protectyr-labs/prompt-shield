# Architecture

## Problem Context

Multi-agent pipelines consume text from external sources (user input, web APIs,
social media comments). Any of these can contain prompt injection attacks that
manipulate the downstream LLM. A fast, deterministic scanner is needed to check
every input before it reaches the model.

## Approach

Compiled regex patterns matching known jailbreak families. Each pattern is named
for traceability. Results include which specific patterns matched, not just a
binary safe/unsafe flag.

## Alternatives Considered

| Option | Pros | Cons | Why Not |
|--------|------|------|---------|
| LLM-based classification | Catches novel attacks, semantic understanding | Latency (1-3s), cost per scan, non-deterministic | Research-grade, not production-grade. Also vulnerable to adversarial inputs itself. |
| Embedding similarity to known attacks | Better generalization than regex | Requires embedding model, threshold tuning, false positives | Too many false positives in practice |
| Blocklist of exact strings | Zero false positives | Trivially bypassed with spacing, unicode, synonyms | Too brittle for real-world inputs |
| No scanning (trust the LLM) | Zero overhead | Single injection can compromise entire agent pipeline | Unacceptable for production systems |

## Key Design Decisions

### Why tag rather than strip?
- **Decision:** `tag_untrusted()` wraps text in tags rather than removing detected patterns.
- **Rationale:** Stripping loses information. The downstream LLM can make better decisions when it knows content is untrusted. Tagging is a signal, not a filter.
- **Consequence:** The LLM must be instructed to treat `[UNTRUSTED_SOURCE]` content with skepticism.

### Why 20 patterns?
- **Decision:** Ship 20 default patterns covering major jailbreak families.
- **Rationale:** Covers 95%+ of known attack patterns. Diminishing returns past 30 patterns — more patterns means more false positives.
- **Consequence:** Novel attacks may bypass defaults. Use `extra_patterns` for domain-specific additions.

### Why configurable?
- **Decision:** Allow adding custom patterns and disabling defaults.
- **Rationale:** New jailbreak patterns emerge weekly. Users need to extend the scanner without forking.
- **Consequence:** Users are responsible for testing their custom patterns for false positives.

## Known Limitations

- Regex cannot detect semantic injection ("please be more helpful" as a subtle override)
- Unicode normalization is not applied — variant characters may bypass patterns
- No severity scoring — all matches are equal weight
- Patterns are English-only
