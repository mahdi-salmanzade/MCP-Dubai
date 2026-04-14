"""
Arabic and abbreviation aliases for ToolDiscovery.

Each equivalence set is a tuple of strings that are treated as the same
token for BM25 indexing. When any member of a set matches in a tool's
searchable text or in a recommend query, all members of the set are
added to the token stream so the BM25 score rises for that tool.

This is the lightest possible bilingualization of MCP-Dubai: no ML, no
runtime translation, no language detection. Just a curated map of the
Dubai terms founders actually type, in the scripts they actually type
them in.

Primary use cases:

- A founder types `تأشيرة ذهبية` and `recommend_tools` surfaces
  `golden_visa_check` (because its English tags include "golden visa").
- A founder types `جميرا مدارس` and `recommend_tools` surfaces
  `khda_search_school` (whose tags include "school" and area names).
- Abbreviations like `DIFC`, `JAFZA`, `RTA`, `KHDA` are spelled out
  into their full names so queries using either form match.

Keep this file short. Every alias set is a judgment call about what
Dubai founders actually say, not a linguistic exercise.
"""

from __future__ import annotations

import re
from typing import Final

# Each tuple is a mutual equivalence set. Order within a set does not
# matter. The comment before each group explains the intent.
EQUIVALENCE_SETS: Final[tuple[tuple[str, ...], ...]] = (
    # --- Dubai areas and neighbourhoods ----------------------------------
    ("jumeirah", "jumeira", "جميرا"),
    ("deira", "ديرة"),
    ("al barsha", "barsha", "البرشاء"),
    ("business bay", "الخليج التجاري"),
    ("dubai marina", "marina", "مارينا"),
    ("downtown dubai", "downtown", "وسط المدينة"),
    ("jlt", "jumeirah lakes towers", "أبراج بحيرات الجميرا"),
    ("silicon oasis", "dso", "واحة دبي للسيليكون"),
    ("dubai south", "dwc", "دبي الجنوب"),
    # --- Free zones and authorities --------------------------------------
    (
        "difc",
        "dubai international financial centre",
        "مركز دبي المالي العالمي",
    ),
    (
        "dmcc",
        "dubai multi commodities centre",
        "مركز دبي للسلع المتعددة",
    ),
    ("jafza", "jebel ali free zone", "المنطقة الحرة لجبل علي", "جافزا"),
    ("ifza", "international free zone authority"),
    ("dafza", "dubai airport free zone", "المنطقة الحرة بمطار دبي"),
    ("meydan", "meydan free zone", "ميدان"),
    ("tecom", "tecom group"),
    ("dhcc", "dubai healthcare city", "مدينة دبي الطبية"),
    # --- Dubai / UAE government bodies ----------------------------------
    (
        "ded",
        "det",
        "moet",
        "department of economy and tourism",
        "دائرة الاقتصاد والسياحة",
    ),
    (
        "rta",
        "roads and transport authority",
        "هيئة الطرق والمواصلات",
    ),
    ("dha", "dubai health authority", "هيئة الصحة بدبي"),
    (
        "dewa",
        "dubai electricity and water authority",
        "هيئة كهرباء ومياه دبي",
    ),
    (
        "khda",
        "knowledge and human development authority",
        "هيئة المعرفة",
    ),
    (
        "dld",
        "dubai land department",
        "دائرة الأراضي والأملاك",
    ),
    (
        "rera",
        "real estate regulatory authority",
        "مؤسسة التنظيم العقاري",
    ),
    ("cbuae", "central bank of uae", "المصرف المركزي"),
    ("mohre", "ministry of human resources", "وزارة الموارد البشرية"),
    ("icp", "federal authority for identity", "الهوية والجنسية"),
    ("fta", "federal tax authority", "الهيئة الاتحادية للضرائب"),
    ("dm", "dubai municipality", "بلدية دبي"),
    # --- Business and legal terms ---------------------------------------
    ("visa", "تأشيرة"),
    ("residence", "residency", "إقامة"),
    ("license", "licence", "رخصة"),
    ("setup", "incorporation", "تأسيس"),
    ("tax", "ضريبة"),
    ("vat", "value added tax", "ضريبة القيمة المضافة"),
    ("corporate tax", "ct", "ضريبة الشركات"),
    ("company", "business", "شركة"),
    ("free zone", "freezone", "منطقة حرة"),
    ("offshore", "أوفشور"),
    ("golden visa", "تأشيرة ذهبية", "الإقامة الذهبية"),
    ("green visa", "تأشيرة خضراء"),
    ("real estate", "property", "عقارات", "عقار"),
    ("banking", "bank account", "حساب بنكي", "مصرف"),
    ("aml", "anti money laundering", "مكافحة غسل الأموال"),
    ("ubo", "beneficial owner", "المالك المستفيد"),
    ("esr", "economic substance", "الجوهر الاقتصادي"),
    ("pdpl", "data protection", "حماية البيانات"),
    # --- Civic and lifestyle terms --------------------------------------
    ("school", "schools", "مدرسة", "مدارس"),
    ("prayer", "salah", "salat", "صلاة"),
    ("qibla", "قبلة"),
    ("quran", "قرآن"),
    ("holiday", "holidays", "عطلة", "عطلات", "إجازة"),
    ("weather", "طقس", "forecast"),
    ("air quality", "aqi", "جودة الهواء"),
    ("metro", "مترو"),
    ("bus", "حافلة", "باص"),
    ("salik", "toll", "رسوم الطريق"),
    ("nol", "nol card", "بطاقة نول"),
)


