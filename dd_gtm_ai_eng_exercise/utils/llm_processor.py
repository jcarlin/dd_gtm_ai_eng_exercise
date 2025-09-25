"""
LLM processor for company classification and email generation.
"""
import os
import json
import random
import asyncio
from typing import Dict, List, Optional, Tuple
from pathlib import Path

import litellm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMProcessor:
    def __init__(self):
        """Initialize LLM processor with environment configuration."""
        self.classification_model = os.getenv("CLASSIFICATION_MODEL")
        self.email_generation_model = os.getenv("EMAIL_GENERATION_MODEL")
        self.max_concurrent = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
        self.request_delay = float(os.getenv("REQUEST_DELAY_SECONDS", "0.5"))

        if not self.classification_model or not self.email_generation_model:
            raise ValueError("CLASSIFICATION_MODEL and EMAIL_GENERATION_MODEL must be set in .env")

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

    async def classify_speaker(self, speaker_name: str, speaker_title: str, company_name: str) -> Tuple[str, str]:
        """
        Classify a speaker into Builder/Owner/Partner/Competitor/Other category.

        Returns:
            Tuple of (category, reasoning)
        """
        async with self._semaphore:
            # Add delay for rate limiting
            await asyncio.sleep(self.request_delay)

            # Format the prompt
            prompt = self.prompt_template.format(
                company_name=company_name,
                speaker_name=speaker_name,
                speaker_title=speaker_title
            )

            try:
                response = await litellm.acompletion(
                    model=self.classification_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1  # Low temperature for consistent classification
                )

                content = response.choices[0].message.content.strip()

                # Parse the response
                category, reasoning = self._parse_classification_response(content)
                return category, reasoning

            except Exception as e:
                print(f"Error classifying {speaker_name}: {str(e)}")
                return "Other", f"Classification failed: {str(e)}"

    def _parse_classification_response(self, content: str) -> Tuple[str, str]:
        """Parse LLM classification response."""
        lines = content.split('\n')
        category = "Other"
        reasoning = "Unable to parse response"

        for line in lines:
            line = line.strip()
            if line.startswith("Category:"):
                category_text = line.replace("Category:", "").strip()
                # Extract category name, handle brackets
                if '[' in category_text and ']' in category_text:
                    category = category_text.split('[')[1].split(']')[0].split('|')[0]
                else:
                    category = category_text
            elif line.startswith("Reasoning:"):
                reasoning = line.replace("Reasoning:", "").strip()

        # Validate category
        valid_categories = ["Builder", "Owner", "Partner", "Competitor", "Other"]
        if category not in valid_categories:
            category = "Other"

        return category, reasoning

    async def generate_email(self, speaker_name: str, speaker_title: str,
                           company_name: str, category: str) -> Tuple[str, str]:
        """
        Generate email subject and body for Builder/Owner categories.

        Returns:
            Tuple of (subject, body) or ("", "") for non-target categories
        """
        # Only generate emails for Builder and Owner categories
        if category not in ["Builder", "Owner"]:
            return "", ""

        async with self._semaphore:
            # Add delay for rate limiting
            await asyncio.sleep(self.request_delay)

            try:
                # Get templates for the category
                templates = self.email_templates[category]

                # Select random subject template
                subject_template = random.choice(templates["subject_templates"])
                subject = subject_template.format(
                    speaker_name=speaker_name,
                    company_name=company_name,
                    speaker_title=speaker_title
                )

                # Generate body from template
                body = templates["body_template"].format(
                    speaker_name=speaker_name,
                    company_name=company_name,
                    speaker_title=speaker_title
                )

                return subject, body

            except Exception as e:
                print(f"Error generating email for {speaker_name}: {str(e)}")
                return "", ""

    async def process_speakers_batch(self, speakers: List[Dict]) -> List[Dict]:
        """
        Process a batch of speakers for classification and email generation.

        Args:
            speakers: List of dicts with keys: name, title, company

        Returns:
            List of dicts with additional keys: category, reasoning, email_subject, email_body
        """
        # Create tasks for classification
        classification_tasks = []
        for speaker in speakers:
            task = self.classify_speaker(
                speaker_name=speaker["name"],
                speaker_title=speaker["title"],
                company_name=speaker["company"]
            )
            classification_tasks.append(task)

        # Execute classifications concurrently
        print(f"Classifying {len(speakers)} speakers...")
        classification_results = await asyncio.gather(*classification_tasks)

        # Add classification results to speaker data
        for speaker, (category, reasoning) in zip(speakers, classification_results):
            speaker["category"] = category
            speaker["reasoning"] = reasoning

        # Generate emails for Builder/Owner categories
        email_tasks = []
        for speaker in speakers:
            task = self.generate_email(
                speaker_name=speaker["name"],
                speaker_title=speaker["title"],
                company_name=speaker["company"],
                category=speaker["category"]
            )
            email_tasks.append(task)

        print(f"Generating emails for qualifying speakers...")
        email_results = await asyncio.gather(*email_tasks)

        # Add email results to speaker data
        for speaker, (subject, body) in zip(speakers, email_results):
            speaker["email_subject"] = subject
            speaker["email_body"] = body

        return speakers