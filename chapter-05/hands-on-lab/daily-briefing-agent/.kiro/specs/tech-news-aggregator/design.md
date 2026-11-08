# Tech News Aggregator Design Document

## Overview

The Tech News Aggregator is a containerized Flask web application that embodies a "Witty Tech Journalist" persona, delivering curated technology news with sharp, cynical commentary. The system automatically collects stories from Hacker News, generates AI-powered summaries using Amazon Bedrock, and presents them through a clean, responsive interface.

> **Lab note**: This starter design shows the architecture the lab converges on after Phase 8 (App Runner with a VPC Connector). The book's Phase 2 constraints deliberately pin Amazon Lightsail + CloudFront first, so the spec you write will contradict this document until the Phase 8 prompt switches the deployment target. That mismatch is intended: driving the change through the spec is the point of Phase 8. When your spec and this document disagree, the spec wins.

## Architecture

### High-Level Architecture

```mermaid
graph TB
    User[User Browser] --> AppRunner[AWS App Runner]

    subgraph "VPC - Private Network"
        AppRunner --> VPCConnector[VPC Connector]

        subgraph "Private Subnets"
            Aurora[(Aurora PostgreSQL)]
        end

        subgraph "VPC Endpoints"
            S3EP[S3 Endpoint]
            BedrockEP[Bedrock Endpoint]
            SecretsEP[Secrets Manager Endpoint]
        end

        VPCConnector --> Aurora
        VPCConnector --> S3EP
        VPCConnector --> BedrockEP
        VPCConnector --> SecretsEP
    end

    S3EP --> S3[S3 Briefings Bucket]
    BedrockEP --> Bedrock[Amazon Bedrock Claude]
    SecretsEP --> Secrets[Secrets Manager]

    AppRunner --> HN[news.ycombinator.com]

    subgraph "Docker Container"
        Flask[Flask Web App]
        Scheduler[APScheduler]
        Services[Business Services]
    end
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | Jinja2 + HTML/CSS | Server-side rendering |
| Backend | Python 3.11 + Flask | Web application |
| Database | Aurora PostgreSQL | Data persistence |
| ORM | SQLAlchemy | Database abstraction |
| AI/ML | Amazon Bedrock (Claude: Haiku tier, Sonnet-tier fallback) | Summary generation |
| Storage | Amazon S3 | Briefing file storage |
| Scraping | requests + BeautifulSoup4 | Web scraping |
| Container | Docker + App Runner | Deployment |
| Secrets | AWS Secrets Manager | Credential management |

## Components and Interfaces

### Story Collector Service

- **Purpose**: Collects stories from Hacker News
- **Location**: `src/services/story_collector.py`
- **Interfaces**: HackerNews API, StoryRepository
- **Key Methods**:
  - `collect_stories() -> List[Story]`: Fetch and process new stories
  - `deduplicate_stories(stories) -> List[Story]`: Remove duplicates
  - `filter_by_quality(stories) -> List[Story]`: Apply quality filters

### Summary Generator Service

- **Purpose**: Generate witty summaries using Amazon Bedrock
- **Location**: `src/services/summary_generator.py`
- **Interfaces**: Bedrock Runtime API, StoryRepository
- **Key Methods**:
  - `generate_summary(story: Story) -> str`: Create witty summary
  - `detect_hype(content: str) -> float`: Score marketing content
  - `create_fallback(story: Story) -> str`: Fallback when AI fails

### Ranking Engine

- **Purpose**: Rank stories by importance and timeliness
- **Location**: `src/services/ranking_engine.py`
- **Interfaces**: StoryRepository
- **Key Methods**:
  - `calculate_score(story: Story) -> float`: Compute ranking score
  - `detect_breaking_news(story: Story) -> bool`: Identify urgent stories
  - `rank_feed(stories: List[Story]) -> List[Story]`: Order stories

### Briefing Generator

- **Purpose**: Create daily briefing markdown files
- **Location**: `src/services/briefing_generator.py`
- **Interfaces**: S3, StoryRepository
- **Key Methods**:
  - `generate_briefing(date: date) -> str`: Create markdown content
  - `save_to_s3(content: str, filename: str)`: Upload to S3

### Hacker News Scraper

- **Purpose**: Scrape stories from news.ycombinator.com
- **Location**: `src/scrapers/hackernews_scraper.py`
- **Interfaces**: HTTP (requests), HTML Parser (BeautifulSoup)
- **Key Methods**:
  - `fetch_top_stories(limit: int) -> List[Dict]`: Get top stories
  - `parse_story(html: str) -> Story`: Parse story HTML

### Web Application Controller

- **Purpose**: Handle HTTP requests and render pages
- **Location**: `src/web/routes.py`
- **Interfaces**: Flask routes, Templates
- **Key Endpoints**:
  - `GET /`: Main feed page
  - `GET /story/{id}`: Individual story view
  - `GET /api/stories`: JSON API for stories
  - `GET /api/briefings`: List available briefings

## Data Models

### Story Model

```python
from sqlalchemy import Column, String, DateTime, Text, Float, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

