"""Tests for web scraper."""
import pytest
from utils.scraper import ConferenceScraper


class TestConferenceScraper:
    """Test ConferenceScraper class."""

    def test_parse_job_text_with_at(self):
        """Test parsing job text with 'at' separator."""
        scraper = ConferenceScraper()
        title, company = scraper._parse_job_text("Project Manager at ABC Construction")
        assert title == "Project Manager"
        assert company == "ABC Construction"

    def test_parse_job_text_with_dash(self):
        """Test parsing job text with '-' separator."""
        scraper = ConferenceScraper()
        title, company = scraper._parse_job_text("CEO - Tech Corp")
        assert title == "CEO"
        assert company == "Tech Corp"

    def test_parse_job_text_with_comma(self):
        """Test parsing job text with ',' separator."""
        scraper = ConferenceScraper()
        title, company = scraper._parse_job_text("Site Manager, BuildCo")
        assert title == "Site Manager"
        assert company == "BuildCo"

    def test_parse_job_text_no_separator(self):
        """Test parsing job text with no separator (all title)."""
        scraper = ConferenceScraper()
        title, company = scraper._parse_job_text("Project Manager")
        assert title == "Project Manager"
        assert company == ""

    def test_parse_job_text_empty(self):
        """Test parsing empty job text."""
        scraper = ConferenceScraper()
        title, company = scraper._parse_job_text("")
        assert title == ""
        assert company == ""

    def test_parse_speakers_valid_html(self, mock_html):
        """Test parsing speakers from valid HTML."""
        scraper = ConferenceScraper()
        speakers = scraper._parse_speakers(mock_html)

        assert len(speakers) == 3
        assert speakers[0]["name"] == "John Smith"
        assert speakers[0]["title"] == "Project Manager"
        assert speakers[0]["company"] == "ABC Construction"

        assert speakers[1]["name"] == "Jane Doe"
        assert speakers[1]["title"] == "CEO"
        assert speakers[1]["company"] == "Tech Corp"

        assert speakers[2]["name"] == "Bob Builder"
        assert speakers[2]["title"] == "Site Manager"
        assert speakers[2]["company"] == "BuildCo"

    def test_parse_speakers_empty_html(self):
        """Test parsing speakers from empty HTML."""
        scraper = ConferenceScraper()
        speakers = scraper._parse_speakers("<html></html>")
        assert speakers == []

    def test_parse_speakers_missing_elements(self):
        """Test parsing speakers with missing elements."""
        html = """
        <html>
            <div class="speaker-grid-details">
                <h3>John Smith</h3>
            </div>
            <div class="speaker-grid-details">
                <div class="speaker-job">CEO at Company</div>
            </div>
        </html>
        """
        scraper = ConferenceScraper()
        speakers = scraper._parse_speakers(html)

        # First speaker has name but no job info
        assert len(speakers) == 1
        assert speakers[0]["name"] == "John Smith"
        assert speakers[0]["title"] == ""
        assert speakers[0]["company"] == ""

    def test_parse_speakers_malformed_html(self):
        """Test parsing speakers from malformed HTML."""
        scraper = ConferenceScraper()
        speakers = scraper._parse_speakers("<html><div><h3>Bad HTML</h3>")
        # Should not crash, just return empty or partial results
        assert isinstance(speakers, list)