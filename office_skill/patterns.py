"""Mechanical tells a gate can see without looking at the page."""

import re

# Case-insensitive fragments that should never survive into a deliverable.
PLACEHOLDER_RE = re.compile(
    r"lorem ipsum|待填写|待补充|此处插入|\[insert[^\]]*\]|\[placeholder\]|【待补】|as an ai|i am an ai|作为人工智能",
    re.IGNORECASE,
)
TOKEN_RE = re.compile(r"\b(TODO|TBD|FIXME|XXX+)\b")
EMOJI_RE = re.compile("[\U0001f000-\U0001faff\U00002600-\U000027bf\U0001f1e6-\U0001f1ff]")

# Exact slide titles that could sit on any deck. Compared after casefold and strip.
GENERIC_TITLES = {
    "overview",
    "summary",
    "conclusion",
    "key takeaways",
    "key insights",
    "agenda",
    "thank you",
    "thanks",
    "概述",
    "总结",
    "关键要点",
    "核心洞察",
    "谢谢",
    "目录",
}


def text_problems(text: str) -> list[str]:
    problems: list[str] = []
    if not text:
        return problems
    if PLACEHOLDER_RE.search(text):
        problems.append("placeholder or boilerplate phrase")
    if TOKEN_RE.search(text):
        problems.append("unresolved token (TODO/TBD/FIXME/XXX)")
    if EMOJI_RE.search(text):
        problems.append("emoji")
    return problems
