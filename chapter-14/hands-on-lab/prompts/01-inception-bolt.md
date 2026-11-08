# Prompt: Inception Bolt (Step 1)

Paste into Claude Code after installing the AI-DLC 1.x rules (see the lab README):

```text
Using AI-DLC, I need to add notification preferences to our user
service. We need endpoints for getting, updating, and deleting
notification preferences. Supported channels: email, SMS, push.
```

AI-DLC starts and asks you directed questions. Expect questions like these:

- Which channels are mandatory vs optional?
- Opt-in or opt-out default?
- Rate limits on preference changes?
- Preference inheritance for team accounts?

Answer honestly. "I don't know, propose a default" is a valid answer. It
becomes a documented design decision. Approve the Inception artifacts
(requirements, design decisions) before you move to Construction.
