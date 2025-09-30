"""Tests for Pydantic models."""
import pytest
from pydantic import ValidationError
from utils.models import (
    Category,
    CompanySize,
    Speaker,
    ClassificationResult,
    EmailContent,
    ProcessedSpeaker
)


class TestCategory:
    """Test Category enum."""

    def test_valid_categories(self):
        """Test all valid category values."""
        assert Category.BUILDER.value == "Builder"
        assert Category.OWNER.value == "Owner"
        assert Category.PARTNER.value == "Partner"
        assert Category.COMPETITOR.value == "Competitor"
        assert Category.OTHER.value == "Other"


class TestCompanySize:
    """Test CompanySize enum."""

    def test_valid_sizes(self):
        """Test all valid company size values."""
        assert CompanySize.SMALL.value == "Small"
        assert CompanySize.LARGE.value == "Large"
        assert CompanySize.UNKNOWN.value == "Unknown"


class TestSpeaker:
    """Test Speaker model."""

    def test_valid_speaker(self):
        """Test creating a valid speaker."""
        speaker = Speaker(
            name="John Smith",
            title="Project Manager",
            company="ABC Construction"
        )
        assert speaker.name == "John Smith"
        assert speaker.title == "Project Manager"
        assert speaker.company == "ABC Construction"

    def test_empty_fields_allowed(self):
        """Test that empty strings are allowed for optional fields."""
        speaker = Speaker(name="John", title="", company="")
        assert speaker.title == ""
        assert speaker.company == ""


class TestClassificationResult:
    """Test ClassificationResult model."""

    def test_valid_classification(self):
        """Test creating a valid classification result."""
        result = ClassificationResult(
            category=Category.BUILDER,
            company_size=CompanySize.LARGE,
            reasoning="This is a valid reasoning with enough characters"
        )
        assert result.category == Category.BUILDER
        assert result.company_size == CompanySize.LARGE
        assert len(result.reasoning) >= 10

    def test_reasoning_too_short(self):
        """Test that reasoning must be at least 10 characters."""
        with pytest.raises(ValidationError) as exc_info:
            ClassificationResult(
                category=Category.BUILDER,
                company_size=CompanySize.LARGE,
                reasoning="short"
            )
        assert "reasoning" in str(exc_info.value).lower()

    def test_reasoning_empty(self):
        """Test that empty reasoning is rejected."""
        with pytest.raises(ValidationError):
            ClassificationResult(
                category=Category.BUILDER,
                company_size=CompanySize.LARGE,
                reasoning=""
            )

    def test_reasoning_whitespace_stripped(self):
        """Test that reasoning whitespace is stripped."""
        result = ClassificationResult(
            category=Category.BUILDER,
            company_size=CompanySize.LARGE,
            reasoning="  Valid reasoning text  "
        )
        assert result.reasoning == "Valid reasoning text"

    def test_invalid_category(self):
        """Test that invalid category values are rejected."""
        with pytest.raises(ValidationError):
            ClassificationResult(
                category="InvalidCategory",
                company_size=CompanySize.LARGE,
                reasoning="Valid reasoning"
            )

    def test_invalid_company_size(self):
        """Test that invalid company size values are rejected."""
        with pytest.raises(ValidationError):
            ClassificationResult(
                category=Category.BUILDER,
                company_size="InvalidSize",
                reasoning="Valid reasoning"
            )


class TestEmailContent:
    """Test EmailContent model."""

    def test_valid_email(self):
        """Test creating valid email content."""
        email = EmailContent(
            subject="Test Subject",
            body="Test email body"
        )
        assert email.subject == "Test Subject"
        assert email.body == "Test email body"

    def test_empty_email(self):
        """Test that empty email content is allowed."""
        email = EmailContent(subject="", body="")
        assert email.subject == ""
        assert email.body == ""


class TestProcessedSpeaker:
    """Test ProcessedSpeaker model."""

    def test_valid_processed_speaker(self):
        """Test creating a valid processed speaker."""
        speaker = ProcessedSpeaker(
            name="John Smith",
            title="Project Manager",
            company="ABC Construction",
            category=Category.BUILDER,
            company_size=CompanySize.LARGE,
            reasoning="Construction company with PM focus",
            email_subject="Visit our booth",
            email_body="Hi John, we'd love to see you..."
        )
        assert speaker.name == "John Smith"
        assert speaker.category == Category.BUILDER
        assert speaker.company_size == CompanySize.LARGE
        assert speaker.email_subject == "Visit our booth"

    def test_processed_speaker_without_email(self):
        """Test processed speaker without email (non-target category)."""
        speaker = ProcessedSpeaker(
            name="Jane Doe",
            title="CEO",
            company="Tech Corp",
            category=Category.PARTNER,
            company_size=CompanySize.LARGE,
            reasoning="Technology partner",
            email_subject="",
            email_body=""
        )
        assert speaker.email_subject == ""
        assert speaker.email_body == ""

    def test_processed_speaker_defaults(self):
        """Test that email fields default to empty strings."""
        speaker = ProcessedSpeaker(
            name="Bob Builder",
            title="Manager",
            company="BuildCo",
            category=Category.BUILDER,
            company_size=CompanySize.SMALL,
            reasoning="Small construction company"
        )
        assert speaker.email_subject == ""
        assert speaker.email_body == ""
