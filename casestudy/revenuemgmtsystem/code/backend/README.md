# ZenithStays - Backend API

This is the Node.js/Express backend for the ZenithStays case study. In the design, it sits between the frontend dashboard and the downstream services (DynamoDB, the Bedrock agents, PMS integrations).

As published, every endpoint answers from in-memory mock data. The one exception is the dashboard insight. It asks a Bedrock agent first, if one is configured. Otherwise it falls back to mock data.

## Technology Stack
- **Runtime**: Node.js 22.12 or later. The `uuid` dependency is an ES module. The backend loads it with `require()`, and older Node.js versions reject that.
- **Framework**: Express 5
- **Data**: In-memory mock data (`src/services/mockDataService.js` and the controllers). DynamoDB is the planned store. Nothing here writes to it.
- **AI**: Amazon Bedrock Agents through `@aws-sdk/client-bedrock-agent-runtime` (`src/services/aiAgentService.js`), used only when `STRATEGY_AGENT_ID` is set.

## Running Locally

You need Node.js 22.12 or later (`node --version`). No cloud account is needed.

```bash
cd casestudy/revenuemgmtsystem/code/backend
npm ci
cp .env.example .env
node server.js
```

Copying `.env.example` is optional. Every variable has a default. In Windows Command Prompt, use `copy .env.example .env`. PowerShell accepts `cp` as written.

Check the output:

- The server prints `Server running on port 3001` and the list of route prefixes.
- The two `[dotenv@17...]` lines above it come from the `dotenv` package. They say it loaded `.env`.
- Each request is logged with its `x-trace-id` header, or `no-trace-id` when the caller sends none.

Stop the server with Ctrl+C.

## Verify

In a second terminal:

```bash
curl http://localhost:3001/health
curl http://localhost:3001/api/dashboard/stats
curl http://localhost:3001/api/dashboard/insight
curl -X POST http://localhost:3001/api/chat -H "Content-Type: application/json" -d '{"message":"What about rates?"}'
```

Check the results:

- `/health` returns `{"status":"ok","service":"ZenithStays API","mode":"modular"}`.
- The insight call returns a mock recommendation. The server log shows `Bedrock Agent ID not configured. Falling back to Mock data.`
- The chat call returns a canned reply. Keywords in `message` pick the reply: rate, price, occupancy, approve, hello.

On Windows, run the GET requests with `curl.exe`. In Windows PowerShell 5.1, plain `curl` is an alias for `Invoke-WebRequest`. For the POST, use:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:3001/api/chat -ContentType 'application/json' -Body '{"message":"What about rates?"}'
```

## API Structure

### Base URL: `http://localhost:3001`

Every route answers from in-memory data. The data resets when the server restarts. The dashboard routes take a `propertyId` query parameter (sample IDs `1` to `4`). An ID with no mock data of its own gets the Miami property's numbers (ID `1`).

| Method | Path | What it does |
| :--- | :--- | :--- |
| `GET` | `/health` | Service status |
| `GET` | `/api/properties` | The four sample properties |
| `GET` | `/api/properties/:id` | One property, or 404 |
| `GET` | `/api/dashboard/stats?propertyId=` | KPI tiles: RevPAR, occupancy, ADR, demand score |
| `GET` | `/api/dashboard/chart?propertyId=` | Seven days of revenue against forecast |
| `GET` | `/api/dashboard/insight?propertyId=` | Strategy agent insight, or a mock one |
| `POST` | `/api/dashboard/insight/approve` | Stub: returns success without calling the Execution agent |
| `GET`, `POST` | `/api/settings/general` | Property and regional settings |
| `POST` | `/api/chat` | Canned assistant replies |
| `GET` | `/api/integrations` | PMS, channel manager, OTA, and payment connections |
| `POST` | `/api/integrations/:id/connect`, `/disconnect`, `/sync` | Simulated connection changes |
| `GET` | `/api/users` | Team members |
| `POST` | `/api/users/invite` | Adds a user with status `Pending`; no email is sent |
| `GET`, `PUT` | `/api/users/idp` | Stored SSO identity provider settings; nothing authenticates against them |

## Multi-Cloud Architecture

The backend sketches the **Adapter Pattern**, so it can deploy on both **AWS** and **GCP**.

- **Core Logic**: Meant to call only generic interfaces (e.g., `StorageInterface`).
- **Adapters**: `AwsStorageProvider` and `GcpStorageProvider` are stubs. They log the call and return a URL. The `@aws-sdk/client-s3` and `@google-cloud/storage` calls are commented out. Neither package is a dependency.
- **Factory**: `CloudFactory.js` selects the implementation at runtime based on the `CLOUD_PROVIDER` env var. Nothing in the server calls it yet.

**Usage** (from this directory):
```bash
node -e "require('./src/services/cloud/CloudFactory').getStorageProvider().uploadFile('my-bucket','file.txt','content').then(console.log)"
```

This prints the factory and provider log lines, then `https://my-bucket.s3.amazonaws.com/file.txt`.

This one-liner does not read `.env`. Set the provider in the shell:

- bash: put `CLOUD_PROVIDER=GCP ` in front of the command.
- PowerShell: run `$env:CLOUD_PROVIDER = "GCP"` first.

The URL then becomes `https://storage.googleapis.com/my-bucket/file.txt`.

## Environment Variables

`.env.example` lists every variable the server reads. All are optional.

| Variable | Default | Used by |
| :--- | :--- | :--- |
| `PORT` | `3001` | `server.js` |
| `AWS_REGION` | `us-east-1` | Bedrock agent runtime client and the AWS storage stub |
| `STRATEGY_AGENT_ID` | unset (mock insight) | `src/services/aiAgentService.js` |
| `STRATEGY_AGENT_ALIAS_ID` | `TSTALIASID`, the test alias for the agent's DRAFT version | `src/services/aiAgentService.js` |
| `CLOUD_PROVIDER` | `AWS` | `src/services/cloud/CloudFactory.js` |

To call a real agent, you also need:

- AWS credentials that the AWS SDK can find (environment variables or a configured profile)
- an agent that already exists

Since July 30, 2026, Amazon Bedrock Agents (now Bedrock Agents Classic) has been closed to new customers. AWS accounts with no Bedrock Agents activity in the previous 12 months cannot create agents. AWS points new work to Amazon Bedrock AgentCore. See [Amazon Bedrock Agents Classic maintenance mode](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-classic-maintenance-mode.html).

The handlers in `src/lambdas/` read `INSIGHTS_TABLE_NAME` and `RATES_TABLE_NAME`. Those belong to the deployed Lambda functions. This server does not use them.

## Common Failures

- **`ERR_REQUIRE_ESM` naming `uuid`**: Node.js is older than 22.12. Upgrade Node.js.
- **The server exits with `Could not start the server on port 3001: listen EADDRINUSE`**: port 3001 is already in use. Stop the other process, or set a different `PORT` in `.env`.
- **`POST /api/chat` returns 500 with `Cannot destructure property 'message' of 'req.body'`**: the request had no JSON body. Send `Content-Type: application/json` and a `message` field, as in the examples above.
- **The insight log shows `Error invoking Strategy Agent` and `falling back to mock`**: `STRATEGY_AGENT_ID` is set, but one of these is wrong: the credentials, Region, agent, or alias. With no credentials at all, the error is `CredentialsProviderError: Could not load credentials from any providers`. The endpoint still answers with the mock insight.
