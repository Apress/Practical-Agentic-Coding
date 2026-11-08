# Decision Authority Matrix

From Chapter 3, Section 3.3 (Decision-Making Protocols, Table 3.1). Each row assigns one decision type to one of three modes:

- The agent acts on its own.
- The agent drafts, and a human approves.
- A human makes the call.

When to use each mode and why: Chapter 3, Section 3.3.

1. Copy this file into your team's working agreement.
2. Edit the rows to match your own decision types. The starting rows below are the sample framework from the book.

## The matrix

| Decision type | AI autonomous | Human-AI collaborative | Human |
|---------------|:-------------:|:----------------------:|:-----:|
| Code formatting & style | X | | |
| Standard pattern implementation | X | | |
| Unit test generation | X | | |
| Simple bug fixes | X | | |
| API integration approach | | X | |
| Performance optimization strategy | | X | |
| Security implementation | | X | |
| Feature prioritization | | | X |
| Architecture decisions | | | X |
| Customer communication | | | X |
| *(add your own decision types)* | | | |
| | | | |
| | | | |

## Column meanings

- **AI autonomous**: the agent acts without waiting for approval.
- **Human-AI collaborative**: the agent proposes. A human reviews and decides.
- **Human**: the agent defers entirely.

Review the matrix in your retrospectives (see [hybrid-retrospective-format.md](hybrid-retrospective-format.md)). Move rows between columns as your team decides.
