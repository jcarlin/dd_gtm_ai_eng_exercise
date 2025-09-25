"""
Web scraper for Digital Construction Week speaker data.
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict
import re


class ConferenceScraper:
    def __init__(self):
        """Initialize the scraper."""
        self.base_url = "https://www.digitalconstructionweek.com"
        self.speakers_url = "https://www.digitalconstructionweek.com/all-speakers/"

        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
        }

    async def scrape_speakers(self) -> List[Dict[str, str]]:
        """
        Scrape speaker information from the Digital Construction Week website.

        Returns:
            List of dicts with keys: name, title, company
        """
        print("Scraping Digital Construction Week speakers...")

        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(self.speakers_url) as response:
                    if response.status != 200:
                        print(f"Failed to fetch speakers page: HTTP {response.status}")
                        return []

                    html = await response.text()
                    return self._parse_speakers_html(html)

            except Exception as e:
                print(f"Error scraping speakers: {str(e)}")
                return []

    def _parse_speakers_html(self, html: str) -> List[Dict[str, str]]:
        """Parse HTML to extract speaker information."""
        soup = BeautifulSoup(html, 'html.parser')
        speakers = []

        # Look for different possible speaker container patterns
        speaker_containers = []

        # Try common speaker listing patterns
        patterns = [
            '.speaker-card',
            '.speaker-item',
            '.speaker',
            '[class*="speaker"]',
            '.profile',
            '.person',
            '.team-member',
            '.bio'
        ]

        for pattern in patterns:
            containers = soup.select(pattern)
            if containers:
                speaker_containers = containers
                print(f"Found {len(containers)} speakers using pattern: {pattern}")
                break

        # If no specific pattern found, try to find any element with speaker-like content
        if not speaker_containers:
            # Look for any divs/sections that might contain speaker info
            potential_containers = soup.find_all(['div', 'section', 'article'],
                                                class_=re.compile(r'(speaker|person|profile|bio|team)', re.I))
            if potential_containers:
                speaker_containers = potential_containers
                print(f"Found {len(potential_containers)} potential speaker containers")

        for container in speaker_containers:
            speaker = self._extract_speaker_info(container)
            if speaker and speaker['name'] and speaker['company']:
                speakers.append(speaker)

        print(f"Successfully parsed {len(speakers)} speakers")
        return speakers

    def _extract_speaker_info(self, container) -> Dict[str, str]:
        """Extract individual speaker information from a container element."""
        speaker = {
            'name': '',
            'title': '',
            'company': ''
        }

        # Try to extract name
        name_selectors = [
            'h1', 'h2', 'h3', 'h4', '.name', '.speaker-name',
            '[class*="name"]', '.title', 'strong', 'b'
        ]

        for selector in name_selectors:
            name_element = container.select_one(selector)
            if name_element:
                name_text = name_element.get_text().strip()
                if name_text and len(name_text.split()) >= 2:  # Likely a full name
                    speaker['name'] = name_text
                    break

        # Try to extract title and company
        # Look for text patterns that indicate titles/companies
        text_elements = container.find_all(text=True)
        all_text = ' '.join([t.strip() for t in text_elements if t.strip()])

        # Split text into lines and look for patterns
        lines = [line.strip() for line in all_text.split('\n') if line.strip()]

        # Common patterns for title/company
        for i, line in enumerate(lines):
            # Skip the name line
            if speaker['name'] in line:
                continue

            # Look for title patterns (usually contains job-related words)
            title_keywords = ['manager', 'director', 'engineer', 'architect', 'consultant',
                            'supervisor', 'coordinator', 'specialist', 'lead', 'chief',
                            'vice president', 'vp', 'president', 'ceo', 'cfo', 'cto']

            if any(keyword in line.lower() for keyword in title_keywords) and not speaker['title']:
                speaker['title'] = line

            # Company is often the last substantial line or follows specific patterns
            if not speaker['company']:
                # Skip very short lines or lines that look like titles
                if len(line) > 5 and not any(keyword in line.lower() for keyword in title_keywords):
                    speaker['company'] = line

        # If we still don't have company, try to get it from common company selectors
        if not speaker['company']:
            company_selectors = ['.company', '.organization', '[class*="company"]',
                               '[class*="org"]', '.employer']
            for selector in company_selectors:
                company_element = container.select_one(selector)
                if company_element:
                    speaker['company'] = company_element.get_text().strip()
                    break

        # Clean up the data
        speaker['name'] = self._clean_text(speaker['name'])
        speaker['title'] = self._clean_text(speaker['title'])
        speaker['company'] = self._clean_text(speaker['company'])

        return speaker

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""

        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text).strip()

        # Remove common unwanted prefixes/suffixes
        text = re.sub(r'^(speaker:?|name:?)\s*', '', text, flags=re.I)

        return text

    async def scrape_with_fallback_data(self) -> List[Dict[str, str]]:
        """
        Attempt to scrape speakers, with fallback to sample data if scraping fails.
        This is useful for development/testing purposes.
        """
        speakers = await self.scrape_speakers()

        if not speakers:
            print("Scraping failed or returned no data. Using sample fallback data...")
            # Fallback sample data for testing
            speakers = [
                {"name": "John Smith", "title": "Construction Manager", "company": "ABC Construction"},
                {"name": "Sarah Johnson", "title": "Project Director", "company": "BuildCorp"},
                {"name": "Mike Chen", "title": "BIM Manager", "company": "TechBuild Solutions"},
                {"name": "Lisa Anderson", "title": "Real Estate Developer", "company": "Anderson Properties"},
                {"name": "David Wilson", "title": "VP of Engineering", "company": "Autodesk"},  # Competitor
                {"name": "Emma Thompson", "title": "Cloud Solutions Architect", "company": "AWS"},  # Partner
                {"name": "Robert Garcia", "title": "Safety Manager", "company": "Safe Site Construction"},
                {"name": "Jennifer Lee", "title": "Property Development Manager", "company": "Urban Development Corp"},
                {"name": "James Brown", "title": "Senior Engineer", "company": "Infrastructure Inc"},
                {"name": "Maria Rodriguez", "title": "Facility Manager", "company": "Corporate Real Estate Partners"}
            ]

        return speakers