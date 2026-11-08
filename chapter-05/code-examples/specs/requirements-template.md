# Requirements Document Template

## Introduction

[One paragraph describing the feature or system being specified. Include the business context and overall purpose.]

## Glossary

- **[Term 1]**: [Definition - What does this term mean in your domain?]
- **[Term 2]**: [Definition]
- **[Term 3]**: [Definition]

## Requirements

### Requirement 1

**User Story:** As a [user type], I want [goal/desire], so that [benefit/value].

#### Acceptance Criteria

1. WHEN [trigger event] THEN [System Name] SHALL [action/behavior]
2. WHEN [trigger event] THEN [System Name] SHALL [action/behavior]
3. WHERE [condition exists] THEN [System Name] SHALL [action/behavior]
4. IF [error condition] THEN [System Name] SHALL [error handling behavior]

---

### Requirement 2

**User Story:** As a [user type], I want [goal/desire], so that [benefit/value].

#### Acceptance Criteria

1. WHEN [trigger event] THEN [System Name] SHALL [action/behavior]
2. WHEN [trigger event] THEN [System Name] SHALL [action/behavior]
3. WHERE [condition exists] THEN [System Name] SHALL [action/behavior]

---

### Requirement 3 (Non-Functional)

**User Story:** As a [stakeholder type], I want [quality attribute], so that [benefit/value].

#### Acceptance Criteria

1. WHEN [operation occurs] THEN [System Name] SHALL [performance/quality requirement]
2. WHERE [scale condition] THEN [System Name] SHALL [scalability requirement]
3. IF [failure condition] THEN [System Name] SHALL [reliability requirement]

---

## Example: Tech News Aggregator Requirements

Below is a completed example for reference:

### Requirement 1

**User Story:** As a tech-savvy reader, I want to access curated technology news with witty commentary, so that I can stay informed while being entertained by sharp insights.

#### Acceptance Criteria

1. WHEN a user visits the application THEN the Tech News Aggregator SHALL display a feed of curated technology stories
2. WHEN stories are displayed THEN the Tech News Aggregator SHALL present each story with a witty summary that maintains a sharp and slightly cynical tone
3. WHEN presenting summaries THEN the Tech News Aggregator SHALL prioritize substance over hype in the commentary
4. WHEN a user clicks on a story THEN the Tech News Aggregator SHALL provide access to the original source article
5. WHERE stories contain industry buzzwords or hype THEN the Tech News Aggregator SHALL provide skeptical commentary that cuts through marketing language

---

## Writing Tips

### User Story Format

```text
As a [user type],
I want [goal/desire],
so that [benefit/value].
```

### EARS Patterns

| Pattern | Template | Use Case |
|---------|----------|----------|
| **Event-driven** | WHEN [event] THEN system SHALL [response] | User actions, triggers |
| **Conditional** | WHERE [condition] THEN system SHALL [behavior] | Feature flags, permissions |
| **State-dependent** | WHILE [state] THEN system SHALL [behavior] | During processes |
| **Alternative** | IF [condition] THEN system SHALL [behavior] | Error handling, edge cases |

### Acceptance Criteria Checklist

- [ ] Is each criterion testable?
- [ ] Does it use specific, measurable language?
- [ ] Are error scenarios covered?
- [ ] Is the behavior clearly defined?
- [ ] Can it be automated in tests?
