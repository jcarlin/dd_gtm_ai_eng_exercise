# MULTI_AGENT_PLAN.md

## Project Overview: DroneDeploy GTM AI Engineering Exercise

**Objective**: Generate draft outbound emails to DroneDeploy's potential construction conference attendees to invite them to booth #42 for demos and free gifts.

**Conference**: Digital Construction Week (https://www.digitalconstructionweek.com/all-speakers/)

**Timeline**: 2 hours maximum

**CRITICAL: KEEP IT SIMPLE!**
This is a coding exercise - prioritize working functionality over complexity. Use the most straightforward approach possible.

## Requirements Analysis

### Target Audience Categorization
- **Builders**: General contractors, specialty contractors, engineering firms
- **Owners**: Organizations getting things built for them
- **Exclude**: Competitors and potential partners

**Classification Approach**: LLM must classify BOTH company AND speaker role using this logic:

**Step 1 - Company Classification:**
- **Competitor**: Direct drone/construction tech competitors (Autodesk, Bentley, Trimble, PlanGrid, Procore, Pix4D, etc.)
- **Partner**: Cloud platforms, system integrators, non-competing tech companies
- Continue to Step 2 if not Competitor/Partner

**Step 2 - Builder vs Owner (by job title):**
- **Builder**: Construction Manager, Project Manager, Engineer, Architect, Contractor, Superintendent, Site Manager, BIM Manager
- **Owner**: Real Estate Developer, Property Developer, Facility Manager, Asset Manager, Owner's Representative, Development Manager
- **Other**: Academic, government, unclear roles

**Final Categories**: Builder, Owner, Partner, Competitor, Other
**Email Generation**: ONLY for Builder/Owner categories (leave empty for Partner/Competitor/Other)

All speakers included in CSV, but only Builder/Owner receive email content.

### Required Technologies
- Python
- Asyncio
- aiohttp (async HTTP client)
- BeautifulSoup4 (HTML parsing)
- LiteLLM (LLM integration - OpenAI, Google, Anthropic)
- LangChain (optional prompt management framework)
- pandas (data processing and CSV generation)
- python-dotenv (environment variables from .env file)

### Output Specifications
CSV file (`email_list.csv`) with columns:
1. Speaker Name
2. Speaker Title
3. Speaker Company
4. Company Category (Builder, Owner, Partner, Competitor, Other)
5. Email Subject (compelling hook)
6. Email Body (personalized pitch for booth visit)

### STRICT REQUIREMENT: Folder Structure
**This folder structure is MANDATORY and must be followed exactly:**
```
dd_gtm_ai_eng_exercise/
   .env_sample
   main.py
   README.md
   in/
   out/
      email_list.csv
   utils/
```

**CRITICAL REQUIREMENT**: All agents must strictly adhere to this exact folder structure:
- `.env_sample`: Sample .env file with API key variables
- `main.py`: Main python file to run the pipeline
- `README.md`: Basic setup/run instructions
- `in/`: Input folder containing templates and prompts
- `out/`: Output folder containing email_list.csv
- `utils/`: Helper functions

**NO DEVIATIONS FROM THIS STRUCTURE ARE PERMITTED.**

## Technical Architecture

### Data Flow
1. **Web Scraping**: Extract speaker data (Name, Title, Company) from conference website, save to `out/raw_speakers.json`
2. **LLM Processing**: Read from `out/raw_speakers.json`, classify companies and generate emails
3. **Classification**: Categorize each company using LLM built-in knowledge (Builder/Owner/Partner/Competitor/Other)
4. **Email Generation**: Generate subject/body ONLY for Builder/Owner categories (leave empty for Partner/Competitor)
5. **CSV Export**: Save final results to `out/email_list.csv` with all required columns

### Technology Stack
- **Web Scraping**: aiohttp + BeautifulSoup4 (already implemented)
- **LLM Integration**: LiteLLM + LangChain
- **Data Processing**: pandas
- **Environment Management**: python-dotenv
- **Async Processing**: asyncio

### Current State Assessment
- Basic scraper utility already exists (`utils/scraper.py`)
- Requirements.txt needs updates for LiteLLM and LangChain
- Missing LLM integration and email generation components

## Multi-Agent Workflow Plan

### Agent 1 (Architect) - COMPLETED
**Role**: Research & Planning
**Deliverables**:
- Requirements analysis
- Technical architecture design
- Multi-agent task breakdown
- This comprehensive plan document

---

### Agent 2 (Builder) - COMPLETED (Initial Implementation)
**Role**: Core Implementation
**Status**: ✅ COMPLETED
**Primary Tasks**:
1. **Environment Setup**
   - Create .env_sample file
   - Create input files in `in/` folder

2. **Input Files** (in `in/` directory):
   - `prompt_template.txt`: LLM classification prompt with DroneDeploy context
   - `email_templates.json`: Email subject/body templates for Builder/Owner categories
   - `example_speaker.json`: Example speaker data showing expected parsing format

3. **Utils Modules**:
   - `utils/scraper.py`: Web scraping functionality (extract Name, Title, Company from conference website)
   - `utils/llm_processor.py`: Read from `out/raw_speakers.json`, classify companies, generate emails for Builder/Owner only
   - `utils/csv_exporter.py`: Generate final CSV from processed data

4. **Main Application** (`main.py`)
   - Orchestrate complete pipeline:
     1. Call `utils/scraper.py` to generate `out/raw_speakers.json`
     2. Call `utils/llm_processor.py` to process speakers from JSON file
     3. Call `utils/csv_exporter.py` to generate `out/email_list.csv`
   - Async processing workflow

**Technical Specifications** (SIMPLE APPROACH):
- Use LiteLLM for LLM access
- Basic async processing
- Minimal error handling
- Focus on working solution over sophistication
- **NO FALLBACKS**: Code must use .env values only, NO hardcoded API keys or model names in code
- **IDEMPOTENT**: Program must be able to run multiple times, overwriting contents in `out/` directory
- **ENV VALIDATION**: Program must validate required .env values are present and error with appropriate message if undefined

**Expected Deliverables**: ✅ ALL COMPLETED
- ✅ `main.py`: Complete pipeline orchestration
- ✅ `utils/scraper.py`: Web scraping, outputs to `out/raw_speakers.json`
- ✅ `utils/llm_processor.py`: Reads `out/raw_speakers.json`, does LLM classification and email generation
- ✅ `utils/csv_exporter.py`: Generates final `out/email_list.csv` from processed data
- ✅ `in/prompt_template.txt`: LLM classification prompt
- ✅ `in/email_templates.json`: Email templates for Builder/Owner
- ✅ `in/example_speaker.json`: Example showing correct name/title/company parsing
- ✅ `.env_sample`: API key variables (NO hardcoded values in code!)
- ✅ `out/raw_speakers.json`: Scraped speaker data in JSON format
- ✅ `out/email_list.csv`: Final output with all required columns

---

### Agent 2 (Builder) - PRODUCTION-READY IMPROVEMENTS
**NEW TASK**: Upgrade LLM Communication for Production Readiness

**Objective**: Add Pydantic validation and tenacity retry logic to make the system more robust and production-ready while maintaining compatibility with `gpt-4o-search-preview`.

**Background**:
- Current implementation uses string templates with manual text parsing (fragile)
- No retry logic for transient failures
- gpt-4o-search-preview does NOT support structured outputs (json_schema)
- Must use text-based prompts + Pydantic validation hybrid approach

#### Implementation Plan

**1. Create `utils/models.py`**
```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal

class ClassificationRequest(BaseModel):
    """Input data for speaker classification."""
    company_name: str
    speaker_name: str
    speaker_title: str

class ClassificationResponse(BaseModel):
    """Validated LLM classification response."""
    category: Literal["Builder", "Owner", "Partner", "Competitor", "Other"]
    company_size: Literal["Small", "Large", "Unknown"]
    reasoning: str = Field(min_length=10, description="Explanation for classification")

    @field_validator('reasoning')
    @classmethod
    def reasoning_not_empty(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError("Reasoning cannot be empty")
        return v.strip()
```

**Key Design:**
- Use `Literal` types for enum validation
- Field validators ensure quality responses
- Simple models - validation only, no business logic

**2. Update `requirements.txt`**
Add dependencies:
```txt
pydantic>=2.0.0
tenacity>=8.0.0
```

**3. Update `.env_sample`**
Add DEBUG configuration:
```bash
# Debug Configuration
DEBUG=false  # Set to true for detailed retry logging
```

**4. Update `utils/llm_processor.py`**

**New Imports:**
```python
import logging
from pydantic import ValidationError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
from utils.models import ClassificationRequest, ClassificationResponse
```

**Update `__init__` Method:**
- Add `self.debug` flag from environment
- Setup logger for tenacity retry logging

**Update `classify_speaker` Method:**
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((Exception,)),
    before_sleep=lambda retry_state: (
        logging.getLogger(__name__).debug(
            f"Retry attempt {retry_state.attempt_number} after error: {retry_state.outcome.exception()}"
        ) if os.getenv("DEBUG", "false").lower() == "true" else None
    ),
    reraise=True
)
async def classify_speaker(self, speaker_name: str, speaker_title: str, company_name: str) -> Tuple[str, str, str]:
    # Validate input with Pydantic
    request = ClassificationRequest(...)

    # Make LLM call (existing logic)
    # Parse response (existing logic)

    # Validate output with Pydantic
    validated = self._parse_and_validate_classification(content)

    return (validated.category, validated.reasoning, validated.company_size)
