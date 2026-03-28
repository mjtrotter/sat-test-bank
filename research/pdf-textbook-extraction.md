# Research: Best methods for extracting structured content from math textbook PDFs at scale. Specifically:

1. State of the art for PDF-to-structured-data pipelines for STEM/math textbooks — tools like Marker, Nougat, Mathpix, PyMuPDF, pdfplumber. Which handle mathematical notation (LaTeX) best?
2. How to distinguish between different content types in a textbook: exposition/lesson text vs worked examples vs practice exercises vs solutions. What structural heuristics work?
3. Handling mathematical notation — OCR for equations, converting to LaTeX or MathML. Which tools produce the most accurate math OCR?
4. Batch processing approaches for 10+ textbooks (1000+ pages total). Pipeline architecture recommendations.
5. How to handle figures, diagrams, and geometric constructions that appear alongside problems (especially in geometry textbooks).
6. Any existing open-source projects that have tackled competition math textbook extraction specifically (e.g., extracting problems from Art of Problem Solving books)?

Context: We have 11 math textbook PDFs (AoPS Algebra I/II, AoPS Geometry, AoPS Precalculus, Gelfand Algebra/Geometry/Trigonometry/Functions/Coordinates, Batterson Competition Math, MATHCOUNTS Primary Text). Need to extract individual problems, tag them by topic/difficulty, and store in a database. Also have 315 MATHCOUNTS test PDFs (1990-2013) in standardized format. Running on M3 Ultra Mac (256GB RAM) + AMD EPYC with MI50 GPUs.

**Mode:** pro
**Thread:** https://www.perplexity.ai/search/best-methods-for-extracting-st-CPTG1y9ySw6__11Sfy75jg
**Date:** 2026-03-28T01:03:02.739077

## Answer

For your corpus, the strongest practical stack is usually a hybrid: a layout-aware PDF parser for structure, plus a dedicated math OCR model for equations, with a commercial fallback like Mathpix for the hardest pages. In 2026, the best open-source “all-in-one” options are still imperfect on textbook math, so the highest-quality pipeline is typically not one tool but a multi-stage system.
github
+4

1) Best PDF-to-structured-data stack

For STEM/math textbooks, the main tradeoff is: better layout recovery vs better LaTeX math recovery. Marker, MinerU, and Nougat are the most relevant open-source end-to-end systems; PyMuPDF and pdfplumber are best as low-level extraction utilities, not as complete semantic parsers.
pdfplumber
+4

A practical ranking for your use case:

Best overall open-source structure extraction: Marker or MinerU for page layout, reading order, headings, and chunking.
github
+2

Best open-source math-only OCR: Texify / math-specific OCR tools tend to do better when the task is primarily equations, while Nougat is more page-oriented and can hallucinate on smaller math-only regions.
github

Best commercial math OCR: Mathpix is still the strongest widely used option for LaTeX/MathML output from PDFs and images.
mathpix
+1

Best low-level PDF text/geometry access: PyMuPDF and pdfplumber for text spans, coordinates, page images, tables, and page-level heuristics.
pymupdf.readthedocs
+1

On math notation specifically, Mathpix explicitly supports LaTeX and MathML export, which is useful if your database needs normalized math representations. Among open-source options in the search results, Marker emphasizes preserving formulas in markdown, but one public benchmark note says it converts fewer equations to LaTeX than Nougat because it detects then converts equations more conservatively. Nougat is designed for academic document OCR with LaTeX math understanding, but it is page-centric rather than problem-centric.
mathpix
+2

2) Distinguishing content types

For textbooks, the most reliable approach is rule-based structure plus ML or LLM classification on chunks. In practice, you can distinguish exposition, worked examples, exercises, and solutions by combining layout cues with lexical markers and numbering patterns.
github
+2

Useful heuristics:

Exposition/lesson text: long paragraphs, section/subsection headings, definitions, theorems, and low density of problem numbering.

Worked examples: labels like “Example,” “Solution,” “Hint,” “Worked Example,” or bold/example callouts, often with dense equations and stepwise derivations.

Practice exercises: many short numbered items in a contiguous block, repeated answer blanks, and instruction verbs like “Find,” “Prove,” “Determine,” “Compute.”

Solutions: explicit “Solution” headers, answer-first patterns, and often reference back to problem numbers.

Geometry textbooks often use visual layout markers too: diagrams near numbered items, callout boxes, and problem numbering close to figures. PDFFigures2 is useful here because it extracts figure bounding boxes and captions, which helps attach diagrams to nearby problems or examples.
github

