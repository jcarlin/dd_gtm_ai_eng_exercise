"""
LLM processor for company classification and email generation.
Reads from out/raw_speakers.json and processes speakers.
"""
import os
import json
import random
import asyncio
import logging
from collections import Counter
from typing import List, Tuple
from pathlib import Path

from openai import AsyncOpenAI, RateLimitError
from pydantic import ValidationError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from utils.models import (
    Category,
    CompanySize,
    Speaker,
    ClassificationResult,
    EmailContent,
    ProcessedSpeaker
)


class LLMProcessor:
    def __init__(self):
        """Initialize LLM processor with environment configuration."""
        self.classification_model = os.getenv("CLASSIFICATION_MODEL")
        self.email_generation_model = os.getenv("EMAIL_GENERATION_MODEL")
        self.max_concurrent = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
        self.request_delay = float(os.getenv("REQUEST_DELAY_SECONDS", "0.5"))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"

        if not self.classification_model or not self.email_generation_model:
            raise ValueError("CLASSIFICATION_MODEL and EMAIL_GENERATION_MODEL must be set in .env")

        # Initialize OpenAI client
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Setup logger for tenacity retry logging
        self.logger = logging.getLogger(__name__)
        if self.debug:
            logging.basicConfig(level=logging.DEBUG)

        # Load templates
        self._load_templates()

        # Semaphore for rate limiting
        self._semaphore = asyncio.Semaphore(self.max_concurrent)

    def _load_templates(self):
        """Load prompt and email templates from in/ directory."""
        base_dir = Path(__file__).parent.parent

        # Load prompt template
        prompt_path = base_dir / "in" / "prompt_template.txt"
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.prompt_template = f.read()

        # Load email templates
        email_path = base_dir / "in" / "email_templates.json"
        with open(email_path, 'r', encoding='utf-8') as f:
            self.email_templates = json.load(f)

        # Known competitors list for pre-validation
        self.known_competitors = [
            'autodesk', 'bentley', 'trimble', 'plangrid', 'procore',
            'pix4d', 'skycatch', 'droneseed', 'kespry', 'measure',
            'site 1001', 'propeller aero', 'propeller'
        ]

    def _is_known_competitor(self, company_name: str) -> bool:
        """Check if company is a known competitor before LLM classification."""
        company_lower = company_name.lower()
        for competitor in self.known_competitors:
            if competitor in company_lower:
                return True
        return False

    def _extract_field_value(self, line: str, prefix: str) -> str:
        """Extract value from 'Prefix: value' or 'Prefix: [value|other]' format."""
        text = line.removeprefix(f"{prefix}:").strip()

        if text.startswith('[') and ']' in text:
            return text[1:text.index(']')].split('|')[0]
        return text

    async def classify_speaker(self, speaker: Speaker) -> ClassificationResult:
        """
        Classify a speaker into Builder/Owner/Partner/Competitor/Other category
        and determine company size using web search.

        Args:
            speaker: Speaker object with name, title, and company

        Returns:
            ClassificationResult with category, reasoning, and company_size
        """
        # Pre-validation: Check if company is a known competitor
        if self._is_known_competitor(speaker.company):
            if self.debug:
                print(f"🎯 {speaker.company} identified as known competitor (pre-validation)")
            return ClassificationResult(
                category=Category.COMPETITOR,
                company_size=CompanySize.UNKNOWN,  # Size doesn't matter for competitors
                reasoning=f"Known competitor in drone/construction software space"
            )

        try:
            return await self._classify_speaker_with_retry(speaker)
        except RateLimitError as e:
            # Always exit on rate limit errors regardless of DEBUG mode
            print(f"❌ Rate limit exceeded: {str(e)}")
            raise
        except Exception as e:
            if self.debug:
                # DEBUG=true: Fail fast - exit on any error
                print(f"❌ [DEBUG MODE] Classification failed for {speaker.name}: {str(e)}")
                raise
            else:
                # DEBUG=false: Continue processing - return default classification
                print(f"⚠️ Classification failed for {speaker.name}, using default: {str(e)}")
                return ClassificationResult(
                    category=Category.OTHER,
                    company_size=CompanySize.UNKNOWN,
                    reasoning=f"Classification failed: {str(e)}"
                )

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=4, max=60),  # 4s, 8s, 16s, 32s, 60s
        retry=retry_if_exception_type((Exception,)),  # Retry all exceptions including rate limits
        before_sleep=lambda retry_state: (
            print(f"⏳ Retry {retry_state.attempt_number} after {retry_state.outcome.exception().__class__.__name__}: waiting {retry_state.next_action.sleep} seconds...")
            if retry_state.outcome.failed else None
        ),
        reraise=True
    )
    async def _classify_speaker_with_retry(self, speaker: Speaker) -> ClassificationResult:
        """Internal method with retry logic for speaker classification."""
        async with self._semaphore:
            # Add delay for rate limiting
            await asyncio.sleep(self.request_delay)

            # Format the prompt
            prompt = self.prompt_template.format(
                company_name=speaker.company,
                speaker_name=speaker.name,
                speaker_title=speaker.title
            )

            response = await self.client.chat.completions.create(
                model=self.classification_model,
                messages=[{"role": "user", "content": prompt}],
                # temperature not supported by gpt-4o-search-preview
                # web_search_options={}  # Enable web search
            )

            content = response.choices[0].message.content.strip()

            # Validate output with Pydantic
            return self._parse_and_validate_classification(content)

    def _parse_classification_response(self, content: str) -> Tuple[str, str, str]:
        """Parse LLM classification response."""
        category = "Other"
        reasoning = "Unable to parse response"
        company_size = "Unknown"

        for line in content.split('\n'):
            line = line.strip()
            if line.startswith("Category:"):
                category = self._extract_field_value(line, "Category")
            elif line.startswith("Company Size:"):
                company_size = self._extract_field_value(line, "Company Size")
            elif line.startswith("Reasoning:"):
                reasoning = self._extract_field_value(line, "Reasoning")

        return category, reasoning, company_size

    def _parse_and_validate_classification(self, content: str) -> ClassificationResult:
        """Parse and validate LLM classification response using Pydantic."""
        category, reasoning, company_size = self._parse_classification_response(content)

        try:
            return ClassificationResult(
                category=category,
                company_size=company_size,
                reasoning=reasoning
            )
        except ValidationError:
            if self.debug:
                self.logger.debug(f"Validation failed: {content[:200]}...")
            raise

    async def generate_email(self, speaker: Speaker, category: Category, company_size: CompanySize) -> EmailContent:
        """
        Generate email subject and body for Builder/Owner categories with Large company size.

        Returns:
            EmailContent with subject and body, or empty strings for non-target categories
        """
        # Only generate emails for Builder and Owner categories with Large company size
        if category not in [Category.BUILDER, Category.OWNER] or company_size != CompanySize.LARGE:
            return EmailContent(subject="", body="")

        async with self._semaphore:
            # Add delay for rate limiting
            await asyncio.sleep(self.request_delay)

            try:
                # Get templates for the category
                templates = self.email_templates[category.value]

                # Select random subject template and generate email
                subject_template = random.choice(templates["subject_templates"])
                subject = subject_template.format(
                    speaker_name=speaker.name,
                    company_name=speaker.company,
                    speaker_title=speaker.title
                )

                body = templates["body_template"].format(
                    speaker_name=speaker.name,
                    company_name=speaker.company,
                    speaker_title=speaker.title
                )

                return EmailContent(subject=subject, body=body)

            except Exception as e:
                print(f"Error generating email for {speaker.name}: {str(e)}")
                return EmailContent(subject="", body="")

    async def process_speakers_batch(self, speakers: List[Speaker]) -> List[ProcessedSpeaker]:
        """
        Process a batch of speakers for classification and email generation.
        Uses chunked processing with semaphore for rate limiting.

        Args:
            speakers: List of Speaker objects

        Returns:
            List of ProcessedSpeaker objects with classification and email data
        """
        # Execute classifications with semaphore-based rate limiting
        print(f"Classifying {len(speakers)} speakers (category + company size)...")
        print(f"⚙️ Settings: {self.max_concurrent} concurrent, {self.request_delay}s delay between requests")

        classification_tasks = [self.classify_speaker(speaker) for speaker in speakers]
        classification_results = await asyncio.gather(*classification_tasks, return_exceptions=True)

        # Handle any exceptions in results
        valid_results = []
        for i, result in enumerate(classification_results):
            if isinstance(result, Exception):
                print(f"⚠️ Failed to classify {speakers[i].name}: {result}")
                # Use default classification for failures
                valid_results.append(ClassificationResult(
                    category=Category.OTHER,
                    company_size=CompanySize.UNKNOWN,
                    reasoning=f"Classification error: {str(result)}"
                ))
            else:
                valid_results.append(result)

        classification_results = valid_results

        # Generate emails concurrently
        print(f"Generating emails for qualifying speakers (Builder/Owner + Large companies)...")
        email_tasks = [
            self.generate_email(speaker, result.category, result.company_size)
            for speaker, result in zip(speakers, classification_results)
        ]
        email_results = await asyncio.gather(*email_tasks)

        # Build ProcessedSpeaker objects
        processed_speakers = [
            ProcessedSpeaker(
                name=speaker.name,
                title=speaker.title,
                company=speaker.company,
                category=result.category,
                company_size=result.company_size,
                reasoning=result.reasoning,
                email_subject=email.subject,
                email_body=email.body
            )
            for speaker, result, email in zip(speakers, classification_results, email_results)
        ]

        # Log category counts
        counts = Counter(s.category.value for s in processed_speakers)
        print(f"Category counts: {dict(counts)}")

        return processed_speakers

    async def process_speakers_from_file(self, raw_speakers_file: str) -> List[ProcessedSpeaker]:
        """
        Process speakers from raw_speakers.json file.

        Args:
            raw_speakers_file: Path to raw_speakers.json file

        Returns:
            List of ProcessedSpeaker objects with classification and email data
        """
        # Load speakers from JSON file and convert to Speaker objects
        with open(raw_speakers_file, 'r', encoding='utf-8') as f:
            speaker_dicts = json.load(f)

        speakers = [Speaker(**s) for s in speaker_dicts]
        print(f"📖 Loaded {len(speakers)} speakers from {raw_speakers_file}")

        # Process the speakers using existing batch method
        processed_speakers = await self.process_speakers_batch(speakers)

        # Save processed data to new file
        output_file = raw_speakers_file.replace('raw_speakers.json', 'speakers_with_categories.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            # Convert ProcessedSpeaker objects to dicts for JSON serialization
            output_data = [
                {
                    "name": s.name,
                    "title": s.title,
                    "company": s.company,
                    "category": s.category.value,
                    "company_size": s.company_size.value,
                    "reasoning": s.reasoning,
                    "email_subject": s.email_subject,
                    "email_body": s.email_body
                }
                for s in processed_speakers
            ]
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved processed speakers to {output_file}")

        return processed_speakers