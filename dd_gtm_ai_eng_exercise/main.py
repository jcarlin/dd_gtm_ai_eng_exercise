"""
DroneDeploy GTM AI Engineering Exercise
Main pipeline for generating outbound emails to conference attendees.
"""
import asyncio
import csv
import json
import os
from pathlib import Path
from typing import List, Dict

from dotenv import load_dotenv

from utils.scraper import ConferenceScraper
from utils.llm_processor import LLMProcessor
from utils.csv_exporter import CSVExporter


async def main():
    """Main pipeline execution."""
    print("🚁 DroneDeploy GTM AI Engineering Exercise")
    print("=" * 50)

    # Load environment variables
    load_dotenv()

    # Verify required environment variables
    required_env_vars = [
        "CLASSIFICATION_MODEL",
        "EMAIL_GENERATION_MODEL"
    ]

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ ERROR: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please copy .env_sample to .env and configure your API keys and models.")
        return

    print("✅ Environment configuration loaded")

    # Define file paths
    output_dir = Path(__file__).parent / "out"
    output_dir.mkdir(exist_ok=True)
    raw_speakers_file = output_dir / "raw_speakers.json"
    email_list_file = output_dir / "email_list.csv"

    # Initialize components
    print("\n📡 Initializing pipeline components...")
    scraper = ConferenceScraper()
    llm_processor = LLMProcessor()
    csv_exporter = CSVExporter()
    print("✅ Components initialized")

    # STEP 1: Call utils/scraper.py to generate out/raw_speakers.json
    print("\n🌐 STEP 1: Scraping speaker data from Digital Construction Week...")
    speakers = await scraper.scrape_speakers()

    if not speakers:
        print("❌ No speakers found. Exiting.")
        return

    # Save raw speaker data to JSON
    with open(raw_speakers_file, 'w', encoding='utf-8') as f:
        json.dump(speakers, f, indent=2, ensure_ascii=False)

    print(f"✅ Step 1 Complete: {len(speakers)} speakers saved to {raw_speakers_file}")

    # STEP 2: Call utils/llm_processor.py to process speakers from JSON file
    print(f"\n🤖 STEP 2: Processing speakers with LLM classification and email generation...")
    processed_speakers = await llm_processor.process_speakers_from_file(str(raw_speakers_file))

    print("✅ Step 2 Complete: LLM processing finished")

    # Show classification summary
    categories = {}
    emails_generated = 0
    for speaker in processed_speakers:
        category = speaker.get('category', 'Unknown')
        categories[category] = categories.get(category, 0) + 1
        if speaker.get('email_subject'):  # Email was generated
            emails_generated += 1

    print(f"\n📊 Classification Summary:")
    for category, count in sorted(categories.items()):
        print(f"   {category}: {count}")
    print(f"   Emails generated: {emails_generated}")

    # STEP 3: Call utils/csv_exporter.py to generate out/email_list.csv
    print(f"\n📄 STEP 3: Generating final CSV output...")
    csv_exporter.export_to_csv(processed_speakers, str(email_list_file))

    print("✅ Step 3 Complete: Final CSV exported")

    # Step 4: Display sample results
    print(f"\n📧 Sample Email Results:")
    print("-" * 40)

    email_samples = [s for s in processed_speakers if s['email_subject']][:2]
    for i, speaker in enumerate(email_samples):
        print(f"\n{i+1}. {speaker['name']} ({speaker['category']})")
        print(f"   Subject: {speaker['email_subject']}")
        print(f"   Body Preview: {speaker['email_body'][:100]}...")

    print(f"\n🎉 Pipeline completed successfully!")
    print(f"📁 Output file: {email_list_file}")
    print(f"📈 Ready for Agent 3 (Validator) to test and validate results")


if __name__ == "__main__":
    asyncio.run(main())