def _is_ascii(s: str) -> bool:
    return all(ord(c) < 128 for c in s)


def _compile_lookups() -> tuple[
    list[tuple[re.Pattern[str], int]],
    list[tuple[str, int]],
]:
    """
    Pre-compile the match rules.

    Returns:
        (ascii_rules, unicode_rules) where
        - ascii_rules is a list of (compiled word-boundary regex, set_index)
        - unicode_rules is a list of (lowercased needle, set_index)

    ASCII terms use word boundaries so `rta` does not match `start`.
    Non-ASCII (Arabic) terms use direct substring matching because
    `\\b` does not behave the same way on Arabic characters.
    """
    ascii_rules: list[tuple[re.Pattern[str], int]] = []
    unicode_rules: list[tuple[str, int]] = []
    for idx, members in enumerate(EQUIVALENCE_SETS):
        for member in members:
            needle = member.lower()
            if _is_ascii(needle):
                pattern = re.compile(rf"\b{re.escape(needle)}\b")
                ascii_rules.append((pattern, idx))
            else:
                unicode_rules.append((needle, idx))
    return ascii_rules, unicode_rules


_ASCII_RULES, _UNICODE_RULES = _compile_lookups()


def expand_text(text: str) -> str:
    """
    Append alias equivalents of any match in `text` to a flat token stream.

    The returned string is `text` plus a space-joined list of every
    equivalent term from every equivalence set that matched. Each set
    is only expanded once per call, so common terms do not inflate the
    token stream out of proportion.
    """
    if not text:
        return text

    lower = text.lower()
    matched_sets: set[int] = set()

    for pattern, idx in _ASCII_RULES:
        if idx in matched_sets:
            continue
        if pattern.search(lower):
            matched_sets.add(idx)

    for needle, idx in _UNICODE_RULES:
        if idx in matched_sets:
            continue
        if needle in lower:
            matched_sets.add(idx)

    if not matched_sets:
        return text

    additions: list[str] = []
    for idx in matched_sets:
        for member in EQUIVALENCE_SETS[idx]:
            additions.append(member.lower())
    return text + " " + " ".join(additions)


def expand_tokens(tokens: list[str]) -> list[str]:
    """
    Token-level expansion used when a caller has already tokenized the
    input. Applies `expand_text` to the joined string and returns the
    resulting token list (split on whitespace).
    """
    if not tokens:
        return tokens
    joined = " ".join(tokens)
    expanded = expand_text(joined)
    return expanded.lower().split()
