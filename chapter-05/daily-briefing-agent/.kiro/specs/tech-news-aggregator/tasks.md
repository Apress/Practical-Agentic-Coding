# Implementation Plan

- [ ] 1. Set up project structure and development environment
  - Create Python project structure with src/, tests/, and infrastructure/ directories
  - Set up requirements.txt with core dependencies (boto3, requests, beautifulsoup4, hypothesis, pytest, moto, responses)
  - Add boto3 with bedrock-runtime support for Claude model integration
  - Configure pytest with pytest.ini for coverage reporting (70% minimum)
  - Set up LocalStack configuration for local AWS service testing
  - Create .gitignore for Python projects
  - _Requirements: 6.1, 6.4_

- [ ] 2. Implement core data models and validation
  - [ ] 2.1 Create Python data models using SQLAlchemy
    - Write Story, Source, SummaryMetadata, and DailyBriefing classes in src/models/
    - Implement validation methods and PostgreSQL serialization/deserialization
    - Add type hints and docstrings for all models
    - _Requirements: 2.2, 5.1_

  - [ ] 2.2 Write property test for data model validation
    - **Property 10: Summary generation completeness**
    - **Validates: Requirements 5.1**

  - [ ] 2.3 Implement PostgreSQL repository layer
    - Create base repository class with CRUD operations in src/repositories/
    - Implement StoryRepository with time-based queries and proper indexing
    - Implement SourceRepository for source management
    - Add error handling and retry logic for PostgreSQL operations
    - _Requirements: 6.4, 2.4_

  - [ ] 2.4 Write unit tests for data models and repositories
    - Create unit tests for data model validation using pytest
    - Write repository tests with mocked PostgreSQL using pytest fixtures
    - Test error conditions and edge cases
    - _Requirements: 2.2, 6.4_

