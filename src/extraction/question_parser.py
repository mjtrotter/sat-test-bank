"""
Parse MATHCOUNTS question PDFs by round type.
"""
import re
from typing import Dict, List
import fitz

BLANK_RE = re.compile(r"^(\d+)\.$")

def _find_problem_markers(words: List[dict], max_num: int) -> List[dict]:
    markers = []
    seen_nums = set()
    for w in words:
        m = BLANK_RE.match(w["text"])
        if not m:
            continue
        num = int(m.group(1))
        if num < 1 or num > max_num:
            continue
        def _is_blank_word(t: str) -> bool:
            return "_" in t or "�" in t or (len(t) > 8 and t == t[0] * len(t))

        has_blank = any(
            _is_blank_word(other["text"])
            and abs(other["y"] - w["y"]) < 5
            and 0 < (other["x"] - w["x"]) < 80
            for other in words
        )
        if has_blank and num not in seen_nums:
            seen_nums.add(num)
            markers.append({"num": num, "x": w["x"], "y": w["y"]})
    return sorted(markers, key=lambda m: m["y"])

# Original code omitted for brevity
