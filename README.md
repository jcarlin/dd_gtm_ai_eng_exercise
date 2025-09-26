# DroneDeploy GTM AI Engineering Exercise

A Python-based email generation system that scrapes conference speaker data and generates personalized outbound emails using LLM technology.

## Overview

This project generates draft outbound emails to potential Digital Construction Week conference attendees, inviting them to visit DroneDeploy's booth #42 for demos and free gifts. It uses web scraping to extract speaker information and leverages Large Language Models to categorize companies and generate personalized email content.

## Key Features

- **Web Scraping**: Extracts speaker data (Name, Title, Company) from conference websites
- **AI Classification**: Uses LLM to categorize companies as Builder, Owner, Partner, Competitor, or Other
- **Email Generation**: Creates personalized subject lines and email bodies for Builder and Owner categories
- **CSV Export**: Outputs results in a structured format for outbound campaigns

## Requirements

- Python 3.8+
- Internet connection for web scraping and LLM API calls
- API key for one of the supported LLM providers (OpenAI, Google, or Anthropic)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd drone-deploy/dd_gtm_ai_eng_exercise
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env_sample .env
# Edit .env file with your API keys
```

## Usage

Run the complete pipeline:

```bash
python main.py
```

This will:
1. Scrape speaker data from the Digital Construction Week website
2. Save raw data to `out/raw_speakers.json`
3. Process speakers through LLM for company classification and save processed classfications to `speakers_with_categories.json`
4. Generate personalized emails for Builder/Owner categories
5. Export final results to `out/email_list.csv`

## Output Format

The final `out/email_list.csv` contains:
- **Speaker Name**: Full name from conference listing
- **Speaker Title**: Job title/role
- **Speaker Company**: Company name
- **Company Category**: Builder, Owner, Partner, Competitor, or Other
- **Email Subject**: Compelling subject line (Builder/Owner only)
- **Email Body**: Personalized email content (Builder/Owner only)

## Company Categories

- **Builder**: Contractors, engineers, architects, construction managers
- **Owner**: Real estate developers, property owners, facility managers
- **Partner**: Non-competing tech companies, system integrators
- **Competitor**: Direct drone/construction tech competitors
- **Other**: Academic, government, unclear roles

*Note: Email content is only generated for Builder and Owner categories.*

## Troubleshooting

**Missing API Keys**: Ensure your `.env` file contains valid API keys for your chosen LLM provider.

**Rate Limiting**: The scraper includes delays to respect website rate limits. If you encounter issues, try running again later.

**Empty Results**: Check that the conference website is accessible and hasn't changed its structure.

**LLM Errors**: Verify your API key is valid and has sufficient credits/quota.

## Development Notes

This project prioritizes working functionality over complexity, following the "keep it simple" principle for the coding exercise. The code is designed to be:
- **Idempotent**: Can be run multiple times safely
- **Environment-dependent**: All configuration via `.env` file
- **Error-validated**: Checks for required environment variables

---

*This is a coding exercise for DroneDeploy's GTM AI Engineering position.*