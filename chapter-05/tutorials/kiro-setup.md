# Kiro Setup Guide

This guide installs and configures Kiro, the agentic IDE that Chapter 5 uses. At the end you have a working Kiro environment for the lab.

> **Update (as of November 7, 2026)**
>
> - The filesystem and memory MCP servers in `../code-examples/mcp-configs/development-tools.json` require Node.js 24 or later. On older Node, npm first prints an `npm warn EBADENGINE` Unsupported engine block.
> - Kiro opens a folder you have not trusted in Restricted Mode, without asking. In Restricted Mode it does not load the folder's steering files or MCP configuration, and it does not run the folder's hooks. Trust the folder before you start (see [Step 2: Open in Kiro](#step-2-open-in-kiro)).

For the latest install steps, see Kiro's own [installation guide](https://kiro.dev/docs/getting-started/installation/) and the [Kiro documentation](https://kiro.dev/docs/).

## Prerequisites

You need:

- A supported operating system for the IDE. The [installation page](https://kiro.dev/docs/getting-started/installation/) has the current list.
  - macOS (Intel or Apple Silicon)
  - Windows 10 or 11 (x64 or ARM64)
  - Linux (Ubuntu 24+, Debian 13+, Fedora 40+, Arch, or Mint 22+) on x86_64 or ARM64
- An internet connection. The models run in the cloud.
- An account to sign in with: GitHub, Google, AWS Builder ID, or your organization's identity provider.
- An AWS account for the lab's Bedrock and deployment phases. Kiro itself does not need one.

## Installation

### Step 1: Download Kiro

1. Go to [https://kiro.dev/docs/getting-started/installation/](https://kiro.dev/docs/getting-started/installation/).
2. Select your operating system.
3. Download the installer package.

### Step 2: Install Kiro

Run the installer you downloaded. Installer names and channels change, so follow the [installation page](https://kiro.dev/docs/getting-started/installation/) for your platform. It also lists any package-manager route.

- **Windows**: Run the downloaded installer.
- **macOS**: Open the disk image and drag Kiro to Applications.
- **Linux**: Install the downloaded package with your distribution's package manager.

### Step 3: First Launch

1. Open Kiro from your applications menu.
2. Sign in (see Authentication below).
3. Optional: import your VS Code settings and extensions, or pick a theme.
4. Open a folder from the welcome page.

## Authentication

Kiro needs a signed-in account for its AI features.

### Step 1: Sign In

1. On the welcome screen, choose a sign-in method:
   - **GitHub**
   - **Google**
   - **AWS Builder ID**
   - **Your organization**: AWS IAM Identity Center or an external identity provider such as Okta or Microsoft Entra ID. Your admin supplies the start URL.
2. Kiro opens your default browser. Sign in there and authorize the Kiro app.
3. The browser returns you to Kiro, signed in.

The [authentication guide](https://kiro.dev/docs/getting-started/authentication/) has the details for each provider. To sign out later, run **Kiro: Sign Out** from the command palette.

### Step 2: Know Your Plan

Kiro meters work in credits. Each model has a different credit cost per request. Treat your remaining credits as a budget, not a request count. The plan names and limits are on the Kiro pricing page and change over time.

If sign-in fails, or Kiro still shows you as signed out, sign out and sign back in first.

## AWS Configuration (Optional but Recommended)

Configure AWS credentials for the Daily Briefing Lab and other AWS projects.

### Step 1: Install AWS CLI

Use AWS's install script. On macOS and Linux:

```bash
curl -fsSL https://awscli.amazonaws.com/v2/install.sh | bash
```

On Windows (PowerShell):

```powershell
irm https://awscli.amazonaws.com/v2/install.ps1 | iex
```

Open a new terminal and run `aws --version` to confirm. The [AWS CLI install guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) covers the package installers and all-users installs.

### Step 2: Configure AWS Credentials

```bash
aws configure

# Enter when prompted:
# AWS Access Key ID: [Your access key]
# AWS Secret Access Key: [Your secret key]
# Default region name: us-east-1
# Default output format: json
```

### Step 3: Verify AWS Access

```bash
aws sts get-caller-identity
```

Check that it prints your account information.

## Configuring Kiro Settings

### Essential Settings

Open Kiro Settings (Cmd/Ctrl + ,). The settings tree changes between Kiro releases. Look for the items below by name.

#### Model Selection

Leave model selection on **Auto**. The lab assumes Auto. The available models and their credit costs are listed at [kiro.dev/docs](https://kiro.dev/docs/). The lineup changes, so check there.

When to override Auto and why: Chapter 5, Section 5.3.

#### Context

Check that `AGENTS.md` is picked up. Steering files and file context both use up the context window.

How the context tiers work: Chapter 5, Section 5.3.

#### Steering Files

- Workspace steering lives in `.kiro/steering/` in the project root.
- Global steering lives in `~/.kiro/steering/` in your home directory.
- Workspace steering wins when the two conflict.

You do not turn steering on. A file in the directory is enough, once the folder is trusted. In Restricted Mode, Kiro loads only global steering.

## Creating Your First Project

### Step 1: Create Project Folder

```bash
mkdir daily-briefing-agent
cd daily-briefing-agent
```

### Step 2: Open in Kiro

1. Launch Kiro.
2. Select File > Open Folder.
3. Select your `daily-briefing-agent` folder.
4. Trust the folder:
   1. Run **Workspaces: Manage Workspace Trust** from the command palette.
   2. Choose **Trust Folder**.
   3. Run **Developer: Reload Window**.

### Step 3: Create Steering Files

1. Open the Kiro panel (the ghost icon in the activity bar).
2. Choose **Generate Steering Docs**.

Kiro analyzes the folder and writes three steering files to `.kiro/steering/`. Every interaction includes them by default.

1. **product.md**: purpose, target audience, key features, business objectives
2. **tech.md**: frameworks, libraries, tools, technical constraints
3. **structure.md**: file organization, naming conventions, import patterns

Review what Kiro wrote. You can also start from the templates in [`../code-examples/steering-files/`](../code-examples/steering-files/). The hands-on lab starter project already ships all three files, so you do not need to write them for the lab. The [first-project guide](https://kiro.dev/docs/getting-started/first-project/) has the current walkthrough.

## Verifying Installation

### Quick Verification Steps

1. **Open Kiro Chat.** The chat pane is open by default. If you closed it, reopen it from the Kiro panel or the command palette.
2. **Send a test message**: "Hello, what can you help me with?"
3. **Check the response.** Kiro should answer.

### Check Kiro Features

Check each feature:

| Feature | How to check | Expected result |
|---------|--------------|-----------------|
| Chat | Open the chat panel from the sidebar | Chat panel opens and answers a test message |
| Specs | Click the Kiro (ghost) icon in the left rail | SPECS section visible, with a (+) to add one |
| Hooks | Same panel | AGENT HOOKS section visible |
| Powers | The Powers panel (ghost icon with a lightning bolt) | Powers panel opens with Available Powers |
| MCP | The MCP entry in the Kiro menu or settings | MCP server configuration reachable |

Keyboard shortcuts vary by platform and release. If a shortcut does not work, find the command in the command palette (Cmd/Ctrl + Shift + P).

## Installing Additional Tools

### Node.js (needed for the npx-launched MCP servers)

Several MCP servers in this chapter launch through `npx`. This includes the local PostgreSQL server (MCP Toolbox for Databases). `npx` ships with Node.js and npm. Check your versions:

```bash
node --version   # any current LTS release; 24 or later for the filesystem and memory servers
npx --version
```

If either is missing, install Node.js from [nodejs.org](https://nodejs.org/) or your platform's package manager. See the update callout at the top for the Node.js 24 requirement.

### Docker (needed for LocalStack and Docker-based MCP servers)

- On macOS or Windows, install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
- On Linux, install Docker Engine from your distribution's packages.

Follow the [official install docs](https://docs.docker.com/get-docker/) for your platform.

Check that the daemon is running:

```bash
docker ps
```

If that errors, start Docker before you continue. These depend on Docker:

- LocalStack
- The container build
- Docker-based MCP servers, such as the GitHub server
- A local Postgres container, if you run one for the PostgreSQL MCP server to talk to

The PostgreSQL MCP server itself runs through `npx`, not Docker.

On Linux, add yourself to the `docker` group so you do not need `sudo` for every command. Then log out and back in:

```bash
sudo usermod -aG docker "$USER"
```

### Python (needed for the Daily Briefing lab)

Check your version:

```bash
python3 --version   # 3.11 or newer
```

If it is older or missing, install a current Python from [python.org](https://www.python.org/downloads/) or your platform's package manager. The lab's spec constraint pins Python 3.13. The starter scaffold runs on 3.11 and up.

## Troubleshooting

### Common Issues

#### "Unable to connect to AI service"

1. Check your internet connection.
2. Check your authentication status in the account panel.
3. Check whether your plan has credits left.

#### MCP server will not connect

1. For Docker-based servers (such as GitHub's `ghcr.io/github/github-mcp-server`), check that Docker is running: `docker ps`.
2. For the local PostgreSQL server (MCP Toolbox for Databases via `npx`), check that Node.js is installed and the `POSTGRES_*` environment variables are set.
3. For AWS MCP servers, check that your AWS profile resolves: `aws sts get-caller-identity`.
4. Check that nothing else holds the port the server needs.

#### Steering files not loading

1. Check that the folder is trusted (**Workspaces: Manage Workspace Trust**). In Restricted Mode, Kiro loads only the global steering in `~/.kiro/steering/`.
2. Check that the files are in `.kiro/steering/` and end in `.md`.
3. Check the YAML front matter:
   - The delimiters are three hyphens on their own lines.
   - `inclusion` must be `always`, `fileMatch`, `manual`, or `auto`.
   - `auto` also requires `name` and `description` keys.
4. For `fileMatch`, check that the `fileMatchPattern` matches the files you are editing. For `auto`, check that the `description` describes the requests that should trigger the file.
5. Restart Kiro.
6. Ask Kiro: "What do you know about this project's conventions?" If the answer does not reflect your steering, Kiro is not reading it.

### Getting Help

- **Kiro documentation**: [kiro.dev/docs](https://kiro.dev/docs/)
- **Kiro Chat**: Paste the error text and ask Kiro to diagnose it. This is usually the fastest route. See Section 5.7 (Phase 5).
- **AWS Support**: For AWS account, quota, and Bedrock model-access issues.

## Next Steps

1. Read the [SDD Methodology Tutorial](./sdd-methodology.md).
2. Read the [Steering Files](./steering-files-guide.md) guide.
3. Start the [Daily Briefing Lab](../hands-on-lab/README.md).

## Quick Reference

### Getting Around

| Action | Where |
|--------|-------|
| Command palette | Cmd/Ctrl + Shift + P. Use this when a shortcut does not work |
| Settings | Cmd/Ctrl + , |
| Chat | The chat panel in the sidebar |
| New spec | The (+) in the SPECS section of the Kiro (ghost) panel |
| New hook | The (+) in the AGENT HOOKS section |
| Install a Power | The POWERS section |

### Important Paths

| Path | Purpose |
|------|---------|
| `.kiro/steering/` | Project steering files |
| `.kiro/specs/` | Spec documents |
| `.kiro/hooks/` | Hook configurations |
| `.kiro/settings/mcp.json` | MCP server config |
| `~/.kiro/steering/` | Global steering files |

## Summary

Check that you now have:

- Kiro installed and signed in, with SPECS and AGENT HOOKS visible and the Powers panel reachable
- AWS credentials configured and verified with `aws sts get-caller-identity`
- Node.js and npm for the `npx`-launched MCP servers
- Docker running
- Python 3.11 or newer
- The locations of steering, specs, hooks, and MCP configuration

Next: [the SDD methodology tutorial](./sdd-methodology.md), then [the hands-on lab](../hands-on-lab/README.md).
