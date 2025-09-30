# DroneDeploy GTM AI Engineering Exercise

Generate targeted outbound emails for Digital Construction Week conference attendees.

## Overview

This system scrapes speaker data from Digital Construction Week, classifies companies using LLM, and generates personalized emails for potential DroneDeploy customers (Builder and Owner categories only).

## Quick Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env_sample .env
   # Edit .env with your API keys and model preferences
   ```

3. **Run the pipeline**:
   ```bash
   python main.py
   ```

## Output

The system generates `out/email_list.csv` with columns:
- Speaker Name
- Speaker Title
- Speaker Company
- Company Category (Builder/Owner/Partner/Competitor/Other)
- Email Subject (only for Builder/Owner)
- Email Body (only for Builder/Owner)

## Configuration

Edit `.env` to configure:
- API keys for your preferred LLM provider
- Model selection (defaults to gpt-3.5-turbo)
- Rate limiting settings

## Categories

- **Builder**: Construction professionals (contractors, engineers, project managers)
- **Owner**: Property/facility owners (developers, asset managers)
- **Partner**: Potential partners (cloud platforms, system integrators)
- **Competitor**: Direct competitors (Autodesk, Procore, Trimble, etc.)
- **Other**: Academic, government, unclear roles

## Company Size Filtering

The system classifies companies by size using web search:
- **Large**: 500+ employees (emails generated)
- **Small**: <500 employees (no emails)
- **Unknown**: Cannot determine size (no emails)

Only Builder and Owner categories with Large company size receive email content.