# GitHub Copilot Setup: Quick Reference

Install and configure GitHub Copilot. For the latest steps, see GitHub's own guide at [docs.github.com/copilot](https://docs.github.com/copilot).

What Copilot's modes and surfaces are for, and when to use each: Chapter 7, Section 7.3.

> **Current tool behavior (as of November 7, 2026).** These differ from the printed book:
>
> - **Edit mode is retired.** VS Code deprecated it in version 1.110. VS Code 1.126 and later offer it only when Agent mode is disabled by policy. There is no `/edit` command. See "Agent Mode with a fixed working set" below.
> - **Names.** The book's "Copilot Async Agent" is the Copilot cloud agent. The book's mission control is the agents page at github.com/copilot/agents.

## Prerequisites

- GitHub account
- GitHub Copilot plan. Free covers chat in the IDE. The cloud agent needs any plan except Free.
- Supported IDE (VS Code, Visual Studio, JetBrains, Neovim)

## Subscription Options

As of November 7, 2026, Copilot bills by usage. Each plan comes with an allowance of GitHub AI Credits. Heavier models consume them faster.

Plans are Free, Student, Pro, Pro+, Max, Business, and Enterprise. See [docs.github.com/copilot](https://docs.github.com/copilot) for current allowances and which features each plan includes.

### Enable Copilot

1. Go to [github.com/settings/copilot](https://github.com/settings/copilot).
2. Choose your plan.
3. Complete billing setup.

## IDE Installation

### VS Code

Copilot ships as part of VS Code's built-in AI features. You do not need to find a separate extension first.

1. Open VS Code.
2. Hover over the Copilot icon in the Status Bar and select **Use AI Features**.
3. Choose a sign-in method and sign in with your GitHub account.

### JetBrains (IntelliJ, PyCharm, WebStorm)

1. Open the IDE.
2. Go to Settings > Plugins.
3. Search for "GitHub Copilot".
4. Install it and restart.
5. Sign in with your GitHub account.

### Visual Studio

1. Open Visual Studio.
2. Go to Extensions > Manage Extensions.
3. Search for "GitHub Copilot".
4. Download and install it.
5. Restart Visual Studio.
6. Sign in with your GitHub account.

### Neovim

```vim
" Using vim-plug
Plug 'github/copilot.vim'

" Then run
:Copilot setup
```

## Configure copilot-instructions.md

### Create Repository Instructions

Open the Copilot chat in VS Code and type `/init`. Copilot analyzes the project and generates or updates the workspace instructions. Check which file it wrote, then review it. (The Copilot CLI's `/init` writes `.github/copilot-instructions.md`.)

To write the file by hand:

1. Create `.github/copilot-instructions.md`:

````markdown
# GitHub Copilot Instructions

## Project Overview
[Description of your project]

## Technology Stack
- [List technologies]

## Code Conventions
- [List conventions]

## Common Patterns
```[language]
// Example pattern
```

## Important Notes
- [Any critical information]
````

For rules that apply only to some files, add path-specific files under `.github/instructions/`, for example `api.instructions.md`. Name the files in the `applyTo` frontmatter field, such as `applyTo: "src/api/**/*.py"`. See [`copilot-instructions-guide.md`](copilot-instructions-guide.md) for the format.

### Organization-Wide Instructions

For organization owners:

1. Go to Organization settings.
2. Open Copilot > Custom instructions.
3. Add the instructions.

GitHub documents organization instructions for Copilot Chat on GitHub.com, Copilot code review, and the Copilot cloud agent.

## Copilot Chat Modes

Pick a mode in the mode picker in the Chat view.

### Ask Mode

```text
Explain how the authentication flow works in this project
```

### Agent Mode with a fixed working set

This replaces the book's Edit mode. Attach only the files you want changed. Say so in the prompt. Review each edit before you keep it.

```text
Refactor this function to use async/await. Change only the attached file.
```

### Agent Mode

```text
Run the tests, fix any failures, and verify the fixes
```

### Plan Mode

Pick **Plan** in the mode picker, or start the prompt with `/plan`. Copilot asks clarifying questions, then drafts an ordered plan. It does not change any code.

```text
Plan the migration of the auth module to OAuth 2.0
```

Check the plan. Then hand it to Agent Mode to execute.

### Custom Agents

1. Define reusable agent profiles as `<name>.agent.md` files in `.github/agents/`, for example `security-reviewer.agent.md`.
2. Publish them organization-wide if you need to.
3. If you have custom chat modes, rename each `.chatmode.md` file to `.agent.md`. Custom agents replace them.

`AGENTS.md` in the project root is a separate instructions convention. Copilot auto-detects it alongside `copilot-instructions.md`.

## Copilot Spaces

### Create a Space

1. Go to [github.com/copilot/spaces](https://github.com/copilot/spaces).
2. Click **Create space**.
3. Name the space and choose whether you or an organization owns it. Click **Create Space**.
4. Add sources:
   - Repositories
   - Files
   - Pull requests
   - Issues
   - Text notes

### Use a Space

1. On GitHub.com, open Copilot Chat.
2. Select your Space.
3. Ask your question. Copilot answers from the Space's sources.

In the IDE, Spaces work in agent mode through the GitHub MCP server. Its `copilot_spaces` toolset is off by default. Turn it on as described in GitHub's "Use Copilot Spaces" documentation.

## Copilot CLI

Copilot CLI runs as an agent in your terminal. It can also run unattended in CI. Inside GitHub Actions it authenticates with the workflow's built-in token.

1. Install it with `npm install -g @github/copilot`. This needs Node.js 22 or later. GitHub also documents winget, Homebrew, and an install script.
2. Start a session with `copilot`.
3. Try this prompt:

```text
Summarize the failing tests in this repo and fix the simplest one
```

## Copilot Cloud Agent (Issues)

The Copilot cloud agent works asynchronously on GitHub. To dispatch it, add Copilot as the assignee on an Issue, as you would a coworker. GitHub also provides an assign-to-Copilot button. Assignment also works from the mobile app and the CLI.

### Create an Issue for Copilot

```markdown
Title: Add pagination to user list endpoint

Description:
Add offset/limit pagination to GET /api/users

Requirements:
- Default limit: 20
- Max limit: 100
- Return total count in headers
- Add tests
```

Then pick Copilot in the assignee dropdown.

The cloud agent is not part of Copilot Free. On Business and Enterprise plans it follows the organization's Copilot in the cloud policy. As of November 7, 2026, that policy is on by default. An administrator can turn it off.

### Monitor Agent Progress

1. Assigning an issue always creates a pull request. Follow the session from the issue, the pull request, or the agents page at github.com/copilot/agents.
2. GitHub Actions workflows do not run automatically on the agent's pushes. Approve them with **Approve and run workflows**.
3. Review the work and give feedback in pull request comments.
4. Merge when you are satisfied.

## Enterprise Configuration

### Organization Policies

1. Go to Organization Settings.
2. Open Copilot > Policies.
3. Configure:
   - Which repos can use Copilot
   - Allowed AI models
   - Data handling settings

Organization custom instructions live on their own page, Copilot > Custom instructions. They are not under Policies.

### Audit Logs

1. Go to Organization Settings > Audit log.
2. Filter by "copilot".
3. View usage and actions.

## Keyboard Shortcuts

### VS Code

| Action | macOS | Windows |
|--------|-------|---------|
| Accept suggestion | Tab | Tab |
| Dismiss suggestion | Esc | Esc |
| Next suggestion | Alt+] | Alt+] |
| Previous suggestion | Alt+[ | Alt+[ |
| Open the Chat view | Ctrl+Cmd+I | Ctrl+Alt+I |
| Open chat in agent mode | Shift+Cmd+I | Ctrl+Shift+I (Linux: Ctrl+Shift+Alt+I) |
| Inline Chat | Cmd+I | Ctrl+I |

### Customize

1. Open Keyboard Shortcuts.
2. Search for "copilot".
3. Change the bindings you need.

## Privacy and Security

### Data Handling

- Suggestions are generated in real time.
- Code context is sent to GitHub servers.
- Enterprise plans have options for data residency.

### Exclude Files

Configure Copilot content exclusions in repository or organization settings, under Settings > Copilot > Content exclusion. There is no dotfile for this. Example exclusion patterns:

```yaml
# Repository content exclusion
- ".env"
- "secrets/**"
- "**/*.pem"
- "credentials.json"
```

### Network Requirements

Behind a firewall or proxy, allow the hosts in GitHub's Copilot allowlist reference. Search docs.github.com/copilot for "allowlist". The list changes as GitHub adds services.

## Troubleshooting

### Common Issues

**Suggestions Not Appearing**
1. Check your subscription status.
2. Check network connectivity.
3. Check that the file type is supported.
4. Review the extension logs.

**Chat Not Responding**
1. Check GitHub authentication.
2. Check that the extension is enabled.
3. Sign out and sign back in.

**Agent Mode Not Working**
1. Check that terminal access is enabled.
2. Check workspace trust settings.
3. Check the extension version.

### Reset Copilot

1. Disable the extension.
2. Clear the extension data.
3. Re-enable it and sign in again.

## Resources

- [Official Documentation](https://docs.github.com/copilot)
- [Changelog](https://github.blog/changelog/label/copilot/)
- [GitHub Community](https://github.com/community)
- [Status Page](https://www.githubstatus.com/)
