import argparse
import asyncio
import httpx
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

from bs4 import BeautifulSoup

from src.models.enums import ContestFamily

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

AOPS_BASE_URL = "https://artofproblemsolving.com/wiki/index.php/"
USER_AGENT = "VanguardAoPSScraper/1.0 (+https://artofproblemsolving.com/wiki/)" # Respectful User-Agent

class RateLimiter:
    """Ensures that requests are made at a maximum rate of 1 per second."""
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit  # requests per second
        self._last_request_time = 0

    async def __aenter__(self):
        elapsed = asyncio.get_event_loop().time() - self._last_request_time
        if elapsed < 1.0 / self.rate_limit:
            await asyncio.sleep(1.0 / self.rate_limit - elapsed)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._last_request_time = asyncio.get_event_loop().time()


class AoPSScraper:
    def __init__(self, output_dir: Path, progress_file: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.image_dir = self.output_dir / "images"
        self.image_dir.mkdir(exist_ok=True)
        self.progress_file = progress_file
        self.progress: Dict[str, Any] = self._load_progress()
        self.client = httpx.AsyncClient(headers={"User-Agent": USER_AGENT})
        self.rate_limiter = RateLimiter(rate_limit=1.0) # 1 request per second

    async def _fetch_page(self, url: str) -> Optional[str]:
        async with self.rate_limiter:
            try:
                response = await self.client.get(url, follow_redirects=True)
                response.raise_for_status()
                logger.info(f"Fetched: {url}")
                return response.text
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error fetching {url}: {e}")
            except httpx.RequestError as e:
                logger.error(f"Request error fetching {url}: {e}")
            return None

    async def _debug_fetch_and_save_page(self, url: str, file_path: Path) -> bool:
        async with self.rate_limiter:
            try:
                response = await self.client.get(url, follow_redirects=True)
                response.raise_for_status()
                file_path.write_text(response.text, encoding='utf-8')
                logger.info(f"DEBUG: Fetched and saved: {url} to {file_path}")
                return True
            except httpx.HTTPStatusError as e:
                logger.error(f"DEBUG: HTTP error fetching {url}: {e}")
            except httpx.RequestError as e:
                logger.error(f"DEBUG: Request error fetching {url}: {e}")
            return False

    def _load_progress(self) -> Dict[str, Any]:
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                logger.warning(f"Could not decode progress file {self.progress_file}: {e}. Starting fresh.")
        return {"completed_contests": {}}

    def _save_progress(self):
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)

    def _mark_contest_as_completed(self, contest_id: str, year: int):
        if contest_id not in self.progress["completed_contests"]:
            self.progress["completed_contests"][contest_id] = []
        if year not in self.progress["completed_contests"][contest_id]:
            self.progress["completed_contests"][contest_id].append(year)
            self._save_progress()

    def _is_contest_completed(self, contest_id: str, year: int) -> bool:
        return contest_id in self.progress["completed_contests"] and year in self.progress["completed_contests"][contest_id]

    def _generate_contest_url(self, contest_family: ContestFamily, year: int, variant: Optional[str] = None) -> str:
        if contest_family == ContestFamily.AMC_8:
            return f"{AOPS_BASE_URL}{year}_AMC_8_Problems"
        elif contest_family == ContestFamily.AMC_10:
            return f"{AOPS_BASE_URL}{year}_AMC_10{variant}_Problems"
        elif contest_family == ContestFamily.AMC_12:
            return f"{AOPS_BASE_URL}{year}_AMC_12{variant}_Problems"
        elif contest_family == ContestFamily.AIME:
            return f"{AOPS_BASE_URL}{year}_AIME_{variant}_Problems"
        else:
            raise ValueError(f"Unsupported contest family: {contest_family}")

    async def _get_problem_links_from_contest_page(self, contest_url: str) -> List[str]:
        html = await self._fetch_page(contest_url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, "html.parser")
        problem_links = []
        # AoPS problem links usually follow a pattern on the contest page
        # e.g., links to ".../Problem_1", ".../Problem_2", etc.
        # We need to find the specific structure they use.
        # This is a placeholder and needs to be refined after inspecting actual pages.
        # A common pattern is <a href="/wiki/index.php/YYYY_Contest_Problems/Problem_N" title="...">
        
        # Look for links that start with the contest page URL, followed by /Problem_N
        base_path = contest_url.replace(AOPS_BASE_URL, "")
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            # Example: /wiki/index.php?title=2020_AMC_10A_Problems/Problem_1
            # Using regex to be more robust
            match = re.search(r"title=(\d{4})_(AMC_8|AMC_10[AB]|AMC_12[AB]|AIME_[IVX]+)_Problems/Problem_(\d+)", href)
            if match:
                 # Reconstruct the full URL
                 full_problem_url = f"{AOPS_BASE_URL}{match.group(1)}_{match.group(2)}_Problems/Problem_{match.group(3)}"
                 if full_problem_url not in problem_links: # Avoid duplicates
                     problem_links.append(full_problem_url)
        
        # Sort to ensure consistent order
        problem_links = sorted(list(set(problem_links)))
        logger.info(f"Found {len(problem_links)} problem links on {contest_url}")
        return problem_links


    async def _scrape_problem_page(self, problem_url: str) -> Optional[Dict[str, Any]]:
        html = await self._fetch_page(problem_url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, "html.parser")
        
        # Placeholder for extraction logic
        # This part will require detailed inspection of AoPS problem page HTML structure
        problem_data = {
            "id": None, # Will generate from URL/contest info
            "source": "aops_wiki",
            "contest": None,
            "year": None,
            "number": None,
            "problem_text": None,
            "problem_latex": None,
            "answer": None,
            "answer_choices": [],
            "solutions": [],
            "figures": [],
            "skill_tags": [], # AoPS's own topic categorization might be useful
            "difficulty_band": None,
            "aops_difficulty_rating": None, # Community difficulty ratings
            "extraction_confidence": 0.98 # Default high confidence for structured AoPS data
        }
        
        # Extract contest, year, problem number from URL
        url_match = re.search(r"(\d{4})_(AMC_8|AMC_10[AB]|AMC_12[AB]|AIME_[IVX]+)_Problems/Problem_(\d+)", problem_url)
        if url_match:
            problem_data["year"] = int(url_match.group(1))
            problem_data["contest"] = url_match.group(2).replace('_', ' ')
            problem_data["number"] = int(url_match.group(3))
            problem_data["id"] = f"{problem_data['contest'].replace(' ', '')}_{problem_data['year']}_{problem_data['number']}"

        # General approach: find the main content div, then look for specific elements
        content_div = soup.find("div", class_="mw-parser-output")
        if not content_div:
            logger.warning(f"Could not find main content div for {problem_url}")
            return None

        # --- Extract Problem Text and LaTeX ---
        problem_heading = content_div.find("h2", string="Problem")
        if problem_heading:
            problem_text_elements = []
            problem_latex_snippets = []
            
            # First, try to extract answer choices from an image within the problem section's siblings
            # This needs to happen before modifying the soup for problem_text
            temp_problem_content_soup = BeautifulSoup("", "html.parser")
            current_element = problem_heading.next_sibling
            while current_element and current_element.name != "h2":
                temp_problem_content_soup.append(current_element)
                current_element = current_element.next_sibling
            
            # Now, use temp_problem_content_soup to find answer choices
            all_latex_images_in_problem_section = temp_problem_content_soup.find_all("img", class_="latex")
            for img_tag in all_latex_images_in_problem_section:
                alt_text = img_tag.get("alt", "")
                if re.search(r"\\textbf{\([A-E]\)}", alt_text) and re.search(r"\\textbf{\([A-E]\)}.*?\\textbf{\([A-E]\)}", alt_text):
                    choices_raw = alt_text.split('\\qquad')
                    problem_data["answer_choices"] = [choice.strip() for choice in choices_raw if choice.strip()]
                    # Remove this img_tag from the temp_problem_content_soup so it's not part of problem_text
                    img_tag.extract()
                    break # Found the answer choices, stop searching in this section

            # Now, reconstruct problem_text and problem_latex from the modified temp_problem_content_soup
            # This is where we replace remaining LaTeX images with their alt text for problem_text
            for img_tag in temp_problem_content_soup.find_all("img", class_="latex"):
                if img_tag.get("alt"):
                    problem_latex_snippets.append(img_tag["alt"])
                    img_tag.replace_with(img_tag["alt"]) # Replace image with its LaTeX alt text
            
            problem_data["problem_text"] = temp_problem_content_soup.get_text(separator=' ', strip=True)
            problem_data["problem_latex"] = " ".join(problem_latex_snippets) if problem_latex_snippets else ""





        # --- Extract Solutions ---
        solutions_list = []
        # Find all h2 tags that contain "Solution " followed by a number
        solution_headings = content_div.find_all("h2", string=re.compile(r"Solution \d+"))
        for sol_heading in solution_headings:
            solution_approach = sol_heading.get_text(strip=True) # "Solution 1", "Solution 2", etc.
            solution_text_html = []
            solution_latex_snippets = []
            
            current_element = sol_heading.next_sibling
            while current_element and current_element.name != "h2" and not current_element.name == "div" and not current_element.name == "table" and not current_element.name == "ul" and not current_element.name == "ol": # Stop at next heading or div/table/list
                if hasattr(current_element, 'find_all'):
                    for img_tag in current_element.find_all("img", class_="latex"):
                        if img_tag.get("alt"):
                            solution_latex_snippets.append(img_tag["alt"])
                    
                    temp_soup = BeautifulSoup(str(current_element), "html.parser")
                    for img_tag in temp_soup.find_all("img", class_="latex"):
                        if img_tag.get("alt"):
                            img_tag.replace_with(img_tag["alt"])
                    solution_text_html.append(str(temp_soup))
                current_element = current_element.next_sibling
            
            full_solution_html_str = "".join(solution_text_html)
            clean_solution_soup = BeautifulSoup(full_solution_html_str, "html.parser")
            full_solution_text = clean_solution_soup.get_text(separator=' ', strip=True)
            full_solution_latex = " ".join(solution_latex_snippets)
            
            # Try to infer answer from solution if it's explicitly boxed/mentioned
            answer_match = re.search(r'\boxed{\textbf{([A-E])}', full_solution_latex)
            if answer_match:
                problem_data["answer"] = answer_match.group(1)

            if full_solution_text or full_solution_latex:
                solutions_list.append({
                    "approach": solution_approach,
                    "text": full_solution_text,
                    "latex": full_solution_latex
                })
        problem_data["solutions"] = solutions_list

        # --- Extract Figures ---
        downloaded_figures = []
        for img_tag in content_div.find_all("img", src=True):
            if "latex" not in img_tag.get("class", []): # Exclude LaTeX images
                img_url = img_tag["src"]
                if img_url.startswith("//"):
                    img_url = "https:" + img_url
                
                # Create a unique filename for the image
                filename = Path(img_url).name
                if not filename: # Fallback if name is empty, e.g., for base64 images
                    filename = f"figure_{len(downloaded_figures)}_{Path(img_url).suffix or '.png'}"

                local_image_path = self.image_dir / filename
                
                # Download the image
                try:
                    async with self.rate_limiter:
                        img_response = await self.client.get(img_url)
                        img_response.raise_for_status()
                        local_image_path.write_bytes(img_response.content)
                        logger.info(f"Downloaded image: {img_url} to {local_image_path}")
                        downloaded_figures.append(str(local_image_path))
                except httpx.HTTPStatusError as e:
                    logger.error(f"HTTP error downloading image {img_url}: {e}")
                except httpx.RequestError as e:
                    logger.error(f"Request error downloading image {img_url}: {e}")
        problem_data["figures"] = downloaded_figures

        # --- Extract AoPS Difficulty Rating ---
        # Difficulty ratings are often in specific tables or meta-info sections
        # Re-inspecting the page, it's not directly on the problem page.
        # It's often found on contest overviews or dedicated difficulty pages.
        # Leaving this as None for now, as direct extraction from this page is not feasible.
        problem_data["aops_difficulty_rating"] = None

        return problem_data

    async def _fetch_samples(self, contest_url: str, problem_url: str, output_path: Path):
        await self._debug_fetch_and_save_page(contest_url, output_path / "sample_contest_page.html")
        await self._debug_fetch_and_save_page(problem_url, output_path / "sample_problem_page.html")
        logger.info("Sample pages fetched and saved. Exiting debug mode.")

    async def scrape_contest(self, contest_family: ContestFamily, year: int, variant: Optional[str] = None):
        contest_id = f"{contest_family.value}_{variant if variant else ''}"
        if self._is_contest_completed(contest_id, year):
            logger.info(f"Skipping {contest_id} {year} - already completed.")
            return

        logger.info(f"Scraping {contest_family.value} {year} {variant if variant else ''}...")
        contest_url = self._generate_contest_url(contest_family, year, variant)
        
        problem_links = await self._get_problem_links_from_contest_page(contest_url)
        if not problem_links:
            logger.warning(f"No problem links found for {contest_url}. Marking as completed to avoid re-attempting if truly empty.")
            self._mark_contest_as_completed(contest_id, year)
            return

        contest_problems_data = []
        for problem_link in problem_links:
            problem_data = await self._scrape_problem_page(problem_link)
            if problem_data:
                contest_problems_data.append(problem_data)
            await asyncio.sleep(0.1) # Small delay between problems as well, within the 1s rate limit

        # Save results to JSON file
        contest_output_dir = self.output_dir / contest_family.value
        contest_output_dir.mkdir(exist_ok=True)
        
        output_filename = f"{year}{variant if variant else ''}.json"
        if contest_family == ContestFamily.AIME: # AIME variants are I/II, so filename needs to reflect that
             output_filename = f"{year}_{variant}.json"

        output_path = contest_output_dir / output_filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(contest_problems_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(contest_problems_data)} problems for {contest_id} {year} to {output_path}")

        self._mark_contest_as_completed(contest_id, year)

    async def run(self, contest: Optional[str], year: Optional[int], output_dir_str: str):
        if output_dir_str: # Update output_dir if specified by CLI
            self.output_dir = Path(output_dir_str)
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.image_dir = self.output_dir / "images"
            self.image_dir.mkdir(exist_ok=True)
            # Re-initialize progress with potentially new output_dir path for progress_file
            self.progress_file = self.output_dir / "aops_progress.json"
            self.progress = self._load_progress()
        
        target_contests = []

        if contest and year:
            # Specific contest and year requested
            contest_family: ContestFamily
            variant: Optional[str] = None
            contest_upper = contest.upper()

            if contest_upper == "AMC_8":
                contest_family = ContestFamily.AMC_8
            elif contest_upper.startswith("AMC_10"):
                contest_family = ContestFamily.AMC_10
                variant = contest_upper[-1] if contest_upper.endswith(('A', 'B')) else None
            elif contest_upper.startswith("AMC_12"):
                contest_family = ContestFamily.AMC_12
                variant = contest_upper[-1] if contest_upper.endswith(('A', 'B')) else None
            elif contest_upper.startswith("AIME"):
                contest_family = ContestFamily.AIME
                variant = contest_upper.split('_')[1] if len(contest_upper.split('_')) > 1 else None
            else:
                raise ValueError(f"Invalid contest format: {contest}. Expected format like 'AMC_8', 'AMC_10A', 'AIME_I'.")
            
            target_contests.append((contest_family, year, variant))
        elif contest:
            # Specific contest type, all years
            contest_family_str = contest.split('_')[0].upper()
            if contest_family_str not in ContestFamily.__members__:
                 raise ValueError(f"Invalid contest family: {contest_family_str}")
            contest_family = ContestFamily[contest_family_str]
            variant = contest.split('_')[1].upper() if len(contest.split('_')) > 1 else None

            years_range = []
            if contest_family == ContestFamily.AMC_8:
                years_range = range(2000, 2027) # 2000-present
                for yr in years_range:
                    target_contests.append((contest_family, yr, None))
            elif contest_family == ContestFamily.AMC_10:
                years_range = range(2002, 2027) # 2002-present
                for yr in years_range:
                    target_contests.append((contest_family, yr, "A"))
                    target_contests.append((contest_family, yr, "B"))
            elif contest_family == ContestFamily.AMC_12:
                years_range = range(2002, 2027) # 2002-present
                for yr in years_range:
                    target_contests.append((contest_family, yr, "A"))
                    target_contests.append((contest_family, yr, "B"))
            elif contest_family == ContestFamily.AIME:
                years_range = range(1983, 2027) # 1983-present
                for yr in years_range:
                    target_contests.append((contest_family, yr, "I"))
                    target_contests.append((contest_family, yr, "II"))
            else:
                raise ValueError(f"Contest {contest_family.value} does not have a defined year range.")
        else:
            # Scrape all known contests and years if no specific contest/year is provided
            # AMC 8
            for year_amc8 in range(2000, 2027):
                target_contests.append((ContestFamily.AMC_8, year_amc8, None))
            # AMC 10A/B
            for year_amc10 in range(2002, 2027):
                target_contests.append((ContestFamily.AMC_10, year_amc10, "A"))
                target_contests.append((ContestFamily.AMC_10, year_amc10, "B"))
            # AMC 12A/B
            for year_amc12 in range(2002, 2027):
                target_contests.append((ContestFamily.AMC_12, year_amc12, "A"))
                target_contests.append((ContestFamily.AMC_12, year_amc12, "B"))
            # AIME I/II
            for year_aime in range(1983, 2027):
                target_contests.append((ContestFamily.AIME, year_aime, "I"))
                target_contests.append((ContestFamily.AIME, year_aime, "II"))


        for contest_family, year, variant in target_contests:
            await self.scrape_contest(contest_family, year, variant)
        
        await self.client.aclose()


