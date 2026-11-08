# Contributing to Apress Source Code

Copyright for Apress source code belongs to the author(s). However, under fair use you are encouraged to fork and contribute minor corrections and updates for the benefit of the author(s) and other readers.

## How to Contribute

1. Make sure you have a GitHub account.
2. Fork the repository for the relevant book.
3. Create a new branch on which to make your change, e.g.
`git checkout -b my_code_contribution`
4. Commit your change. Include a commit message describing the correction. Please note that if your commit message is not clear, the correction will not be accepted.
5. Submit a pull request.

If you find a problem you do not want to fix yourself, open an issue at [github.com/Apress/Practical-Agentic-Coding/issues](https://github.com/Apress/Practical-Agentic-Coding/issues) instead.

## What helps most

- **Corrections**: a lab step that does not work, a broken link, or a command that fails on your platform. Say which chapter and which file. Say what you saw.
- **Tool drift**: a CLI flag or install path that works differently from the lab. Link to the vendor documentation that shows the current behavior.
- **Platform notes**: a Windows, macOS, or Linux variation of a command that the lab does not cover.

Before you open a pull request, check these two points:

- The `starter/` directories are incomplete on purpose. The `TODO` comments there are the exercise. Please do not submit solutions for them.
- Code here matches the listings printed in the book. A change that improves the code but does not match the book can confuse a reader following along. If you think the change is worth it anyway, say so in the pull request. We will note the difference in the chapter README.

For repository conventions (where things go, naming, the pre-push checklist), see [MAINTENANCE.md](MAINTENANCE.md). For book text corrections, see [errata.md](errata.md).

Thank you for your contribution!