- [ ] 3. Implement Hacker News web scraping functionality
  - [ ] 3.1 Create web scraper using requests and BeautifulSoup4
    - Write HackerNewsScraper class in src/scrapers/ to fetch and parse news.ycombinator.com
    - Implement story extraction with title, URL, score, and comment count
    - Add rate limiting (respect HN's rate limits) and error handling for HTTP requests
    - _Requirements: 2.1, 2.5_

  - [ ] 3.2 Write property test for multi-source collection
    - **Property 3: Multi-source collection**
    - **Validates: Requirements 2.1, 2.3**

  - [ ] 3.3 Implement content filtering and deduplication
    - Create content quality scoring algorithm in src/services/
    - Implement duplicate detection based on title similarity (fuzzy matching) and URL matching
    - Add relevance filtering for technology-focused content
    - _Requirements: 2.2, 2.4_

  - [ ] 3.4 Write property test for content filtering
    - **Property 4: Content filtering**
    - **Validates: Requirements 2.2**

  - [ ] 3.5 Write property test for deduplication
    - **Property 5: Deduplication consistency**
    - **Validates: Requirements 2.4**

  - [ ] 3.6 Write unit tests for web scraping
    - Create unit tests for scraper with mocked HTTP responses using responses library
    - Test filtering and deduplication logic with various input scenarios
    - Test error handling for network failures and malformed HTML
    - _Requirements: 2.1, 2.2, 2.4, 2.5_

- [ ] 4. Implement story ranking and scoring system
  - [ ] 4.1 Create ranking algorithm with multiple factors
    - Implement RankingEngine class in src/services/ with scoring based on recency, HN score, comment count, and content quality
    - Add breaking news detection (high velocity score increases) and priority boosting
    - Create time-based decay for older stories (>48 hours)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [ ] 4.2 Write property test for comprehensive ranking
    - **Property 7: Comprehensive ranking**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

  - [ ] 4.3 Write unit tests for ranking system
    - Create unit tests for scoring algorithm with various story combinations
    - Test breaking news detection and prioritization
    - Test time-based ranking with different story ages
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 5. Implement AI-powered summary generation with Amazon Bedrock
  - [ ] 5.1 Create dedicated SummaryGenerator service class
    - Extract SummaryGenerator from src/lambda_handlers/summarizer.py into src/services/summary_generator.py
    - Replace OpenAI implementation with boto3 bedrock-runtime client for Claude model integration
    - Implement Claude model integration (Claude 3 Sonnet primary, Claude 3 Haiku fallback)
    - Implement witty journalist persona prompts with system and user messages for Claude
    - Implement hype detection (keyword matching) and skeptical commentary generation
    - Add technical jargon translation while preserving accuracy
    - Handle low-content stories with brief assessments or exclusion logic
    - Add token usage tracking and cost optimization
    - Update src/services/__init__.py to export SummaryGenerator
    - _Requirements: 5.1, 5.3, 5.4, 5.5_

  - [ ] 5.2 Update Lambda handler to use new SummaryGenerator service
    - Modify src/lambda_handlers/summarizer.py to import and use the new SummaryGenerator service
    - Remove the embedded SummaryGenerator class from the Lambda handler
    - Update environment variable handling for Bedrock configuration
    - _Requirements: 5.1_

  - [ ] 5.3 Write property test for hype detection
    - **Property 2: Hype detection and skeptical commentary**
    - **Validates: Requirements 1.3, 1.5, 5.4**

  - [ ] 5.4 Write property test for jargon translation
    - **Property 11: Technical jargon translation**
    - **Validates: Requirements 5.3**

  - [ ] 5.5 Write property test for low-content handling
    - **Property 12: Low-content story handling**
    - **Validates: Requirements 5.5**

  - [ ] 5.6 Implement summary generation fallback
    - Create fallback mechanism for when Bedrock API calls fail (rate limits, service errors)
    - Use original article excerpts or metadata as backup descriptions
    - Implement retry logic with exponential backoff for transient failures
    - _Requirements: 6.3_

  - [ ] 5.7 Write property test for summary fallback
    - **Property 13: Summary generation fallback**
    - **Validates: Requirements 6.3**

  - [ ] 5.8 Write unit tests for summary generation
    - Create unit tests for summary generator with mocked Bedrock API responses using moto
    - Test persona consistency and hype detection logic
    - Test fallback mechanisms and error handling for Bedrock failures
    - Test token usage tracking and cost optimization features
    - _Requirements: 5.1, 5.3, 5.4, 5.5, 6.3_

- [ ] 6. Implement daily briefing file generation
  - [ ] 6.1 Create briefing generator and S3 integration
    - Write DailyBriefingGenerator class in src/services/ to create briefing_YYYY-MM-DD.md files
    - Implement markdown formatting with witty summaries and story rankings
    - Add S3 upload functionality using boto3 for briefing file storage
    - _Requirements: 1.1, 1.2, 3.1_

  - [ ] 6.2 Write unit tests for briefing generation
    - Create unit tests for markdown generation and S3 upload with moto
    - Test file naming convention and content formatting
    - Test error handling for S3 operations
    - _Requirements: 1.1, 1.2, 3.1_

- [ ] 7. Implement AWS Lambda functions
  - [ ] 7.1 Create story collector Lambda function
    - Write Lambda handler in src/lambda_handlers/collector.py for scheduled story collection from Hacker News
    - Integrate scraper, filtering, deduplication, and PostgreSQL storage
    - Add CloudWatch logging and error handling
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [ ] 7.2 Create summary generator Lambda function
    - Write Lambda handler in src/lambda_handlers/summarizer.py triggered by SQS for story processing
    - Integrate Bedrock AI summary generation and PostgreSQL updates
    - Add retry logic and dead letter queue handling for Bedrock API failures
    - _Requirements: 5.1, 5.3, 5.4, 5.5_

  - [ ] 7.3 Create daily briefing Lambda function
    - Write Lambda handler in src/lambda_handlers/briefing.py for daily briefing generation and S3 upload
    - Integrate ranking system and markdown generation
    - Schedule daily execution via EventBridge
    - _Requirements: 1.1, 1.2, 3.1_

  - [ ] 7.4 Create API Lambda functions
    - Write Lambda handlers in src/lambda_handlers/api.py for story retrieval and feed generation
    - Implement API Gateway integration with proper error responses
    - Add request validation and JSON response formatting
    - _Requirements: 1.1, 4.3, 4.4_

  - [ ] 7.5 Write property test for source failure resilience
    - **Property 6: Source failure resilience**
    - **Validates: Requirements 2.5, 6.1**

  - [ ] 7.6 Write property test for database error recovery
    - **Property 14: Database error recovery**
    - **Validates: Requirements 6.4**

  - [ ] 7.7 Write unit tests for Lambda functions
    - Create unit tests for all Lambda handlers with mocked AWS services
    - Test event processing, error handling, and response formatting
    - Test integration between Lambda functions and AWS services
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 5.1, 5.3, 5.4, 5.5, 1.1, 1.2, 3.1, 4.3, 4.4_

- [ ] 8. Create Python web application with Flask
  - [ ] 8.1 Set up Flask web application structure
    - Create Flask application in src/web/ with proper project structure
    - Set up Jinja2 templates directory with base template
    - Configure static file serving for CSS and JavaScript
    - Implement template inheritance and macros
    - _Requirements: 4.1, 4.2, 4.5_

  - [ ] 8.2 Design and implement responsive UI
    - Create CSS styles with responsive design for mobile, tablet, and desktop
    - Define visual design system (colors, typography, spacing) reflecting witty journalist persona
    - Implement story card component with clean, readable layout
    - Create loading states, error states, and empty states
    - _Requirements: 4.1, 4.2, 4.5_

  - [ ] 8.3 Implement story feed and interaction pages
    - Create main feed route with server-side rendered story list
    - Implement story card templates with links to original URLs
    - Add pagination or infinite scroll with AJAX loading
    - Create error pages (404, 500) with appropriate messaging
    - _Requirements: 1.1, 1.4, 4.3, 4.4_

  - [ ] 8.4 Write property test for story link accessibility
    - **Property 1: Story link accessibility**
    - **Validates: Requirements 1.4**

  - [ ] 8.5 Write property test for infinite scroll
    - **Property 8: Infinite scroll loading**
    - **Validates: Requirements 4.3**

  - [ ] 8.6 Write property test for UI interaction feedback
    - **Property 9: UI interaction feedback**
    - **Validates: Requirements 4.4**

  - [ ] 8.7 Write unit tests for web application
    - Create unit tests for Flask routes and templates using pytest
    - Test HTML rendering, pagination, and error responses
    - Test responsive behavior and accessibility features
    - _Requirements: 1.1, 1.4, 4.1, 4.2, 4.3, 4.4, 4.5_

  - [ ] 8.8 Test development server functionality
    - Validate that run_dev_server.py starts successfully on port 5000
    - Test mock data loading and story repository setup
    - Verify Flask app creation with development configuration
    - Test server accessibility on localhost and network interfaces
    - Validate graceful shutdown and error handling
    - _Requirements: 4.1, 4.2, 6.1_

- [ ] 9. Environment configuration and hybrid local integration testing with LocalStack














  - [ ] 9.1 Create environment configuration system



    - Create .env.example file with all required environment variables documented
    - Create environment-specific configuration files (.env.local, .env.dev, .env.prod)
    - Add python-dotenv integration to load environment variables in development
    - Document environment variables for LocalStack vs AWS cloud deployment
    - Create configuration validation to ensure required variables are set
    - _Requirements: 6.1, 7.1_

  - [ ] 9.2 Configure LocalStack hybrid testing environment



    - Start LocalStack with docker-compose.localstack.yml for DynamoDB, S3, SQS, and API Gateway
    - Run localstack-setup.sh to create tables, buckets, and queues
    - Configure environment variables for hybrid testing (LocalStack for AWS services, mocked Bedrock)
    - Create integration test configuration that combines LocalStack and moto mocking
    - _Requirements: 7.1, 7.2_

  - [ ] 9.3 Implement hybrid integration test suite
    - **COMPLETED**: Created comprehensive hybrid integration test suite with 42 integration tests
    - **COMPLETED**: Main test suite (`test_hybrid_integration_suite.py`) covers complete workflows:
      - Story collection workflow with LocalStack DynamoDB operations
      - Summary generation with mocked Bedrock and LocalStack storage
      - Daily briefing generation with real S3 operations
      - Web application integration with LocalStack backend
      - Lambda function integration with hybrid setup
      - Data consistency and performance testing with large datasets
    - **COMPLETED**: Extended test suite (`test_hybrid_integration_suite_extended.py`) covers error scenarios:
      - Database connection failures and network errors
      - S3 operation failures and timeout conditions
      - Malformed data handling and Unicode support
      - Concurrent operations and edge cases
      - Cross-service data integrity validation
    - **COMPLETED**: API coverage suite (`test_hybrid_integration_api_coverage.py`) covers endpoints:
      - Comprehensive API pagination and search functionality
      - Breaking news and individual story retrieval
      - Manual briefing generation and listing
      - Web application security and error handling
      - System health checks and performance monitoring
    - **COMPLETED**: Achieved 78% combined test coverage with 123 total tests
    - **COMPLETED**: Created comprehensive test coverage report and documentation
    - _Requirements: 7.2, 7.3_

  - [ ] 9.4 Validate Lambda functions with hybrid LocalStack setup
    - **COMPLETED**: Comprehensive Lambda function testing with hybrid LocalStack setup
    - **COMPLETED**: Created `test_lambda_hybrid_localstack.py` with 17 test methods covering all core Lambda functionality
    - **COMPLETED**: Created `test_lambda_hybrid_localstack_extended.py` with 15 additional test methods for edge cases
    - **COMPLETED**: Achieved 100% Lambda handler coverage (11/11 handlers tested):
      - Collector Lambda: lambda_handler, health_check_handler
      - Summarizer Lambda: lambda_handler, dead_letter_handler  
      - Briefing Lambda: lambda_handler, manual_briefing_handler, list_briefings_handler, health_check_handler
      - API Lambda: lambda_handler, get_feed_handler, search_stories_handler, options_handler
    - **COMPLETED**: Comprehensive test scenarios: basic functionality, error handling, environment configuration, integration workflows, performance testing, boundary conditions, security validation
    - **COMPLETED**: LocalStack integration for DynamoDB, S3, SQS with mocked Bedrock for unavailable services
    - **COMPLETED**: Cross-service integration testing with complete story processing workflows
    - **COMPLETED**: Performance testing with large datasets and concurrent operations
    - **COMPLETED**: Error scenario testing including network failures, database errors, S3 permission issues
    - **COMPLETED**: CORS and security testing for API endpoints
    - **COMPLETED**: Created comprehensive testing documentation and execution guide
    - _Requirements: 7.4_

  - [ ] 9.5 Performance and reliability testing with LocalStack
    - **COMPLETED**: Performance testing integrated into hybrid test suite
    - **COMPLETED**: System performance tested with large datasets (100+ stories) using LocalStack persistence
    - **COMPLETED**: Data consistency validated across multiple operations and concurrent access
    - **COMPLETED**: Concurrent operations tested against LocalStack services with thread safety validation
    - **COMPLETED**: Batch operation performance benchmarked and optimized
    - **COMPLETED**: Query performance tested with different indexes and data sizes
    - **COMPLETED**: Performance metrics collection and monitoring implemented
    - _Requirements: 7.5_

  - [ ] 9.6 Create hybrid testing documentation and scripts
    - **COMPLETED**: Comprehensive hybrid testing documentation created
    - **COMPLETED**: LocalStack setup and hybrid testing approach documented in `docs/LOCALSTACK_TESTING.md`
    - **COMPLETED**: Test runner scripts created for different testing modes (unit, hybrid, full integration)
    - **COMPLETED**: Pytest markers properly configured for LocalStack-dependent tests
    - **COMPLETED**: Test coverage report and analysis documentation created
    - **COMPLETED**: CI/CD configuration guidance provided for hybrid testing pipeline
    - _Requirements: 7.1_

  - [ ] 9.7 Set up browser testing with Playwright
    - **COMPLETED**: Installed and configured Playwright for automated browser testing
    - **COMPLETED**: Set up Playwright WebDriver with Chromium browser for browser automation
    - **COMPLETED**: Created comprehensive browser test fixtures and page object models for web application
    - **COMPLETED**: Configured headless Chrome for CI/CD pipeline testing with environment variable controls
    - **COMPLETED**: Added browser testing dependencies (playwright>=1.40.0, pytest-playwright>=0.4.3) to requirements.txt
    - **COMPLETED**: Created browser testing infrastructure with device-specific contexts (mobile, tablet, desktop)
    - **COMPLETED**: Implemented page object models (FeedPage, ErrorPage) with comprehensive interaction methods
    - **COMPLETED**: Created browser test runner script with multiple execution options
    - **COMPLETED**: Added comprehensive browser testing documentation and setup guides
    - **COMPLETED**: Validated setup with 7 passing browser infrastructure tests
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [ ] 9.8 Implement browser-based UI tests using Playwright infrastructure
    - **COMPLETED**: Created comprehensive browser-based UI test suite using Playwright infrastructure
    - **COMPLETED**: End-to-end tests for story feed loading and pagination using FeedPage page object model
    - **COMPLETED**: Responsive design testing across different viewport sizes (mobile 375x667, tablet 768x1024, desktop 1280x720)
    - **COMPLETED**: Infinite scroll functionality testing with real browser interactions using Playwright
    - **COMPLETED**: Story link accessibility and navigation testing with automated accessibility validation
    - **COMPLETED**: UI interaction feedback and loading states testing using browser automation
    - **COMPLETED**: Accessibility features validation using Playwright's built-in accessibility testing capabilities
    - **COMPLETED**: Comprehensive UI test suite covering all user interaction flows with 15+ browser tests
    - **COMPLETED**: Created browser test coverage reports and documentation
    - _Requirements: 1.4, 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 10. Create comprehensive CloudFormation infrastructure templates





  - [ ] 10.1 Create main infrastructure CloudFormation template


    - Write comprehensive template in infrastructure/cloudformation/main-infrastructure.yaml for DynamoDB tables (Stories, Sources, DailySummaries) with GSI indexes
    - Create S3 buckets for briefing file storage with proper permissions
    - Define Lambda functions with proper IAM roles, environment variables, and layers
    - Add Bedrock IAM permissions for Claude model access (bedrock:InvokeModel)
    - Set up API Gateway with Lambda proxy integration, CORS, and throttling
    - Create SQS queue for story processing with dead letter queue
    - _Requirements: 6.1, 6.4_

  - [ ] 10.2 Create Lambda deployment package template


    - Create CloudFormation template for Lambda deployment packages
    - Include proper dependency management and layer configuration
    - Add environment-specific configuration parameters
    - _Requirements: 6.1, 6.4_

  - [ ] 10.3 Implement deployment automation


    - Create deployment script (deploy.py) for CloudFormation stack management
    - Set up environment-specific parameter files (dev.json, prod.json)
    - Add stack validation and rollback procedures
    - Create Lambda deployment packages with dependencies
    - _Requirements: 6.1, 6.4_



  - [ ] 10.4 Write infrastructure tests
    - Create tests for CloudFormation template validation using cfn-lint
    - Test deployment and rollback procedures
    - Validate IAM permissions and security configurations
    - _Requirements: 6.1, 6.4_

- [ ] 11. Implement local development and testing infrastructure
  - [ ] 11.1 Create development server for local testing
    - **COMPLETED**: Created `run_dev_server.py` for local Flask development
    - **COMPLETED**: Mock data generation with realistic tech news stories
    - **COMPLETED**: Dependency injection system for testing different components
    - **COMPLETED**: Hot reloading and debug capabilities for rapid development
    - **COMPLETED**: Environment configuration for development vs production
    - _Requirements: 4.1, 6.1_

  - [ ] 11.2 Set up LocalStack for AWS service simulation
    - **COMPLETED**: LocalStack configuration for DynamoDB, S3, SQS, and EventBridge
    - **COMPLETED**: Setup scripts for creating tables, buckets, and queues
    - **COMPLETED**: Environment configuration for hybrid testing (LocalStack + mocked Bedrock)
    - **COMPLETED**: Integration test configuration combining LocalStack and moto mocking
    - **COMPLETED**: Docker Compose setup for LocalStack services
    - _Requirements: 7.1, 7.2_

  - [ ] 11.3 Implement comprehensive testing infrastructure
    - **COMPLETED**: Unit tests with pytest and moto for AWS service mocking
    - **COMPLETED**: Property-based tests with Hypothesis for correctness validation
    - **COMPLETED**: Hybrid integration tests with LocalStack for realistic AWS behavior
    - **COMPLETED**: Browser testing with Playwright for UI validation
    - **COMPLETED**: Comprehensive test coverage across all components and workflows
    - **COMPLETED**: Test runner scripts for different testing modes
    - **COMPLETED**: Performance and reliability testing with large datasets
    - _Requirements: 7.2, 7.3, 7.4, 7.5_

  - [ ] 11.4 Write property tests for enhanced data models and analytics
    - [ ] 11.4.1 Write property test for multi-category story support
      - **Property 21: Multi-category story support**
      - **Validates: Requirements 9.1**

    - [ ] 11.4.2 Write property test for analytics tracking
      - **Property 22: Analytics tracking completeness**
      - **Validates: Requirements 9.3**

    - [ ] 11.4.3 Write property test for CloudWatch metrics integration
      - **Property 23: CloudWatch metrics integration**
      - **Validates: Requirements 9.4**

  - [ ] 11.5 Write property tests for security and credential management
    - [ ] 11.5.1 Write property test for Secrets Manager integration
      - **Property 24: Secrets Manager credential retrieval**
      - **Validates: Requirements 10.2**

    - [ ] 11.5.2 Write property test for VPC endpoint connectivity
      - **Property 25: VPC endpoint connectivity**
      - **Validates: Requirements 10.3**

    - [ ] 11.5.3 Write property test for IAM least privilege enforcement
      - **Property 26: IAM least privilege enforcement**
      - **Validates: Requirements 10.4, 10.5**

    - [ ] 11.5.4 Write property test for Bedrock Global Inference integration
      - **Property 27: Bedrock Global Inference integration**
      - **Validates: Requirements 10.1**

- [ ] 12. AWS App Runner Deployment with VPC and Enhanced Security
  - [ ] 12.1 Deploy VPC infrastructure and Aurora PostgreSQL cluster (Foundation Layer)
    - Create CloudFormation template for VPC with private subnets across multiple AZs
    - Deploy Aurora PostgreSQL cluster in private subnets with Multi-AZ configuration
    - Create VPC endpoints for S3, Secrets Manager, Bedrock, and CloudWatch
    - Configure security groups for App Runner to Aurora connectivity
    - Set up Aurora Serverless v2 with auto-scaling configuration
    - Create S3 bucket for briefing file storage with proper permissions
    - Configure IAM roles and policies for VPC endpoint access
    - Validate Aurora connectivity and basic operations through VPC
    - _Requirements: 6.6, 6.7, 6.8, 10.3, 10.5_

  - [ ] 12.2 Configure AWS Secrets Manager and database credentials
    - Create Secrets Manager secret for Aurora PostgreSQL credentials
    - Configure automatic credential rotation with 30-day cycle
    - Create dedicated application database user with minimal CRUD permissions
    - Set up IAM policies for Secrets Manager access from App Runner
    - Implement credential retrieval logic in application code
    - Test credential rotation and application reconnection
    - Validate least privilege database access permissions
    - _Requirements: 6.7, 6.8, 10.2, 10.4, 10.5_

  - [ ] 12.3 Deploy containerized Flask application to AWS App Runner (Application Layer)
    - Create CloudFormation template for App Runner service with VPC Connector
    - Configure App Runner to connect to VPC private subnets
    - Set up ECR repository for Docker image storage with vulnerability scanning
    - Build and push Docker container with Flask application
    - Configure environment variables for VPC endpoint connectivity
    - Set up App Runner IAM role with Bedrock, Secrets Manager, S3, and CloudWatch permissions
    - Configure auto-scaling settings and health checks
    - Test App Runner to Aurora connectivity through VPC Connector
    - _Requirements: 1.1, 4.1, 4.2, 6.6, 10.1, 10.3, 10.4_

  - [ ] 12.4 Implement enhanced data models with categories and analytics tracking
    - Update SQLAlchemy models to include Category, StoryAccessLog, and enhanced Story models
    - Create Alembic migration for new table structure with proper indexes
    - Implement many-to-many relationship between stories and categories
    - Add analytics tracking fields (view_count, engagement_score, access_logs)
    - Update repository layer to support category management and analytics
    - Implement CloudWatch custom metrics integration
    - Test data model relationships and analytics tracking functionality
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

  - [ ] 12.5 Configure Amazon Bedrock with Claude Haiku 4.5 Global Inference profiles
    - Update Bedrock integration to use Claude Haiku 4.5 Global Inference profiles
    - Configure correct model ARNs for primary and fallback models
    - Set up VPC endpoint connectivity for Bedrock API access
    - Implement cost tracking and token usage monitoring
    - Update IAM policies for Bedrock Global Inference access
    - Test summary generation with Global Inference profiles
    - Validate cost optimization and performance improvements
    - _Requirements: 5.1, 5.3, 5.4, 5.5, 10.1, 10.3_

  - [ ] 12.6 Implement CloudWatch analytics and monitoring
    - Create CloudWatch custom metrics for story views, engagement, and category performance
    - Set up CloudWatch dashboards for system health and user analytics
    - Configure CloudWatch alarms for database errors, high costs, and performance issues
    - Implement structured logging across all application components
    - Set up SNS notifications for critical alerts
    - Create operational runbooks for common failure scenarios
    - Test monitoring and alerting functionality
    - _Requirements: 6.1, 6.4, 9.4_

  - [ ] 12.7 Configure Amazon QuickSight integration for business intelligence
    - Create QuickSight data source connection to Aurora PostgreSQL
    - Set up QuickSight datasets for stories, categories, and analytics tables
    - Create comprehensive analytics dashboards for story performance and user engagement
    - Configure automated report generation and distribution
    - Set up proper IAM permissions for QuickSight Aurora access
    - Test dashboard functionality and data refresh
    - _Requirements: 9.5_

  - [ ] 12.8 End-to-end system validation and security testing
    - Test complete story collection, AI processing, and display workflow through VPC
    - Verify Flask web application performance on App Runner with real Aurora data
    - Test system resilience with simulated Aurora failures and VPC connectivity issues
    - Validate cross-browser compatibility and mobile responsiveness in production
    - Perform security testing of VPC endpoints and IAM role permissions
    - Test Secrets Manager credential rotation and application reconnection
    - Validate data consistency across Aurora cluster operations under load
    - Test CloudWatch monitoring and alerting with real failure scenarios
    - Verify App Runner auto-scaling behavior under load
    - _Requirements: 1.1, 4.1, 4.2, 6.1, 6.6, 6.7, 6.8, 10.2, 10.3, 10.4, 10.5_

- [ ] 13. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.