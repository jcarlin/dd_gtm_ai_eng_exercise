"""Pytest configuration and shared fixtures."""
import pytest
import json
from pathlib import Path


@pytest.fixture
def sample_speakers():
    """Sample speaker data for testing."""
    return [
        {"name": "John Smith", "title": "Project Manager", "company": "ABC Construction"},
        {"name": "Jane Doe", "title": "CEO", "company": "Tech Corp"},
        {"name": "Bob Builder", "title": "Site Manager", "company": "BuildCo"}
    ]


@pytest.fixture
def mock_html():
    """Mock HTML from Digital Construction Week website."""
    return """
    <html>
        <div class="speaker-grid-details">
            <h3>John Smith</h3>
            <div class="speaker-job">Project Manager at ABC Construction</div>
        </div>
        <div class="speaker-grid-details">
            <h3>Jane Doe</h3>
            <div class="speaker-job">CEO - Tech Corp</div>
        </div>
        <div class="speaker-grid-details">
            <h3>Bob Builder</h3>
            <div class="speaker-job">Site Manager, BuildCo</div>
        </div>
    </html>
    """


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory for tests."""
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def sample_processed_speakers():
    """Sample processed speaker data with classifications."""
    from utils.models import ProcessedSpeaker, Category, CompanySize

    return [
        ProcessedSpeaker(
            name="John Smith",
            title="Project Manager",
            company="ABC Construction",
            category=Category.BUILDER,
            company_size=CompanySize.LARGE,
            reasoning="Construction company with project management focus",
            email_subject="See DroneDeploy at DCW Booth #42",
            email_body="Hi John, stop by our booth..."
        ),
        ProcessedSpeaker(
            name="Jane Doe",
            title="CEO",
            company="Tech Corp",
            category=Category.PARTNER,
            company_size=CompanySize.LARGE,
            reasoning="Technology partner company",
            email_subject="",
            email_body=""
        ),
        ProcessedSpeaker(
            name="Bob Builder",
            title="Site Manager",
            company="BuildCo",
            category=Category.BUILDER,
            company_size=CompanySize.SMALL,
            reasoning="Small construction company",
            email_subject="",
            email_body=""
        )
    ]