3) Mathematical notation handling

If the goal is accurate LaTeX or MathML, the best answer is usually Mathpix for production-grade OCR, especially when the source PDF contains scans or mixed-quality typesetting. If you want open source, Texify is specifically aimed at math OCR to LaTeX and supports both block and inline equations; Nougat is broader and more page-structured, while Marker is more conservative about equation conversion.
github
+4

A good practical rule:

Use native PDF text extraction first when the PDF has embedded text, because this preserves exact symbols and is cheaper.

Use equation-region OCR second only on detected math spans or images.

Normalize output into LaTeX in storage, and optionally render/store MathML if you need browser-side semantic math or search indexing.
mathpix

For formulas in mixed text, a hybrid approach often works best: OCR the page structure with Marker/MinerU/Nougat, then send only equation crops to Mathpix or Texify for clean LaTeX.
mathpix
+3

4) Batch pipeline for 10+ books

For 1000+ pages, use a staged, resumable pipeline with page-level artifacts and caching. The best architecture is usually: ingest PDFs, classify page type, extract layout/text, detect figures/equations, OCR only the hard regions, then post-process into problem records.
github
+3

A robust pipeline shape:

PDF fingerprinting and deduplication.

Page rendering at a fixed DPI plus native text extraction with PyMuPDF/pdfplumber.

Layout segmentation into blocks, figures, equations, tables, and headers.

Page-type classification: lesson, examples, exercises, solutions, answers, mixed.

Math OCR on selected regions only.

Problem segmentation into atomic items.

Metadata enrichment: topic, difficulty, source book, chapter, page, image links.

Human review queue for low-confidence pages.

For your hardware, the M3 Ultra can be very useful for CPU-heavy parsing and image preprocessing, while the AMD EPYC + MI50 setup is better suited to batch OCR/inference workloads if your stack can use those GPUs efficiently. Also, because your MATHCOUNTS PDFs are standardized, they are ideal for a separate high-precision pipeline with templates, since those documents are much more regular than textbooks.
mathcounts

5) Figures and geometry diagrams

For geometry-heavy books, treat figures as first-class objects rather than as page decorations. PDFFigures2 is directly relevant because it extracts figure boxes, captions, and some surrounding text, which helps anchor diagrams to the nearest exercise or example.
github

Best practice:

Crop and store each figure separately with page coordinates.

Link each figure to the nearest problem block by spatial proximity and numbering.

Preserve captions, labels, and any text inside the figure.

For diagrams with annotations, keep an image artifact even if you also OCR the labels.

If a problem references “the figure above” or “as shown,” attach the diagram to the problem record and keep the page layout metadata, because later retrieval and evaluation depend on that linkage.

6) Existing competition-math extraction work

There is relevant community and research work around AoPS and math problem extraction. A GitHub repo tied to a paper reproducing an AoPS data pipeline exists, and an Emergent Mind summary describes an automated AoPS pipeline that classifies math questions and extracts large-scale QA pairs from forum data.
emergentmind
+1

For textbook PDFs specifically, the search results show a GitHub “teachyourselfmath” project aimed at converting a math PDF into LaTeX and stripping irrelevant parts, which is directionally similar to your task. For figures and structured scholarly PDFs, PDFFigures2 is still one of the more useful open-source components to borrow from.
github
+1

Recommended setup for your corpus

For your exact mix of AoPS, Gelfand, Batterson, MATHCOUNTS Primary, and 315 MATHCOUNTS tests, I would use this split:

Standardized MATHCOUNTS tests: PyMuPDF/pdfplumber + deterministic layout heuristics, because the format is highly regular.

AoPS/Gelfand/Batterson textbooks: Marker or MinerU for structure, plus targeted math OCR on equation crops.

Hard scan pages / bad math / geometry diagrams: Mathpix fallback for equations and PDFFigures2-style figure extraction.
github
+3

Problem tagging: a classifier on extracted blocks, using heading cues, numbering, and nearby solution sections.

If you want, I can turn this into a concrete architecture diagram plus a proposed schema for your problem database and a page-classification rubric.

## Sources

1. [github](https://github.com/VikParuchuri/texify)
2. [github](https://github.com/allenai/pdffigures2)
3. [mathpix](https://mathpix.com/pdf-data-extraction)
4. [mathcounts](https://mathcounts.org/sites/default/files/2025%20Chapter%20solutions%20FINAL%20PDF_0.pdf)
