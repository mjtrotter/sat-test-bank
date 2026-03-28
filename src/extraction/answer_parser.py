"""
Parse MATHCOUNTS answer key PDFs using word-level spatial analysis.

Uses PyMuPDF's word extraction for fine-grained positioning, then matches
answer values to numbered blanks by proximity. Handles fractions (stacked
numerator/denominator) and multi-part answers like coordinates.
"""

import re
from typing import Dict, List, Optional, Tuple

import fitz


EXPECTED_COUNTS = {"sprint": 30, "target": 8, "team": 10}
SECTION_RE = re.compile(r"(Sprint|Target|Team)\s+Round", re.IGNORECASE)
SKIP_SECTION_RE = re.compile(r"(Countdown|Tiebreaker)\s+Round", re.IGNORECASE)

UNIT_WORDS = {
    "hours", "hour", "minutes", "minute", "seconds", "second", "days", "day",
    "cm", "cm2", "cm3", "in", "ft", "m", "km", "miles", "mile", "feet",
    "units", "unit", "units2", "units3", "lengths", "length",
    "dollars", "dollar", "cents", "cent",
    "degrees", "degree", "percent",
    "ounces", "ounce", "cups", "cup", "gallons", "gallon",
    "pairs", "pair", "integers", "integer", "triangles", "triangle",
    "faces", "face", "families", "family", "ways", "students", "student",
    "games", "people", "outcomes", "bars", "segments", "disks",
    "mi/h", "ft/s",
}

NOISE_WORDS = {
    "copyright", "mathcounts", "mathcounts,", "inc.", "all", "rights",
    "reserved.", "chapter", "state", "national", "competition",
    "answer", "key", "round", "sprint", "target", "team",
    "note", "coordinators", "tiebreaker", "sponsors", "founding",
    "founded", "do", "not", "begin", "until", "instructed",
}


def _get_words(page: fitz.Page) -> List[dict]:
    """Extract words with positions. Returns list of {text, x, y, x2, y2}."""
    raw = page.get_text("words")
    words = []
    for x0, y0, x1, y1, text, bno, lno, wno in raw:
        words.append({"text": text.strip(), "x": x0, "y": y0, "x2": x1, "y2": y1})
    return words


def _find_blanks(words: List[dict], max_num: int) -> List[dict]:
    """Find numbered blank entries (e.g., '1.' followed by '____')."""
    blanks = []
    for i, w in enumerate(words):
        m = re.match(r"^(\d+)\.$", w["text"])
        if not m:
            continue
        num = int(m.group(1))
        if num < 1 or num > max_num:
            continue
        # Check if next word is underscores (confirming it's a blank, not a problem number)
        if i + 1 < len(words):
            next_w = words[i + 1]
            if "_" in next_w["text"] and abs(next_w["y"] - w["y"]) < 5:
                blanks.append({"num": num, "x": w["x"], "y": w["y"]})
    return blanks


def _find_answer_candidates(words: List[dict]) -> List[dict]:
    """Find words that could be answer values (not blanks, units, or noise)."""
    candidates = []
    for w in words:
        text = w["text"].strip()
        if not text:
            continue
        if "_" in text:
            continue
        low = text.lower().rstrip(".,;:")
        if low in NOISE_WORDS or low in UNIT_WORDS:
            continue
        if text in ("$", "(", ")", ",", "or"):
            continue
        # Keep numbers, fractions, negative numbers, expressions
        candidates.append(w)
    return candidates


def _match_answers(
    blanks: List[dict], candidates: List[dict]
) -> Dict[int, str]:
    """
    Match each blank to its answer value(s) by spatial proximity.

    Answer values sit above the blank line, offset ~35px to the right.
    Fractions have numerator and denominator stacked vertically at same x.
    """
    answers = {}
    used = set()

    for blank in blanks:
        # Find all candidate words in the answer zone for this blank
        zone_words = []
        for i, c in enumerate(candidates):
            if i in used:
                continue
            dx = c["x"] - blank["x"]
            dy = blank["y"] - c["y"]  # positive = candidate above blank

            # Answer zone: 15-160px right, 0-25px above (or 5px below)
            if 15 <= dx <= 160 and -8 <= dy <= 30:
                zone_words.append((i, c, dx, dy))

        if not zone_words:
            continue

        # Group zone words by x-proximity (within 5px = same column = fraction stack)
        # Take the word(s) closest to the expected answer position
        zone_words.sort(key=lambda t: abs(t[3]) + abs(t[2]) * 0.3)

        # Primary answer word
        best_idx, best_word, _, _ = zone_words[0]
        used.add(best_idx)
        answer_parts = [best_word["text"]]

        # Check for stacked fraction parts at same x (within 5px)
        for idx, w, dx, dy in zone_words[1:]:
            if idx in used:
                continue
            if abs(w["x"] - best_word["x"]) < 8:
                # Vertically stacked at same x = fraction or multi-line
                used.add(idx)
                if w["y"] < best_word["y"]:
                    answer_parts.insert(0, w["text"])  # numerator goes first
                else:
                    answer_parts.append(w["text"])

        # Join parts — fractions become "num/denom", others get space-joined
        if len(answer_parts) == 2 and all(re.match(r"^-?\d+$", p) for p in answer_parts):
            # Two integers stacked = fraction
            answer = f"{answer_parts[0]}/{answer_parts[1]}"
        else:
            answer = " ".join(answer_parts)

        # Clean up
        answer = re.sub(r"\s*\(.*?\)\s*$", "", answer).strip()
        if answer:
            answers[blank["num"]] = answer

    return answers


