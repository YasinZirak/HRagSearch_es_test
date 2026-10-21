"""Persian text normalization.

Use the SAME function on documents (before indexing) and on user queries
(before searching), otherwise matches fail on invisible differences.
"""
import re

# Arabic letters -> Persian letters
_LETTER_MAP = str.maketrans({
    "ي": "ی",   # Arabic yeh
    "ى": "ی",   # alef maksura
    "ك": "ک",   # Arabic kaf
    "ة": "ه",   # teh marbuta
})

# Persian (۰-۹) and Arabic-Indic (٠-٩) digits -> ASCII digits
_DIGIT_MAP = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
    "01234567890123456789",
)

_DIACRITICS = re.compile("[\u064B-\u0652\u0640]")   # harakat + tatweel
_ZWNJ = "\u200c"                                     # half-space
_THOUSANDS = re.compile(r"(?<=\d)[,٬](?=\d{3})")     # 50,000 / 50٬000 -> 50000
_SPACES = re.compile(r"\s+")


def normalize_fa(text: str) -> str:
    """Normalize Persian text for search and embeddings (not for display)."""
    if not text:
        return ""
    text = text.translate(_LETTER_MAP)
    text = text.translate(_DIGIT_MAP)
    text = _DIACRITICS.sub("", text)
    text = text.replace(_ZWNJ, " ")        # می‌خواهم -> می خواهم
    text = _THOUSANDS.sub("", text)
    text = _SPACES.sub(" ", text).strip()
    return text.lower()                    # lowercases Latin (Honda -> honda)


def build_search_text(bike: dict) -> str:
    """One searchable string per bike: both brand spellings + model + text."""
    parts = [
        bike["brand"], bike["brand_en"], bike["model"],
        bike["category_fa"], bike["description"],
    ]
    return normalize_fa(" ".join(parts))
