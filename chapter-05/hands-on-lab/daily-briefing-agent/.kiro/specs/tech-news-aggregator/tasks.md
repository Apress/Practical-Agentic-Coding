# Implementation Plan

## MVP 1: Local Development Foundation

- [ ] 1. Set up project structure and development environment
  - Create Python project structure (src/, tests/, infrastructure/)
  - Set up requirements.txt with dependencies
  - Configure pytest with coverage reporting (70% minimum)
  - Create .gitignore for Python projects
  - _Requirements: 6, 8_

- [ ] 2. Implement core data models
  - [ ] 2.1 Create Pydantic models
    - Write Story, Source, SummaryMetadata models in src/models/
    - Add validation and type hints
    - _Requirements: 1, 2_

  - [ ] 2.2 Implement SQLAlchemy ORM models
    - Create database models matching Pydantic schemas
    - Add indexes for frequently queried fields
    - _Requirements: 6_

  - [ ] 2.3 Write unit tests for models
    - Test model validation
    - Test serialization/deserialization
    - _Requirements: 8_

- [ ] 3. Implement Hacker News scraper
  - [ ] 3.1 Create HackerNewsScraper class
    - Fetch stories from news.ycombinator.com
    - Extract title, URL, score, comments
    - Add rate limiting and error handling
    - _Requirements: 2_

  - [ ] 3.2 Implement content filtering
    - Create quality scoring algorithm
    - Filter low-quality content
    - _Requirements: 2, 3_

  - [ ] 3.3 Implement deduplication
    - Detect duplicate stories by URL and title similarity
    - _Requirements: 2_

  - [ ] 3.4 Write unit tests for scraper
    - Test with mocked HTTP responses
    - Test error handling
    - _Requirements: 8_

- [ ] 4. Implement ranking engine
  - [ ] 4.1 Create RankingEngine class
    - Score stories by recency, HN score, comments
    - Implement breaking news detection
    - Add time-based decay (>48 hours)
    - _Requirements: 3_

  - [ ] 4.2 Write unit tests for ranking
    - Test scoring algorithm
    - Test breaking news detection
    - _Requirements: 8_

---

## MVP 2: AI Integration

- [ ] 5. Implement summary generation with Amazon Bedrock
  - [ ] 5.1 Create SummaryGenerator service
    - Integrate boto3 bedrock-runtime client
    - Implement witty journalist prompt
    - Call the model from BEDROCK_MODEL_ID, falling back to BEDROCK_FALLBACK_MODEL_ID
    - _Requirements: 5_

  - [ ] 5.2 Implement hype detection
    - Detect marketing buzzwords
    - Generate skeptical commentary
    - _Requirements: 5_

  - [ ] 5.3 Implement fallback mechanism
    - Handle Bedrock API failures
    - Use original content excerpts as fallback
    - _Requirements: 5, 6_

  - [ ] 5.4 Write unit tests for summary generation
    - Test with mocked Bedrock responses
    - Test fallback behavior
    - _Requirements: 8_

- [ ] 6. Implement daily briefing generation
  - [ ] 6.1 Create BriefingGenerator service
    - Generate markdown format briefings
    - Include top-ranked stories with summaries
    - Name files as briefing_YYYY-MM-DD.md
    - _Requirements: 7_

  - [ ] 6.2 Add S3 integration
    - Upload briefings to S3 bucket
    - Handle upload failures
    - _Requirements: 7_

  - [ ] 6.3 Write unit tests for briefing generation
    - Test markdown generation
    - Test S3 upload with moto
    - _Requirements: 8_

---

## MVP 3: Web Application

