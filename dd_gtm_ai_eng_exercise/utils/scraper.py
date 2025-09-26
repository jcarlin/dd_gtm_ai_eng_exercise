"""
Web scraper for Digital Construction Week speaker data.
"""
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict

class ConferenceScraper:
    def __init__(self):
        self.speakers_url = "https://www.digitalconstructionweek.com/all-speakers/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    async def scrape_speakers(self) -> List[Dict[str, str]]:
        """Scrape speaker information from the Digital Construction Week website."""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(self.speakers_url) as response:
                    if response.status != 200:
                        return []
                    html = await response.text()
                    return self._parse_speakers(html)
            except Exception as e:
                print(f"Error scraping speakers: {e}")
                return []

    def _parse_speakers(self, html: str) -> List[Dict[str, str]]:
        """Parse HTML to extract speaker information."""
        soup = BeautifulSoup(html, 'html.parser')
        speakers = []

        # Find all speaker-grid-details elements
        speaker_elements = soup.select('.speaker-grid-details')

        for element in speaker_elements:
            # Extract name from h3
            name_elem = element.select_one('h3')
            name = name_elem.get_text().strip() if name_elem else ''

            # Extract job info from .speaker-job
            job_elem = element.select_one('.speaker-job')
            job_text = job_elem.get_text().strip() if job_elem else ''

            # Parse job text to separate title and company
            title, company = self._parse_job_text(job_text)

            if name:
                speakers.append({
                    'name': name,
                    'title': title,
                    'company': company
                })

        return speakers

    def _parse_job_text(self, job_text: str) -> tuple[str, str]:
        """Parse job text to extract title and company."""
        if ' at ' in job_text:
            parts = job_text.split(' at ', 1)
            return parts[0].strip(), parts[1].strip()
        elif ' - ' in job_text:
            parts = job_text.split(' - ', 1)
            return parts[0].strip(), parts[1].strip()
        elif ', ' in job_text:
            parts = job_text.split(', ', 1)
            return parts[0].strip(), parts[1].strip()
        else:
            # If no separator found, assume it's all title
            return job_text, ''
