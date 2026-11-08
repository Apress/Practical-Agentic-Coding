# Phase 2 UI Implementation: Agentic Features

> **Note:** This guide refers to React source (`src/context/`, `src/components/`, `src/layouts/MainLayout.jsx`) that is not published in this repository. Read it as the plan for that code.

## 1. Overview
This guide details the technical implementation of the Agentic UI components (Chat, Insights, Workflows) into the existing React application.
It translates the [UX Mocks](./mocks/agent_ux_mocks.html) into reusable React components.

## 2. Dependencies
Ensure the following packages are installed:
```bash
npm install lucide-react react-markdown clsx tailwind-merge
```

## 3. Directory Structure
```text
src/
  ├── context/
  │   └── AgentContext.jsx       # Global state for Chat & Sessions
  ├── components/
  │   ├── agent/                 # NEW Folder for Agentic UI
  │   │   ├── ChatWidget.jsx     # The floating chat window
  │   │   ├── ChatMessage.jsx    # Individual bubbles (User vs Agent)
  │   │   └── ActionModal.jsx    # Reusable approval dialog
  │   ├── dashboard/
  │   │   └── InsightCard.jsx    # Refactored "Nudge" component
```

## 4. Component Architectures

### 4.1 AgentContext (`src/context/AgentContext.jsx`)
Manages the global state of the AI Assistant so the conversation persists as the user navigates between pages.
*   **State**:
    *   `isChatOpen`: boolean
    *   `messages`: Array<{ id, role, content, timestamp }>
    *   `isTyping`: boolean
*   **Actions**:
    *   `sendMessage(text)`: Calls backend API.
    *   `toggleChat()`

### 4.2 ChatWidget (`src/components/agent/ChatWidget.jsx`)
The floating component that lives in the `MainLayout`.
*   **Position**: `fixed bottom-6 right-6`.
*   **Behavior**:
    *   Collapsed: Shows Avatar Button.
    *   Expanded: Shows Header + Scrollable List + Input.
*   **Props**: None (Consumes `AgentContext`).

### 4.3 ActionModal (`src/components/agent/ActionModal.jsx`)
A generic modal for approving Agent actions (Price Updates, Promos).
*   **Props**:
    *   `isOpen`: boolean
    *   `title`: string
    *   `description`: string
    *   `data`: Array<{ label, oldValue, newValue }> (For table view)
    *   `onConfirm`: () => Promise<void>
    *   `onCancel`: () => void

## 5. Implementation Steps

### Step 1: Create the Context
Create `AgentContext.jsx` to wrap your application. This allows any component (header, dashboard, etc.) to trigger the AI.

### Step 2: Build the Global Chat
Interact with `src/api/chat` (needs to be created).
*   Use `react-markdown` to render the Agent's sophisticated responses (bolding, lists).
*   Implement "Streaming" effect (optional, but recommended for perceived speed).

### Step 3: Refactor Dashboard
Extract the existing "Gradient Card" code from `Dashboard.jsx` into `InsightCard.jsx`.
*   Connect it to the `ActionModal` instead of using `window.alert`.

### Step 4: Update Layout
In `src/layouts/MainLayout.jsx`:
```jsx
return (
  <AgentProvider>
    <div className="app-container">
      <Sidebar />
      <main>{children}</main>
      <ChatWidget /> {/* Always visible */}
    </div>
  </AgentProvider>
);
```

## 6. Styling Reference (Tailwind)
Use the classes defined in `agent_ux_mocks.html`:
*   **Chat Header**: `bg-slate-900 text-white`
*   **Agent Bubble**: `bg-white border border-slate-200 text-slate-700`
*   **User Bubble**: `bg-indigo-600 text-white`
*   **Action Button**: `bg-indigo-600 hover:bg-indigo-700 text-white`

## 7. API Integration
*   **Chat**: `POST /api/chat` -> `{ session_id, message }`
*   **Approvals**: `POST /api/dashboard/insight/approve` -> `{ id }`
