"""
DroneDeploy GTM AI Engineering Exercise
Main pipeline for generating outbound emails to conference attendees.
"""
import asyncio
import csv
import os
from pathlib import Path
from typing import List, Dict

from dotenv import load_dotenv

from utils.scraper import ConferenceScraper
from utils.llm_processor import LLMProcessor


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

    # Initialize components
    print("\n📡 Initializing scraper and LLM processor...")
    scraper = ConferenceScraper()
    llm_processor = LLMProcessor()

    print("✅ Components initialized")

    # Step 1: Scrape speaker data
    print("\n🌐 Step 1: Scraping speaker data from Digital Construction Week...")
    speakers = await scraper.scrape_with_fallback_data()

    if not speakers:
        print("❌ No speaker data found. Exiting.")
        return

    print(f"✅ Found {len(speakers)} speakers")

    # Show sample of scraped data
    print("\n📋 Sample speakers:")
    for i, speaker in enumerate(speakers[:3]):
        print(f"  {i+1}. {speaker['name']} - {speaker['title']} at {speaker['company']}")
    if len(speakers) > 3:
        print(f"  ... and {len(speakers) - 3} more")

    # Step 2: Process speakers with LLM
    print(f"\n🤖 Step 2: Processing {len(speakers)} speakers with LLM...")
    print("   - Classifying companies (Builder/Owner/Partner/Competitor/Other)")
    print("   - Generating emails for Builder/Owner categories")

    processed_speakers = await llm_processor.process_speakers_batch(speakers)

    print("✅ LLM processing completed")

    # Show classification summary
    categories = {}
    emails_generated = 0
    for speaker in processed_speakers:
        category = speaker['category']
        categories[category] = categories.get(category, 0) + 1
        if speaker['email_subject']:  # Email was generated
            emails_generated += 1

    print(f"\n📊 Classification Summary:")
    for category, count in sorted(categories.items()):
        print(f"   {category}: {count}")
    print(f"   Emails generated: {emails_generated}")

    # Step 3: Generate CSV output
    print(f"\n📄 Step 3: Generating CSV output...")

    output_dir = Path(__file__).parent / "out"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "email_list.csv"

    # Define CSV columns as specified in requirements
    csv_columns = [
        "Speaker Name",
        "Speaker Title",
        "Speaker Company",
        "Company Category",
        "Email Subject",
        "Email Body"
    ]

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()

        for speaker in processed_speakers:
            writer.writerow({
                "Speaker Name": speaker['name'],
                "Speaker Title": speaker['title'],
                "Speaker Company": speaker['company'],
                "Company Category": speaker['category'],
                "Email Subject": speaker['email_subject'],
                "Email Body": speaker['email_body']
            })

    print(f"✅ CSV file generated: {output_file}")
    print(f"   Total records: {len(processed_speakers)}")
    print(f"   Records with emails: {emails_generated}")

    # Step 4: Display sample results
    print(f"\n📧 Sample Email Results:")
    print("-" * 40)

    email_samples = [s for s in processed_speakers if s['email_subject']][:2]
    for i, speaker in enumerate(email_samples):
        print(f"\n{i+1}. {speaker['name']} ({speaker['category']})")
        print(f"   Subject: {speaker['email_subject']}")
        print(f"   Body Preview: {speaker['email_body'][:100]}...")

    print(f"\n🎉 Pipeline completed successfully!")
    print(f"📁 Output file: {output_file}")
    print(f"📈 Ready for Agent 3 (Validator) to test and validate results")


if __name__ == "__main__":
    asyncio.run(main())