```

**Add New Method `_parse_and_validate_classification`:**
- Parse text response (keep existing parsing logic)
- Validate with Pydantic `ClassificationResponse`
- Raises `ValidationError` on invalid data (triggers retry)

#### Retry Strategy

**Retry Behavior:**
- ✅ Retry on: `RateLimitError`, `Timeout`, `APIConnectionError`, `ValidationError` (all exceptions for now)
- ❌ Don't retry: None initially (can refine later)
- **Max 3 attempts** (1 original + 2 retries)
- **Exponential backoff**: 2-10 seconds between attempts
- **DEBUG mode**: Logs each retry attempt with error details

**Token Efficiency:**
- Only retries on failures (not multiple sampling)
- Max 3 attempts prevents excessive token usage
- Exponential backoff respects rate limits

#### Key Design Decisions

1. **Hybrid Approach**: Text prompts + Pydantic validation (not json_schema)
   - Reason: gpt-4o-search-preview has compatibility issues with structured outputs
   - Maintains web search capability for company size lookup

2. **Retry All Exceptions**: Catch-all retry initially
   - Can be refined later to skip unrecoverable errors (auth failures, etc.)
   - Simple and robust for production readiness

3. **Backward Compatible**:
   - No changes to `main.py` required
   - Existing method signatures preserved
   - Only internal validation/retry logic added

4. **DEBUG Flag**:
   - Production: No retry logging (clean output)
   - Debug: Detailed logs for troubleshooting
   - No token waste on excessive logging

#### Implementation Order

1. Create `utils/models.py` first (defines contracts)
2. Update `requirements.txt` (install dependencies)
3. Update `.env_sample` (add DEBUG flag)
4. Update `utils/llm_processor.py`:
   - Add imports
   - Update `__init__` method
   - Add `_parse_and_validate_classification` method
   - Update `classify_speaker` with retry decorator

#### Testing Checklist

- [ ] Test with `DEBUG=true` to verify retry logging works
- [ ] Test with malformed LLM responses (trigger validation errors)
- [ ] Verify exponential backoff timing (2s, 4s, 8s)
- [ ] Confirm existing functionality preserved (classification + email generation)
- [ ] Validate no changes needed to `main.py`

#### Success Criteria

- Type-safe input/output validation with Pydantic
- Intelligent retry logic handles transient failures
- DEBUG flag provides visibility without token waste
- Backward compatible with existing pipeline
- Production-ready error handling

**Expected Time**: 30-45 minutes for implementation and testing

---

### Agent 3 (Validator) - AFTER BUILDER
**Role**: Testing & Validation
**Restrictions**: Cannot edit source code, only tests and validation

**Primary Tasks**:
1. **Test Suite Creation**
   - Unit tests for scraper functionality
   - LLM classification accuracy tests
   - Email generation quality tests
   - Integration tests for full pipeline

2. **Data Validation**
   - Speaker data completeness checks
   - Company categorization accuracy review
   - Email content quality assessment
   - CSV format validation

3. **Performance Testing**
   - Async processing efficiency
   - API rate limiting compliance
   - Memory usage optimization
   - Error handling robustness

**Expected Deliverables**:
- Comprehensive test suite
- Validation reports
- Performance benchmarks
- Issue reports for Builder to address

---

### Agent 4 (Scribe) - FINAL
**Role**: Documentation & Refinement
**Primary Tasks**:
1. **README.md Creation**
   - Setup and installation instructions
   - Usage guide with examples
   - Configuration details
   - Troubleshooting guide

2. **Code Documentation**
   - Inline code comments
   - Docstring improvements
   - Type hints validation
   - API documentation

3. **Example Materials**
   - Sample .env configuration
   - Example output files
   - Usage scenarios
   - Best practices guide

**Expected Deliverables**:
- Professional README.md
- Complete code documentation
- User-friendly examples
- Final code refinements

## Implementation Priorities

### Phase 1 (Agent 2 - Builder) - SIMPLE APPROACH
1. **Critical**: Basic scraper + LLM classification + email templates
2. **Skip**: Complex error handling, advanced personalization, optimization

### Phase 2 (Agent 3 - Validator) - SIMPLE APPROACH
1. **Critical**: Verify CSV output format is correct
2. **Skip**: Complex performance testing, extensive edge case handling

### Phase 3 (Agent 4 - Scribe) - SIMPLE APPROACH
1. **Critical**: Basic README with setup/run instructions
2. **Skip**: Advanced documentation, complex examples

## Risk Assessment & Mitigation

### Technical Risks
- **Rate Limiting**: Implement respectful scraping delays
- **LLM Costs**: Use efficient prompting and caching
- **Data Quality**: Robust parsing with fallbacks
- **API Changes**: Error handling for website changes

### Time Constraints
- **2-hour limit**: Focus on core functionality first
- **MVP approach**: Basic working solution over perfect polish
- **Parallel work**: Agents work simultaneously where possible

## Success Criteria

### Minimum Viable Product
- Successfully scrape speaker data
- Categorize companies accurately (>80% accuracy)
- Generate personalized email content
- Export clean CSV with all required columns
- Clear setup and usage instructions

### Stretch Goals
- Advanced personalization based on speaker roles
- Multiple email template variations
- Confidence scoring for classifications
- Batch processing optimization

## Questions Answered

**Q: Can all requirements be accomplished with the specified technologies?**
**A: Yes, absolutely.** The technology stack (Python, Asyncio, LLM via LiteLLM, LangChain) is perfectly suited for this task:

- **Web Scraping**: Python + asyncio + aiohttp (already implemented)
- **LLM Integration**: LiteLLM provides unified access to OpenAI, Google, Anthropic
- **Framework**: LangChain offers excellent prompt management and chain orchestration
- **Data Processing**: pandas for CSV manipulation
- **Environment**: .env for secure API key management

**Q: Any additional questions or concerns?**
- Conference timing (already passed) - confirmed this is for exercise purposes only
- API costs will be minimal for ~200 speakers
- Current scraper foundation provides good starting point
- LangChain + LiteLLM combination offers flexibility and robustness

## Next Steps

### ✅ Phase 1 Complete: Initial Implementation
Agent 2 (Builder) has completed the initial implementation including:
- ✅ LLM integration setup
- ✅ Company categorization logic
- ✅ Email generation pipeline
- ✅ Main orchestration script

### 🔄 Phase 2 In Progress: Production-Ready Improvements
Agent 2 (Builder) should now implement production-ready improvements:
1. Create Pydantic models for type-safe validation
2. Add tenacity retry logic for robustness
3. Implement DEBUG flag for visibility
4. Maintain backward compatibility

See **Agent 2 (Builder) - PRODUCTION-READY IMPROVEMENTS** section above for detailed implementation plan.

**Expected Time**: 30-45 minutes

The architecture is sound and all requirements have been successfully implemented.
