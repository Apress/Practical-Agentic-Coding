# Phase 1 Vibe Output

**Reference**: Chapter 5, Section 5.7, Phase 1 (The "Vibe" Prompt)

## What This Is

Kiro wrote these four files on its own. It wrote them in response to the vibe prompt in Phase 1 of the hands-on lab, in the author's session.

The prompt asked only for a persona and a purpose. Kiro answered with:

- A concept brief
- An MVP feature list
- A set of persona voice samples
- A tech-stack survey

## The Files

| File | What Kiro produced |
|------|--------------------|
| `concept-exploration.md` | Open questions on content strategy, UX, technical approach, and monetization |
| `mvp-features.md` | A must-have / nice-to-have split for phase one |
| `persona-voice-examples.md` | Three worked before-and-after summaries showing the witty voice |
| `tech-stack-considerations.md` | Frontend, backend, data, AI, and deployment options with trade-offs |

## What to Compare

Compare `tech-stack-considerations.md` with the constraints in Phase 2 of the lab.

- Kiro's survey recommends a starting stack of Next.js, Node.js with Express, the OpenAI API, and Vercel plus Railway.
- The Phase 2 spec pins Python 3.13, Flask, Amazon Bedrock, and AWS.
- None of the recommended stack survived. The pieces that did (Python, PostgreSQL, Claude, AWS) appear in the survey only as alternatives.

Use `persona-voice-examples.md` to calibrate the persona's tone.

Why vibe and spec differ: Chapter 5, Section 5.2.

## What to Do With Them

Read them once, before Phase 2. Do not edit them. They are not inputs to the lab, and none of them belong in `.kiro/`. Your own vibe prompt may produce different artifacts. This is expected. Agentic output varies by model and by phrasing.

To run the comparison yourself:

1. Save whatever Kiro creates during your Phase 1 into a scratch directory.
2. Work through Phase 2.
3. Diff Kiro's technical suggestions against the constraints you stated.

## Related

- Lab walkthrough (Phase 1 prompt): [`../hands-on-lab/README.md`](../hands-on-lab/README.md)
- The specs the same session eventually produced: [`../daily-briefing-agent/`](../daily-briefing-agent/)
- SDD quick reference: [`../tutorials/sdd-methodology.md`](../tutorials/sdd-methodology.md)
