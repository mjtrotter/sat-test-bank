"""
Extract images from MATHCOUNTS PDFs and associate them with problems.

Uses PyMuPDF to pull embedded images, saves them to disk, and maps
each image to the problem on the same page by y-proximity.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

import fitz


def extract_images(
    pdf_path: str,
    output_dir: str,
    problem_markers: List[Dict],
) -> List[Dict]:
    """
    Extract images from a PDF and associate with problem numbers.

    Args:
        pdf_path: Path to the PDF
        output_dir: Directory to save extracted images
        problem_markers: List of {num, page, y} from the question parser

    Returns:
        List of {problem_number, image_path, page, figure_type}
    """
    doc = fitz.open(pdf_path)
    os.makedirs(output_dir, exist_ok=True)

    figures = []
    stem = Path(pdf_path).stem.split(" ")[0]  # e.g., "sprint"

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        images = page.get_images()

        if not images:
            continue

        # Get markers on this page
        page_markers = [
            m for m in problem_markers if m.get("page") == page_idx + 1
        ]

        for img_idx, img_info in enumerate(images):
            xref = img_info[0]

            try:
                pix = fitz.Pixmap(doc, xref)

                # Skip tiny images (logos, decorations)
                if pix.width < 30 or pix.height < 30:
                    continue

                # Convert CMYK to RGB if needed
                if pix.n > 4:
                    pix = fitz.Pixmap(fitz.csRGB, pix)

                # Save image
                fname = f"{stem}_p{page_idx + 1}_img{img_idx + 1}.png"
                img_path = os.path.join(output_dir, fname)
                pix.save(img_path)

                # Associate with nearest problem on this page
                # Use image's position on the page
                img_rects = page.get_image_rects(img_info)
                if img_rects:
                    img_y = img_rects[0].y0
                else:
                    img_y = 0

                # Find the problem whose y range contains this image
                best_num = None
                if page_markers:
                    for i, m in enumerate(page_markers):
                        m_y = m["y"] if "y" in m else 0
                        next_y = page_markers[i + 1]["y"] if i + 1 < len(page_markers) else 9999
                        if m_y - 20 <= img_y < next_y:
                            best_num = m["num"]
                            break
                    if best_num is None:
                        # Default to nearest marker
                        best_num = min(page_markers, key=lambda m: abs(m.get("y", 0) - img_y))["num"]

                figures.append({
                    "problem_number": best_num,
                    "image_path": img_path,
                    "page": page_idx + 1,
                    "width": pix.width,
                    "height": pix.height,
                    "figure_type": "diagram",
                })

            except Exception as e:
                print(f"  Warning: could not extract image xref={xref}: {e}")

    doc.close()
    return figures
