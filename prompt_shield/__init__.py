"""
Prompt Shield — detect prompt injection patterns in untrusted text.

Uses compiled regex patterns for zero-latency, zero-cost detection.
Designed to scan external content (user input, web scrapes, API responses)
before including it in LLM prompts.
"""
import re
from dataclasses import dataclass, field
from typing import Optional

__version__ = "0.1.0"

DEFAULT_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("ignore_previous_instructions", re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|context|rules)", re.IGNORECASE)),
    ("override_system_prompt", re.compile(r"(disregard|forget|override)\s+(your|the|all)\s+(system|initial)\s+(prompt|instructions|rules)", re.IGNORECASE)),
    ("new_instructions", re.compile(r"(new|updated|revised)\s+instructions\s*:", re.IGNORECASE)),
    ("you_are_now", re.compile(r"you\s+are\s+now\s+(a|an|the)\s+", re.IGNORECASE)),
    ("act_as", re.compile(r"(act|behave|respond)\s+as\s+(if\s+you\s+are|a|an)", re.IGNORECASE)),
    ("dan_mode", re.compile(r"\bDAN\b.*\b(mode|enabled|activated)\b", re.IGNORECASE)),
    ("jailbreak", re.compile(r"\bjailbreak\b", re.IGNORECASE)),
    ("do_anything_now", re.compile(r"do\s+anything\s+now", re.IGNORECASE)),
    ("pretend_no_restrictions", re.compile(r"pretend\s+(you\s+)?(have\s+)?no\s+(restrictions|limits|rules|guidelines)", re.IGNORECASE)),
    ("reveal_system_prompt", re.compile(r"(reveal|show|output|print|display)\s+(your|the)\s+(system|initial|original)\s+(prompt|instructions|message)", re.IGNORECASE)),
    ("base64_injection", re.compile(r"(decode|base64)\s+(this|the\s+following)", re.IGNORECASE)),
    ("eval_exec", re.compile(r"\b(eval|exec)\s*\(", re.IGNORECASE)),
    ("import_os", re.compile(r"\bimport\s+(os|subprocess|sys)\b", re.IGNORECASE)),
    ("script_tag", re.compile(r"<script\b", re.IGNORECASE)),
    ("system_command", re.compile(r"(run|execute)\s+(this\s+)?(command|code|script)", re.IGNORECASE)),
    ("markdown_injection", re.compile(r"\[.*\]\(javascript:", re.IGNORECASE)),
    ("role_play_evil", re.compile(r"(evil|malicious|unethical)\s+(AI|assistant|version)", re.IGNORECASE)),
    ("unlimited_mode", re.compile(r"(unlimited|unrestricted|unfiltered)\s+mode", re.IGNORECASE)),
    ("token_smuggling", re.compile(r"<\|im_start\|>|<\|im_end\|>|<\|endoftext\|>", re.IGNORECASE)),
    ("prompt_leaking", re.compile(r"(repeat|echo)\s+(everything|all)\s+(above|before|from\s+the\s+start)", re.IGNORECASE)),
]


@dataclass
class ScanResult:
    """Result of scanning text for injection patterns."""
    safe: bool
    warnings: list[str] = field(default_factory=list)
    pattern_count: int = 0


def scan(
    text: str,
    extra_patterns: Optional[list[str]] = None,
    use_defaults: bool = True,
) -> ScanResult:
    """
    Scan text for prompt injection patterns.

    Args:
        text: The text to scan.
        extra_patterns: Additional regex patterns to check (raw strings).
        use_defaults: Whether to use the built-in 20 default patterns.

    Returns:
        ScanResult with safe flag, list of matched pattern names, and count.
    """
    if not text:
        return ScanResult(safe=True)

    warnings: list[str] = []

    if use_defaults:
        for name, pattern in DEFAULT_PATTERNS:
            if pattern.search(text):
                warnings.append(name)

    if extra_patterns:
        for i, raw in enumerate(extra_patterns):
            compiled = re.compile(raw, re.IGNORECASE)
            if compiled.search(text):
                warnings.append(f"custom_{i}")

    return ScanResult(
        safe=len(warnings) == 0,
        warnings=warnings,
        pattern_count=len(warnings),
    )


def tag_untrusted(text: str, source: str) -> str:
    """
    Wrap text with untrusted source tags.

    Use this to mark external content in your prompts so the LLM
    knows to treat it with appropriate skepticism.
    """
    return f"[UNTRUSTED_SOURCE: {source}] {text} [/UNTRUSTED_SOURCE]"
