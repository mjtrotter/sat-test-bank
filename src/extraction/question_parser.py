"""
Parse MATHCOUNTS question PDFs by round type.

Sprint: 30 questions, blanks on left, question text on right
Target: 8 questions in pairs, cover page + 2 questions per pair
Team: 10 questions, similar layout to sprint

Uses word-level extraction to separate answer blanks from question text.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import fitz


BLANK_RE = re.compile(r"^(\d+)\.$")

# X threshold separating answer blank column from question text
# Sprint/Team: blanks at x≈54, text at x≈167+
# Target: blanks at x≈46, text spans wider
QUESTION_X_THRESHOLD = 160

NOISE_PATTERNS = [
    re.compile(r"copyright", re.I),
    re.compile(r"mathcounts", re.I),
    re.compile(r"do\s+not\s+begin", re.I),
    re.compile(r"all\s+rights\s+reserved", re.I),
    re.compile(r"sprint\s+round", re.I),
    re.compile(r"target\s+round", re.I),
    re.compile(r"team\s+round", re.I),
    re.compile(r"chapter\s+competition", re.I),
    re.compile(r"state\s+competition", re.I),
    re.compile(r"national\s+competition", re.I),
    re.compile(r"problems?\s+\d+", re.I),
    re.compile(r"total\s+correct", re.I),
    re.compile(r"scorer", re.I),
    re.compile(r"^\s*name\s*$", re.I),
    re.compile(r"^\s*school\s*$", re.I),
]


def _is_noise_line(text: str) -> bool:
    """Check if a line is boilerplate (headers, copyright, instructions)."""
    return any(p.search(text) for p in NOISE_PATTERNS)


def _extract_page_words(page: fitz.Page) -> List[dict]:
    """Extract words with positions from a page."""
    raw = page.get_text("words")
    return [
        {"text": w[4], "x": w[0], "y": w[1], "x2": w[2], "y2": w[3]}
        for w in raw
    ]


def _find_problem_markers(words: List[dict], max_num: int) -> List[dict]:
    """
    Find problem number markers (e.g., '1.' followed by '___').
    Returns list of {num, y} sorted by y position.

    Uses spatial proximity (not list order) to find the underscore blank
    near each "N." marker, since PyMuPDF word order doesn't guarantee
    physical reading order.
    """
    markers = []
    seen_nums = set()
    for w in words:
        m = BLANK_RE.match(w["text"])
        if not m:
            continue
        num = int(m.group(1))
        if num < 1 or num > max_num:
            continue
        # Find nearest blank word within spatial box (not list order).
        # Blanks are underscores or garbled unicode (some PDFs use replacement chars).
        def _is_blank_word(t: str) -> bool:
            return "_" in t or "\ufffd" in t or (len(t) > 8 and t == t[0] * len(t))

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


def _collect_question_text(
    words: List[dict],
    y_start: float,
    y_end: float,
    x_threshold: float = 0,
) -> str:
    """
    Collect question text from words between y_start and y_end.
    Filters out blank words, problem number markers, and boilerplate.
    """
    q_words = []
    for w in words:
        if w["y"] < y_start - 8 or w["y"] >= y_end:
            continue
        if w["x"] < x_threshold:
            continue
        # Skip underscore/blank words
        if "_" in w["text"] or "\ufffd" in w["text"]:
            continue
        # Skip standalone problem number markers (e.g., "6.")
        if BLANK_RE.match(w["text"]):
            continue
        q_words.append(w)

    if not q_words:
        return ""

    # Sort by (y, x) to reconstruct reading order
    q_words.sort(key=lambda w: (round(w["y"] / 3) * 3, w["x"]))

    # Group into lines by y proximity
    lines = []
    current_line = [q_words[0]]
    for w in q_words[1:]:
        if abs(w["y"] - current_line[-1]["y"]) < 5:
            current_line.append(w)
        else:
            lines.append(current_line)
            current_line = [w]
    lines.append(current_line)

    # Join words within each line, then join lines
    text_lines = []
    for line in lines:
        line_text = " ".join(w["text"] for w in sorted(line, key=lambda w: w["x"]))
        if not _is_noise_line(line_text):
            text_lines.append(line_text)

    return " ".join(text_lines).strip()


def parse_sprint(pdf_path: str) -> List[Dict]:
    """
    Parse a Sprint round PDF. Expected: 30 questions.
    Layout: blanks in left column, question text in right area.
    """
    doc = fitz.open(pdf_path)
    all_markers = []
    page_words = {}

    # Collect markers and words from all pages
    for pg_idx in range(len(doc)):
        page = doc[pg_idx]
        words = _extract_page_words(page)
        markers = _find_problem_markers(words, max_num=30)

        if markers:
            page_words[pg_idx] = words
            for m in markers:
                m["page"] = pg_idx
                all_markers.append(m)

    doc_ref = doc  # keep open for page heights

    # Build problems by finding text between consecutive markers
    problems = []
    for i, marker in enumerate(all_markers):
        # Y boundary: from this marker to the next (or page bottom)
        if i + 1 < len(all_markers) and all_markers[i + 1]["page"] == marker["page"]:
            y_end = all_markers[i + 1]["y"] - 5
        else:
            y_end = doc_ref[marker["page"]].rect.height - 30  # leave margin for copyright

        words = page_words[marker["page"]]
        text = _collect_question_text(words, marker["y"], y_end)

        if text and len(text) > 10:
            problems.append({
                "problem_number": marker["num"],
                "problem_text": text,
                "page": marker["page"] + 1,
            })

    doc.close()

    # Deduplicate (same problem number shouldn't appear twice)
    seen = {}
    for p in problems:
        num = p["problem_number"]
        if num not in seen or len(p["problem_text"]) > len(seen[num]["problem_text"]):
            seen[num] = p
    return [seen[n] for n in sorted(seen.keys())]


def parse_target(pdf_path: str) -> List[Dict]:
    """
    Parse a Target round PDF. Expected: 8 questions.
    Layout: pairs of problems on alternating pages (cover + questions).
    Even pages (2, 4, 6, 8) typically have the actual questions.
    """
    doc = fitz.open(pdf_path)
    all_markers = []
    page_words = {}

    for pg_idx in range(len(doc)):
        page = doc[pg_idx]
        words = _extract_page_words(page)
        markers = _find_problem_markers(words, max_num=8)

        if markers:
            page_words[pg_idx] = words
            for m in markers:
                m["page"] = pg_idx
                all_markers.append(m)

    problems = []
    for i, marker in enumerate(all_markers):
        if i + 1 < len(all_markers) and all_markers[i + 1]["page"] == marker["page"]:
            y_end = all_markers[i + 1]["y"] - 5
        else:
            y_end = doc[marker["page"]].rect.height - 30

        words = page_words[marker["page"]]
        # Target has a wider text area — lower the x threshold
        text = _collect_question_text(words, marker["y"], y_end, x_threshold=120)

        if text and len(text) > 10:
            problems.append({
                "problem_number": marker["num"],
                "problem_text": text,
                "page": marker["page"] + 1,
            })

    doc.close()

    seen = {}
    for p in problems:
        num = p["problem_number"]
        if num not in seen or len(p["problem_text"]) > len(seen[num]["problem_text"]):
            seen[num] = p
    return [seen[n] for n in sorted(seen.keys())]


def parse_team(pdf_path: str) -> List[Dict]:
    """
    Parse a Team round PDF. Expected: 10 questions.
    Similar layout to Sprint but fewer questions.
    """
    doc = fitz.open(pdf_path)
    all_markers = []
    page_words = {}

    for pg_idx in range(len(doc)):
        page = doc[pg_idx]
        words = _extract_page_words(page)
        markers = _find_problem_markers(words, max_num=10)

        if markers:
            page_words[pg_idx] = words
            for m in markers:
                m["page"] = pg_idx
                all_markers.append(m)

    problems = []
    for i, marker in enumerate(all_markers):
        if i + 1 < len(all_markers) and all_markers[i + 1]["page"] == marker["page"]:
            y_end = all_markers[i + 1]["y"] - 5
        else:
            y_end = doc[marker["page"]].rect.height - 30

        words = page_words[marker["page"]]
        text = _collect_question_text(words, marker["y"], y_end)

        if text and len(text) > 10:
            problems.append({
                "problem_number": marker["num"],
                "problem_text": text,
                "page": marker["page"] + 1,
            })

    doc.close()

    seen = {}
    for p in problems:
        num = p["problem_number"]
        if num not in seen or len(p["problem_text"]) > len(seen[num]["problem_text"]):
            seen[num] = p
    return [seen[n] for n in sorted(seen.keys())]


def parse_questions(pdf_path: str, round_type: str) -> List[Dict]:
    """Dispatch to the correct parser based on round type."""
    parsers = {
        "sprint": parse_sprint,
        "target": parse_target,
        "team": parse_team,
    }
    parser = parsers.get(round_type)
    if not parser:
        return []
    return parser(pdf_path)