class Story(Base):
    __tablename__ = 'stories'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    original_url = Column(Text, nullable=False)
    source = Column(String(100), nullable=False, default='hackernews')
    published_at = Column(DateTime, nullable=False)
    collected_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    content = Column(Text, default='')
    summary = Column(Text, default='')
    score = Column(Float, default=0.0, index=True)
    is_breaking = Column(Boolean, default=False, index=True)
    hn_score = Column(Integer, nullable=True)
    hn_comments = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Source Model

```python
class Source(Base):
    __tablename__ = 'sources'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    url = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    reliability_score = Column(Float, default=1.0)
    last_checked = Column(DateTime, nullable=True)
    scraping_config = Column(JSON, nullable=True)
```

### SummaryMetadata Model

```python
class SummaryMetadata(Base):
    __tablename__ = 'summary_metadata'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(UUID(as_uuid=True), ForeignKey('stories.id'), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    model_used = Column(String(100), nullable=True)
    token_count = Column(Integer, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    hype_score = Column(Float, nullable=True)
```

## Amazon Bedrock Integration

### Model Configuration

Model identifiers are read from the environment, never hardcoded. Bedrock's Claude
lineup changes, and the bedrock-runtime APIs take an inference profile ID for current
Claude models, so confirm the IDs on the model cards in the Bedrock documentation
before deploying (`.env.example` has the details). Anthropic models also need a
one-time use-case form per AWS account before the first call. Current Claude models on Bedrock accept only the default sampling settings, so requests leave out temperature, top_p, and top_k. They also think by default: a response can start with a thinking block, so read the summary from the content block whose type is text rather than content[0], and leave max_tokens room for the thinking.

```python
BEDROCK_CONFIG = {
    'primary_model': {
        # e.g. global.anthropic.claude-haiku-5-5
        'model_id': os.environ['BEDROCK_MODEL_ID'],
        'max_tokens': 4096
    },
    'fallback_model': {
        'model_id': os.environ['BEDROCK_FALLBACK_MODEL_ID'],
        'max_tokens': 4096
    },
    'region': os.getenv('AWS_REGION', 'us-east-1')
}
```

### Prompt Template

```python
SUMMARY_PROMPT = """You are a Witty Tech Journalist. Your tone is sharp, concise,
and slightly cynical. You prioritize substance over hype.

Summarize this tech story in 2-3 sentences. Be skeptical of marketing language.
Cut through the hype and deliver the actual news.

Story Title: {title}
Story Content: {content}

Your witty summary:"""
```

## Error Handling

### Error Hierarchy

```python
class DailyBriefingError(Exception):
    """Base exception for application"""
    pass

class ScrapingError(DailyBriefingError):
    """Error during web scraping"""
    pass

class SummaryGenerationError(DailyBriefingError):
    """Error generating AI summary"""
    pass

class DatabaseError(DailyBriefingError):
    """Database operation error"""
    pass
```

### Retry Strategy

```python
RETRY_CONFIG = {
    'max_retries': 3,
    'base_delay': 1.0,  # seconds
    'max_delay': 30.0,
    'exponential_base': 2
}
```

## Security Configuration

### IAM Policy (App Runner Service Role)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": ["bedrock:InvokeModel"],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/anthropic.claude-*",
                "arn:aws:bedrock:*:*:inference-profile/*anthropic.claude-*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": ["secretsmanager:GetSecretValue"],
            "Resource": ["arn:aws:secretsmanager:*:*:secret:daily-briefing/*"]
        },
        {
            "Effect": "Allow",
            "Action": ["s3:GetObject", "s3:PutObject"],
            "Resource": ["arn:aws:s3:::daily-briefing-*/*"]
        }
    ]
}
```

## Testing Strategy

### Test Layers

| Layer | Framework | Purpose |
|-------|-----------|---------|
| Unit | pytest + moto | Fast, isolated tests |
| Property | Hypothesis | Correctness validation |
| Integration | LocalStack | AWS service simulation |
| Browser | Playwright | UI testing |

### LocalStack Configuration

```yaml
# docker-compose.localstack.yml
services:
  localstack:
    image: localstack/localstack
    ports:
      - "4566:4566"
    environment:
      - SERVICES=s3,secretsmanager
      - DEBUG=1
      - LOCALSTACK_AUTH_TOKEN=${LOCALSTACK_AUTH_TOKEN:?}
```

## Deployment

### Environment Variables

```bash
# Required
DATABASE_URL=postgresql://user:pass@host:5432/db
AWS_REGION=us-east-1

# Optional
FLASK_ENV=production
LOG_LEVEL=INFO
BEDROCK_MODEL_ID=global.anthropic.claude-haiku-5-5
```

### Health Check Endpoint

```python
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': os.getenv('APP_VERSION', 'unknown')
    })
```
