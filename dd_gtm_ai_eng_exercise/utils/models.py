"""
Pydantic models for type-safe validation of LLM inputs and outputs.
"""
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class Category(str, Enum):
    """Speaker category classification."""
    BUILDER = "Builder"
    OWNER = "Owner"
    PARTNER = "Partner"
    COMPETITOR = "Competitor"
    OTHER = "Other"


class CompanySize(str, Enum):
    """Company size classification."""
    SMALL = "Small"
    LARGE = "Large"
    UNKNOWN = "Unknown"


class Speaker(BaseModel):
    """Input speaker data from scraper."""
    name: str
    title: str
    company: str


class ClassificationResult(BaseModel):
    """LLM classification response."""
    category: Category
    company_size: CompanySize
    reasoning: str = Field(min_length=10)

    @field_validator('reasoning')
    @classmethod
    def reasoning_not_empty(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError("Reasoning cannot be empty")
        return v.strip()


class EmailContent(BaseModel):
    """Generated email content."""
    subject: str
    body: str


class ProcessedSpeaker(Speaker):
    """Speaker with classification and email results."""
    category: Category
    company_size: CompanySize
    reasoning: str
    email_subject: str = ""
    email_body: str = ""