def main():
    parser = argparse.ArgumentParser(description="AoPS Wiki Scraper for AMC/AIME problems.")
    parser.add_argument("--contest", type=str, 
                        help="Specific contest to scrape (e.g., 'AMC_10A', 'AIME_I'). If not provided, all known contests are scraped. Use format like 'AMC_8', 'AMC_10A', 'AMC_12B', 'AIME_I'.")
    parser.add_argument("--year", type=int, 
                        help="Specific year to scrape. Requires --contest to be specified. If --contest is given but --year is not, all available years for that contest will be scraped.")
    parser.add_argument("--output-dir", type=str, default="data/aops",
                        help="Directory to save scraped data and images.")
    
    args = parser.parse_args()

    output_path = Path(args.output_dir)
    progress_file = output_path / "aops_progress.json"

    scraper = AoPSScraper(output_path, progress_file)
    
    # Temporarily fetch and save sample pages for inspection
    # contest_url = "https://artofproblemsolving.com/wiki/index.php/2020_AMC_10A_Problems"
    # problem_url = "https://artofproblemsolving.com/wiki/index.php/2020_AMC_10A_Problems/Problem_1"
    # asyncio.run(scraper._fetch_samples(contest_url, problem_url, output_path))
    
    # Run the async scraper
    asyncio.run(scraper.run(args.contest, args.year, args.output_dir))


if __name__ == "__main__":
    main()