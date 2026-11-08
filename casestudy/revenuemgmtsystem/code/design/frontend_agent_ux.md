# Frontend UX: Agent Integration Guide

> **Visual Reference**: [View Interactive HTML Mocks](./mocks/agent_ux_mocks.html)

> **Note:** The React files this guide names (`Dashboard.jsx`, `RevenueAssistantChat.jsx`, and others) are not published in this repository. The status markers below describe the original build. You cannot open that code here. Of the backend endpoints it mentions, `GET /api/dashboard/insight` and `POST /api/chat` exist in `code/backend/`. `POST /api/actions/confirm` does not.

## 1. Overview
This document defines how the **Backend AI Agents** (Supervisor, Strategy, Market) are exposed to the **Frontend (React)** user experience.
We aim for "Invisible AI" for general tasks and "Interactive AI" for deep analysis.

## 2. Integration Points

### 2.1 Passive Insights (The "Nudge")
Automatically presented on the Dashboard without user query.
*   **Current Status**: Implemented in `Dashboard.jsx`.
*   **UI Component**: `Dashboard.jsx` (Red "Strategy Agent Insight" Panel).
*   **Backend Flow**:
    1.  Frontend calls `GET /api/dashboard/insight`.
    2.  Backend invokes **Strategy Agent**: *"Analyze current alerts for user's property."*
    3.  Agent uses **Code Interpreter** to check occupancy vs. forecast.
    4.  Agent Output: *"Occupancy for next weekend is 10% below compset. Recommend promotional email."*
*   **User Action**: "Approve" (Buttons: [Launch Promo] [Dismiss]).

### 2.2 Active Assistant (The "Chat")
A side-panel or floating chat interface for "Ad-hoc Revenue Analysis".
*   **UI Component**: `RevenueAssistantChat.jsx` (Global Floating Button).
*   **Trigger**: User clicks "Ask AI".
*   **User Query**: "Why did we miss budget last month?"
*   **Backend Flow**:
    1.  Frontend calls `POST /api/chat` with `{ session_id, message }`.
    2.  Backend routing: `Supervisor Agent`.
    3.  **Supervisor** delegates to **Market Agent** (fetch past events) and **Strategy Agent** (analyze variance).
    4.  Response streamed back.
*   **UX Feature**: **Citation**. If Agent used "Knowledge Base", show citation: *Source: SOP Document v2, Page 4*.

### 2.3 Approval Workflows (Human-in-the-Loop)
When an agent wants to *write* data (e.g., Change Rates), it **must** pause for approval.
*   **Mechanism**:
    1.  Agent returns a structured "Tool Call Request" (JSON).
    2.  Backend intercepts this and *does not* execute. Returns JSON to Frontend.
    3.  **Frontend**: Renders a "Confirmation Modal".
        *   *Action*: Update Rates
        *   *Params*: { date: '2025-12-25', rate: 450 }
    4.  **User**: Clicks "Confirm".
    5.  **Frontend**: Sends `POST /api/actions/confirm { id: ... }`.
    6.  Backend executes the actual PMS write.

## 3. Experience Transformation

The move to Agentic AI fundamentally shifts the user role from **Operator** (data entry) to **Supervisor** (approver).

| Feature | Current State (Legacy) | Future State (Agentic AI) |
| :--- | :--- | :--- |
| **Market Data** | User manually checks external sites (events, competitors). | **Market Agent** auto-fetches events & competitor rates 24/7. |
| **Pricing** | User calculates rates in Excel, types them into calendar. | **Strategy Agent** proposes rates based on math; User clicks "Approve". |
| **Analysis** | "Why is occupancy low?" -> User digs through 10 reports. | **Chat Assistant** explains: "Low because Art Basel ended early." |
| **Responsiveness** | Reactive. User notices problem days later. | Proactive. **Insight Card** alerts user *before* the problem happens. |
| **Knowledge** | Policy buried in PDFs. Team makes mistakes. | **Knowledge Base** enforces SOPs instantly (RAG). |

---

## 4. Implementation Plan (Frontend)

### Phase 1: Dashboard Insight (MVP)
*   [x] Backend Endpoint (`dashboardController.js`)
*   [x] Frontend Widget (`Dashboard.jsx`) - *Implemented & Connected*

### Phase 2: Chat Interface
*   New Context: `AgentContext.jsx` (Manages chat history/session).
*   New Component: `ChatWindow.tsx` (using Tailwind).

### Phase 3: Action Feed
*   New Page: `/actions` showing pending Agent proposals.