def _parse_inline_answers(
    words: List[dict], max_num: int
) -> Dict[int, str]:
    """
    Parse inline answer format used in national-level answer keys.

    National keys have "N." followed directly by the answer value (no underscore blanks).
    Multi-column layout — markers appear at various x positions.
    """
    answers = {}
    for i, w in enumerate(words):
        m = re.match(r"^(\d+)\.$", w["text"])
        if not m:
            continue
        num = int(m.group(1))
        if num < 1 or num > max_num:
            continue

        # Collect answer words: within 15px y and to the right of this marker
        answer_words = []
        for j, other in enumerate(words):
            if j == i:
                continue
            dy = abs(other["y"] - w["y"])
            dx = other["x"] - w["x2"]
            if dy < 15 and 0 < dx < 150:
                answer_words.append(other)

        answer_words.sort(key=lambda aw: aw["x"])

        # Take numeric-looking answer value(s). Stop at any alphabetic word (unit).
        parts = []
        for aw in answer_words:
            text = aw["text"].strip().rstrip(".,;:")
            if not text or "_" in text:
                continue
            if text in ("$", "(", ")", ",", "or", "md", "dm"):
                continue
            # If it looks like a number/expression, keep it as part of the answer
            is_numeric = bool(re.match(
                r'^[−\-]?\d+([./,]\d+)*$|'   # integers, decimals, fractions
                r'^[−\-]?\d*[./]\d+$|'        # .5, 3/4
                r'^\d+[a-z]?$|'               # like "2jc" (expression)
                r'^[−\-]?\d+$',               # negative integers
                text
            ))
            if not is_numeric:
                break  # hit a unit/label word — answer is complete
            parts.append(text)
            if len(parts) >= 2:
                break

        if parts:
            answer = " ".join(parts)
            # Detect stacked fractions: two integers vertically aligned
            # Check if there's a second number directly below the first
            if len(parts) == 1 and re.match(r"^-?\d+$", parts[0]):
                for aw in answer_words:
                    if abs(aw["x"] - answer_words[0]["x"]) < 8 and aw["y"] > answer_words[0]["y"] + 5:
                        denom = aw["text"].strip()
                        if re.match(r"^-?\d+$", denom):
                            answer = f"{parts[0]}/{denom}"
                        break

            answer = re.sub(r"\s*\(.*?\)\s*$", "", answer).strip()
            if answer and num not in answers:
                answers[num] = answer

    return answers


def parse_answer_key(pdf_path: str, use_inline: bool = False) -> Dict[str, Dict[int, str]]:
    """
    Parse a MATHCOUNTS answer key PDF.

    Args:
        use_inline: If True, use inline parser (for national-level keys without underscore blanks).
                    If False (default), use spatial blank+value parser (for chapter/state keys).

    Returns: {round_type: {problem_num: answer_str}}
    """
    doc = fitz.open(pdf_path)
    all_answers: Dict[str, Dict[int, str]] = {}
    current_section: Optional[str] = None

    # Auto-detect: check if answer pages have "N." + underscore blank pairs
    if not use_inline:
        blank_count = 0
        for page_idx in range(len(doc)):
            text = doc[page_idx].get_text()
            if not SECTION_RE.search(text):
                continue
            words = _get_words(doc[page_idx])
            blanks = _find_blanks(words, 30)
            blank_count += len(blanks)
        if blank_count < 5:
            use_inline = True

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        text = page.get_text()

        # Detect section header
        if SKIP_SECTION_RE.search(text):
            current_section = None
            continue
        m = SECTION_RE.search(text)
        if m:
            current_section = m.group(1).lower()
            if current_section not in all_answers:
                all_answers[current_section] = {}

        if current_section is None:
            continue

        max_num = EXPECTED_COUNTS.get(current_section, 30)
        words = _get_words(page)

        if use_inline:
            page_answers = _parse_inline_answers(words, max_num)
        else:
            blanks = _find_blanks(words, max_num)
            if not blanks:
                continue
            candidates = _find_answer_candidates(words)
            page_answers = _match_answers(blanks, candidates)

        all_answers[current_section].update(page_answers)

    doc.close()

    for rt in ["sprint", "target", "team"]:
        if rt not in all_answers:
            all_answers[rt] = {}

    return all_answers
