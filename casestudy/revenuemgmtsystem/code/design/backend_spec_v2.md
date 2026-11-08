# ZenithStays Backend Design Specification (v2.0)

> **Note (as of November 7, 2026):** This specification dates from December 2025. The published backend (`code/backend/`) implements only part of it: it serves mock data under unversioned `/api/...` routes rather than the `/v1/...` routes specified below, and it has no authentication, rate limiting, or DynamoDB access yet.

## 1. Executive Summary
This specification sets out the architecture, data models, and API contracts for the ZenithStays application. It is designed to be **Cloud-Native**, **Event-Driven**, and **AI-First**, ensuring scalability to manage thousands of properties and process millions of data points for real-time revenue management.

---

## 2. High-Level Architecture

### 2.1 Core Principles
*   **Microservices Ready**: Although starting as a modular monolith, the codebase is structured (Services/Controllers) to be split into Lambda functions or Containers.
*   **Event-Driven**: Asynchronous processing for heavy workloads (e.g., PMS sync, Market Data ingestion) via **AWS EventBridge** and **SQS**.
*   **API First**: Strict OpenAPI (Swagger) specifications for all endpoints.
*   **Security First**: Zero-trust architecture with **Cognito** (JWT) for AuthN/AuthZ.

### 2.2 System Diagram (Conceptual)
```text
[Client App] <--> [API Gateway] <--> [Backend API (Express/Lambda)]
                                          |
                                          +--> [DynamoDB (Single Table Design)]
                                          +--> [AWS Bedrock (AI Agents)]
                                          +--> [EventBridge] --> [Data Ingestion Workers]
```

### 2.3 Compute Strategy: Addressing Cold Starts
**Concern**: AWS Lambda "Cold Starts" (latency on first request) can impact user experience, especially for a Booking Engine.

**Analysis**:
*   *Node.js Cold Starts*: Typically fast (< 500ms).
*   *VPC Latency*: Modern AWS networking has negligible penalty.

**Recommendation: Hybrid Approach**
1.  **Core API (Booking/Search)**: deploy on **AWS Fargate (Containers)**.
    *   *Pros*: Consistent latency, no cold starts, supports WebSockets for real-time rates.
    *   *Cons*: Higher baseline cost (always running).
2.  **Async/Background (Data Sync, AI, Reporting)**: deploy on **AWS Lambda**.
    *   *Pros*: Scales out automatically (within account concurrency quotas), pay-per-ms, perfect for "bursty" workloads (e.g., syncing inventory every hour).
    *   *Mitigation*: Use **AWS Lambda Provisioned Concurrency** or **SnapStart** (Java, Python, and .NET runtimes only, not Node.js) if latency becomes an issue for specific functions.

---

## 3. Data Models (DynamoDB Schema)

We use a **Single Table Design** for performance and scalability.

**Partition Key (PK)**: `ENTITY#{ID}`
**Sort Key (SK)**: `METADATA` or `SUB_ENTITY#{ID}`

### 3.1 Properties
*   **PK**: `PROP#{UUID}`
*   **SK**: `METADATA`
*   **Attributes**:
    *   `name`: string
    *   `type`: enum (Hotel, Resort, VacationRental)
    *   `status`: enum (Active, Maintenance)
    *   `location`: { lat, lng, address_obj, timezone }
    *   `integrations`: { pms_id, channel_manager_id }

### 3.2 Inventory & Rooms
*   **PK**: `PROP#{UUID}`
*   **SK**: `ROOM#{ROOM_TYPE_ID}`
*   **Attributes**:
    *   `code`: string (e.g., "KNG")
    *   `inventory_count`: number
    *   `base_rate`: decimal

### 3.3 Reservations
*   **PK**: `RES#{YYYY-MM}#{PROP_ID}` (Sharded by Month/Property for reporting)
*   **SK**: `RES#{UUID}`
*   **Attributes**:
    *   `guest`: { id, name, segment }
    *   `stay`: { check_in, check_out, nights }
    *   `financials`: { total, currency, status }

### 3.4 Market Intelligence (Events)
Source: PredictHQ / Google Events
*   **PK**: `EVENT#{GEO_HASH}` (Clustered by location)
*   **SK**: `DATE#{ISO_TIMESTAMP}`
*   **Attributes**:
    *   `id`: string
    *   `rank`: number (0-100 impact score)
    *   `category`: string
    *   `predicted_attendance`: number

---

## 4. API Specification & Standards

### 4.1 Global Standards
*   **Versioning**: `/api/v1/...`
*   **Authentication**: Bearer Token (JWT from AWS Cognito/Auth0).
*   **Rate Limiting**: Redis-backed leaky bucket per tenant.
*   **Response Format**: A JSON envelope.
    ```json
    {
      "data": { ... },
      "meta": { "page": 1, "limit": 20, "traceId": "abc-123" },
      "error": null
    }
    ```

### 4.2 Endpoints

#### Properties Domain
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/v1/properties` | `read:properties` | List properties with pagination/filtering |
| `PATCH` | `/v1/properties/:id` | `write:properties` | Update non-critical property details |
| `POST` | `/v1/properties/:id/sync` | `admin` | **Async**. Trigger PMS synchronization |

#### Administration & Configuration
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/users` | `admin` | List all team members |
| `POST` | `/api/users/invite` | `admin` | Invite new user (Email trigger) |
| `GET` | `/api/settings/idp` | `admin` | Get current SSO/IDP configuration |
| `PUT` | `/api/settings/idp` | `admin` | Update IDP settings (Keys, Endpoints, RBAC Roles) |
| `GET` | `/api/integrations` | `admin` | List PMS/OTA Integrations status |
| `POST` | `/api/integrations/:id/connect` | `admin` | Securely exchange API keys for integration |


#### Revenue Strategy Domain
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/v1/strategy/:propertyId/calendar` | `read:strategy` | Get demand calendar with events |
| `POST` | `/v1/strategy/:propertyId/optimize` | `write:strategy` | **Async**. Trigger AI price optimization |

#### Dashboard & Insights
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/v1/dashboard/insight` | `read:insights` | Get AI recommendations (Passive Nudge) |
| `POST` | `/v1/dashboard/insight/approve` | `write:insights` | Execute recommended action |
| `POST` | `/v1/chat` | `read:chat` | **New**. Interactive Chat Assistant Query |

---

## 5. Security & Compliance
*   **Data Encryption**: AES-256 for data at rest (DynamoDB), TLS 1.3 for transit.
*   **PII Handling**: Guest PII (Names, Emails) stored in separate isolated records with higher access controls.
*   **Audit Logging**: All write operations stream to AWS CloudWatch Logs for audit trails.

## 6. AI Agent Integration (Bedrock)
*   **Strategy Agent**:
    *   *Input*: Historical Booking Curves, Competitor Rates, Market Events.
    *   *Output*: Price Recommendations, Stay Restrictions (MinLOS).
*   **Execution Agent**:
    *   *Role*: Autonomous execution of approved strategies via PMS Write-backs.

## 7. Roadmap to Production
1.  **Phase 1 (MVP)**: Express Monolith, Mock Interface, Basic JWT.
2.  **Phase 2 (Data)**: Integrate DynamoDB, PredictHQ fetchers, Real PMS (via HAPI/SiteMinder).
3.  **Phase 3 (AI)**: Deploy Bedrock Agents, Automated Price Updates.
4.  **Phase 4 (Scale)**: Migrate to Serverless (Lambda), Multi-region replication.