- [ ] 7. Create Flask web application
  - [ ] 7.1 Set up Flask application factory
    - Create app.py with factory pattern
    - Configure logging and error handling
    - _Requirements: 4_

  - [ ] 7.2 Implement API routes
    - GET / - Main feed page
    - GET /api/stories - JSON story list
    - GET /api/briefings - Briefing list
    - _Requirements: 1, 4_

  - [ ] 7.3 Create Jinja2 templates
    - base.html - Layout template
    - feed.html - Story feed
    - story_card.html - Individual story
    - _Requirements: 4_

  - [ ] 7.4 Add responsive CSS
    - Clean, readable design
    - Mobile-first responsive layout
    - _Requirements: 4_

  - [ ] 7.5 Implement pagination
    - Add infinite scroll or pagination
    - Load more stories on demand
    - _Requirements: 4_

  - [ ] 7.6 Write tests for web application
    - Test route responses
    - Test template rendering
    - _Requirements: 8_

---

## MVP 4: Integration and Testing

- [ ] 8. Set up LocalStack testing environment
  - [ ] 8.1 Create docker-compose.localstack.yml
    - Configure LocalStack services (S3, Secrets Manager)
    - Create setup scripts
    - _Requirements: 8_

  - [ ] 8.2 Write integration tests
    - Test end-to-end story collection
    - Test summary generation workflow
    - Test briefing generation
    - _Requirements: 8_

- [ ] 9. Implement property-based tests
  - [ ] 9.1 Story model properties
    - Test Story validation with Hypothesis
    - _Requirements: 8_

  - [ ] 9.2 Ranking properties
    - Test ranking consistency
    - Test time decay behavior
    - _Requirements: 8_

  - [ ] 9.3 Deduplication properties
    - Test duplicate detection accuracy
    - _Requirements: 8_

---

## MVP 5: AWS Infrastructure

> **Lab note**: Task 10.3 targets App Runner because that is where Phase 8 of the lab lands. If you are mid-lab with the Phase 2 Lightsail constraint still in force, expect Kiro to rewrite this task when you run the Phase 8 prompt.

- [ ] 10. Create CloudFormation templates
  - [ ] 10.1 VPC and networking (vpc.yaml)
    - Private subnets for database
    - VPC endpoints for AWS services
    - Security groups
    - _Requirements: 9_

  - [ ] 10.2 Aurora PostgreSQL (database.yaml)
    - Aurora Serverless v2 cluster
    - Secrets Manager integration
    - _Requirements: 6, 9_

  - [ ] 10.3 App Runner service (apprunner.yaml)
    - Container deployment
    - VPC Connector configuration
    - IAM role with required permissions
    - _Requirements: 6, 9_

  - [ ] 10.4 S3 and monitoring (storage.yaml)
    - Briefings bucket
    - CloudWatch alarms
    - _Requirements: 7, 9_

- [ ] 11. Implement deployment automation
  - [ ] 11.1 Create deploy.py script
    - Stack deployment orchestration
    - Parameter management
    - _Requirements: 6_

  - [ ] 11.2 Create Dockerfile
    - Multi-stage build
    - Security hardening
    - _Requirements: 6_

  - [ ] 11.3 Configure CI/CD
    - Build and test pipeline
    - Deploy to staging and production
    - _Requirements: 6_

---

## MVP 6: Documentation and Finalization

- [ ] 12. Create documentation
  - [ ] 12.1 README.md
    - Project overview
    - Setup instructions
    - Usage guide
    - _Requirements: 6_

  - [ ] 12.2 API documentation
    - Document all endpoints
    - Include examples
    - _Requirements: 4_

  - [ ] 12.3 Deployment guide
    - CloudFormation deployment steps
    - Environment configuration
    - _Requirements: 6_

- [ ] 13. Final validation
  - Run complete test suite
  - Verify 70% coverage
  - Security review
  - Performance testing
  - _Requirements: 6, 8, 9_

---

## Task Legend

| Symbol | Status |
|--------|--------|
| `[ ]` | Not started |
| `[~]` | In progress |
| `[x]` | Completed |

## Priority Order

1. **MVP 1** - Foundation (Days 1-2)
2. **MVP 3** - Web Application (Day 3)
3. **MVP 2** - AI Integration (Days 4-5)
4. **MVP 4** - Testing (Day 6)
5. **MVP 5** - Infrastructure (Days 7-8)
6. **MVP 6** - Documentation (Day 9)
