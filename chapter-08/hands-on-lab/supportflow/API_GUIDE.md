# SupportFlow API Guide

Complete guide to using the SupportFlow REST API.

## Base URL

```text
http://localhost:8000
```

## Authentication

All API endpoints (except `/health`) require authentication using an API key.

**Header**: `X-API-Key`
**Default Key**: `demo-key-12345`

### Example Request

```bash
curl -X GET http://localhost:8000/responses/pending \
  -H "X-API-Key: demo-key-12345"
```

## Endpoints

### Health Check

**GET** `/health`

Check service health and database connectivity.

**Authentication**: Not required

**Response** `200 OK`:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "database": "connected"
}
```

---

### Submit Ticket

**POST** `/tickets`

Submit a new customer support ticket. This endpoint:
1. Creates a ticket in the database
2. Analyzes the ticket (category, sentiment, urgency, entities)
3. Evaluates for escalation
4. Generates a draft response requiring human approval
5. Logs all operations to audit trail

**Request Body**:
```json
{
  "content": "I'm very frustrated! I was charged twice for order #12345."
}
```

**Validation**:
- `content`: Required, 10-5000 characters

**Response** `201 Created`:
```json
{
  "ticket": {
    "ticket_id": "TKT-20240115-ABC12345",
    "content": "I'm very frustrated! I was charged twice for order #12345.",
    "created_at": "2024-01-15T10:30:00Z",
    "analysis": {
      "category": "billing",
      "category_confidence": 0.92,
      "urgency": "high",
      "urgency_confidence": 0.88,
      "sentiment": "angry",
      "sentiment_confidence": 0.95,
      "requires_priority_review": true,
      "extracted_entities": [
        {
          "entity_type": "order_id",
          "value": "12345",
          "confidence": 0.95
        }
      ]
    },
    "escalation": {
      "should_escalate": true,
      "priority": "HIGH",
      "reasons": ["angry_sentiment", "multiple_negative_indicators"],
      "details": {}
    },
    "responses": []
  },
  "draft_response": {
    "response_id": "RESP-20240115-XYZ78910",
    "ticket_id": "TKT-20240115-ABC12345",
    "body": "Dear valued customer, we apologize for the billing error...",
    "status": "DRAFT",
    "requires_human_review": true,
    "template_id": "billing_apology",
    "reviewed_by": null,
    "reviewed_at": null,
    "rejection_reason": null,
    "created_at": "2024-01-15T10:30:01Z"
  }
}
```

**Errors**:
- `401 Unauthorized` - Invalid API key
- `422 Unprocessable Entity` - Content validation failed

---

### Get Ticket Details

**GET** `/tickets/{ticket_id}`

Retrieve complete ticket information including analysis and all responses.

**Path Parameters**:
- `ticket_id` (string) - The ticket ID (e.g., `TKT-20240115-ABC12345`)

**Response** `200 OK`:
```json
{
  "ticket_id": "TKT-20240115-ABC12345",
  "content": "I need help with account settings",
  "created_at": "2024-01-15T10:30:00Z",
  "analysis": {
    "category": "account",
    "category_confidence": 0.85,
    "urgency": "medium",
    "urgency_confidence": 0.75,
    "sentiment": "neutral",
    "sentiment_confidence": 0.80,
    "requires_priority_review": false,
    "extracted_entities": []
  },
  "escalation": {
    "should_escalate": false,
    "priority": "LOW",
    "reasons": [],
    "details": {}
  },
  "responses": [
    {
      "response_id": "RESP-20240115-XYZ78910",
      "ticket_id": "TKT-20240115-ABC12345",
      "body": "Thank you for contacting us...",
      "status": "APPROVED",
      "requires_human_review": true,
      "template_id": "account_help",
      "reviewed_by": "reviewer@example.com",
      "reviewed_at": "2024-01-15T10:35:00Z",
      "rejection_reason": null,
      "created_at": "2024-01-15T10:30:01Z"
    }
  ]
}
```

**Errors**:
- `404 Not Found` - Ticket does not exist
- `401 Unauthorized` - Invalid API key

---

### List Pending Responses

**GET** `/responses/pending`

List all responses with `DRAFT` status that are awaiting human review.

**Response** `200 OK`:
```json
{
  "responses": [
    {
      "response_id": "RESP-20240115-XYZ78910",
      "ticket_id": "TKT-20240115-ABC12345",
      "body": "Thank you for contacting us about your billing issue...",
      "status": "DRAFT",
      "requires_human_review": true,
      "template_id": "billing_apology",
      "reviewed_by": null,
      "reviewed_at": null,
      "rejection_reason": null,
      "created_at": "2024-01-15T10:30:01Z"
    }
  ],
  "total": 1
}
```

**Use Case**: Human reviewers check this endpoint to find responses that need approval.

---

### Approve Response

**POST** `/responses/{response_id}/approve`

Approve a draft response for sending to the customer.

**Path Parameters**:
- `response_id` (string) - The response ID (e.g., `RESP-20240115-XYZ78910`)

**Request Body**:
```json
{
  "reviewed_by": "reviewer@example.com"
}
```

**Validation**:
- `reviewed_by`: Required, 1-100 characters
- Response must have status `DRAFT`

**Response** `200 OK`:
```json
{
  "response_id": "RESP-20240115-XYZ78910",
  "ticket_id": "TKT-20240115-ABC12345",
  "body": "Thank you for contacting us...",
  "status": "APPROVED",
  "requires_human_review": true,
  "template_id": "billing_apology",
  "reviewed_by": "reviewer@example.com",
  "reviewed_at": "2024-01-15T10:35:00Z",
  "rejection_reason": null,
  "created_at": "2024-01-15T10:30:01Z"
}
```

**Errors**:
- `404 Not Found` - Response does not exist
- `400 Bad Request` - Response already reviewed
- `401 Unauthorized` - Invalid API key

---

### Reject Response

**POST** `/responses/{response_id}/reject`

Reject a draft response with feedback for improvement.

**Path Parameters**:
- `response_id` (string) - The response ID (e.g., `RESP-20240115-XYZ78910`)

**Request Body**:
```json
{
  "reviewed_by": "reviewer@example.com",
  "reason": "Response tone doesn't match customer's angry sentiment"
}
```

**Validation**:
- `reviewed_by`: Required, 1-100 characters
- `reason`: Required, 10-1000 characters
- Response must have status `DRAFT`

**Response** `200 OK`:
```json
{
  "response_id": "RESP-20240115-XYZ78910",
  "ticket_id": "TKT-20240115-ABC12345",
  "body": "Thank you for contacting us...",
  "status": "REJECTED",
  "requires_human_review": true,
  "template_id": "billing_apology",
  "reviewed_by": "reviewer@example.com",
  "reviewed_at": "2024-01-15T10:35:00Z",
  "rejection_reason": "Response tone doesn't match customer's angry sentiment",
  "created_at": "2024-01-15T10:30:01Z"
}
```

**Errors**:
- `404 Not Found` - Response does not exist
- `400 Bad Request` - Response already reviewed
- `422 Unprocessable Entity` - Validation error
- `401 Unauthorized` - Invalid API key

---

## Common Workflows

### Complete Support Ticket Workflow

```bash
# 1. Customer submits ticket
RESPONSE=$(curl -s -X POST http://localhost:8000/tickets \
  -H "X-API-Key: demo-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"content": "I need help with billing"}')

# Extract IDs
TICKET_ID=$(echo $RESPONSE | jq -r '.ticket.ticket_id')
RESPONSE_ID=$(echo $RESPONSE | jq -r '.draft_response.response_id')

# 2. System analyzes ticket and generates draft response
# (Done automatically in step 1)

# 3. Human reviewer checks pending responses
curl -X GET http://localhost:8000/responses/pending \
  -H "X-API-Key: demo-key-12345"

# 4. Reviewer approves the response
curl -X POST http://localhost:8000/responses/$RESPONSE_ID/approve \
  -H "X-API-Key: demo-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"reviewed_by": "reviewer@example.com"}'

# 5. Verify ticket status
curl -X GET http://localhost:8000/tickets/$TICKET_ID \
  -H "X-API-Key: demo-key-12345"
```

### Handling Escalated Tickets

```bash
# Submit angry customer ticket
RESPONSE=$(curl -s -X POST http://localhost:8000/tickets \
  -H "X-API-Key: demo-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"content": "This is OUTRAGEOUS! I demand a refund immediately!"}')

# Check escalation status
echo $RESPONSE | jq '.ticket.escalation'

# Output will show:
# {
#   "should_escalate": true,
#   "priority": "HIGH",
#   "reasons": ["angry_sentiment", "multiple_negative_indicators"]
# }

# High-priority tickets should be routed to senior support staff
```

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "detail": "Error message describing what went wrong",
  "error_code": "OPTIONAL_ERROR_CODE"
}
```

### Common Errors

**401 Unauthorized**
```json
{
  "detail": "Invalid API key"
}
```

**403 Forbidden**
```json
{
  "detail": "Not authenticated"
}
```

**404 Not Found**
```json
{
  "detail": "Ticket TKT-123 not found"
}
```

**422 Validation Error**
```json
{
  "detail": [
    {
      "loc": ["body", "content"],
      "msg": "ensure this value has at least 10 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

## Rate Limiting

Currently, there are no rate limits enforced. For production deployment, consider implementing rate limiting based on API key.

## Interactive Testing

The API includes Swagger UI for interactive testing:

**Access**: http://localhost:8000/docs

Features:
- Try all endpoints directly in the browser
- View request/response schemas
- See example requests and responses
- No need for separate API client

## Database

### Audit Logs

All operations are logged to the `audit_logs` table with:
- ISO 8601 timestamp
- Action type (e.g., `ticket.created`, `response.approved`)
- User/agent ID
- Resource type and ID
- Additional details (JSON)

### Data Retention

By default, all data is retained indefinitely. For production:
- Configure audit log retention (recommended: 7 years for compliance)
- Set up database backups
- Implement data archival policies

## Security Best Practices

1. **Change Default API Key**: Replace `demo-key-12345` with a secure random key
2. **Use HTTPS**: Enable TLS/SSL in production
3. **Rotate API Keys**: Regularly rotate authentication keys
4. **Monitor Audit Logs**: Review logs for suspicious activity
5. **Validate Input**: All inputs are validated, but additional application-level checks may be needed
6. **Rate Limiting**: Implement rate limiting per API key in production

## Support

For issues or questions:
- Check the interactive documentation at `/docs`
- Review audit logs for debugging
- Check the health endpoint for system status
