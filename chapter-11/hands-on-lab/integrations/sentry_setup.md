# Sentry Setup Guide

Step-by-step setup for Sentry error tracking with your Zero-Downtime Deployer.

These steps summarize Sentry's own docs. For the latest, see the [Sentry Python SDK docs](https://docs.sentry.io/platforms/python/).

## What is Sentry?

Sentry is an error tracking platform. In Exercise 3, you use it to track
deployment errors. The deployer rolls back when error rates spike.

---

## Step 1: Create Free Sentry Account

Sentry has a free tier that covers this lab.

### Sign Up

1. Open your browser and go to: **https://sentry.io/signup/**
2. Choose one of these options:
   - Sign up with GitHub (recommended - faster)
   - Sign up with email address
3. If using email:
   - Enter your email address
   - Create a password
   - Click "Sign Up"
   - Check your email for verification link
   - Click the verification link

### What You Get (Free Tier)

As of November 7, 2026, Sentry's free Developer plan includes 5k errors, one
user, and a 30-day lookback. Plans change. Check
[sentry.io/pricing](https://sentry.io/pricing/) for the current terms. The lab
sends only a few events per deployment, so the free plan is enough.

---

## Step 2: Create Your Project

After signing up and logging in:

### Project Creation

1. You'll see the welcome screen
2. Click **"Create Project"** button
3. On the project creation page:
   - **Choose a platform**: Scroll down and select **"Python"**
   - **Alert frequency**: Keep **"Alert me on high priority issues"** (the default)
   - **Project name**: Enter `zero-downtime-deployer-lab`
   - **Team**: Use default team (usually your username)
4. Click **"Create Project"**

### What Happens Next

Sentry then does three things:
- Creates your project
- Shows you setup instructions
- Displays your unique DSN (Data Source Name)

---

## Step 3: Get Your DSN

The DSN is your connection string. It works like an API key for Sentry.

### Locate Your DSN

After creating the project:

1. You'll see a page titled **"Configure Python"**
2. Look for a code block that shows:
   ```python
   sentry_sdk.init(
       dsn="https://abc123def456@o789.ingest.sentry.io/123456",
       ...
   )
   ```
3. The DSN is the long URL in quotes after `dsn=`

### DSN Format

Your DSN looks like:
```text
https://[PUBLIC_KEY]@o[ORG_ID].ingest.sentry.io/[PROJECT_ID]
```

Example:
```text
https://a1b2c3d4e5f6g7h8i9j0@o123456.ingest.sentry.io/789012
```

### Save Your DSN

**IMPORTANT**: Copy this DSN somewhere safe. You'll need it in the next step.

If you lose it:
1. Go to **Settings** (gear icon)
2. Click **Projects**
3. Click your project name
4. Click **Client Keys (DSN)**
5. Copy the DSN shown

---

## Step 4: Configure Your Lab Environment

Next, add Sentry to your deployer configuration.

### Update .env File

1. Open your lab directory in your code editor:
   ```bash
   cd /path/to/Practical-Agentic-Coding/chapter-11/hands-on-lab
   ```

2. Open the `.env` file (if it doesn't exist, copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

3. Find the Sentry section (around line 49):
   ```env
   # -----------------------------------------------------------------------------
   # OPTIONAL: Sentry Integration (Exercise 3)
   # -----------------------------------------------------------------------------
   # Sign up at: https://sentry.io/signup/ (free tier covers this lab)
   # SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
   # SENTRY_ENVIRONMENT=lab
   # SENTRY_TRACES_SAMPLE_RATE=1.0
   ```

4. Uncomment the lines and add your actual DSN:
   ```env
   # -----------------------------------------------------------------------------
   # OPTIONAL: Sentry Integration (Exercise 3)
   # -----------------------------------------------------------------------------
   SENTRY_DSN=https://a1b2c3d4e5f6g7h8i9j0@o123456.ingest.sentry.io/789012
   SENTRY_ENVIRONMENT=lab
   SENTRY_TRACES_SAMPLE_RATE=1.0
   ```

### Configuration Options Explained

- **SENTRY_DSN**: Your unique connection string
- **SENTRY_ENVIRONMENT**: Tags events with "lab" so you can filter them
- **SENTRY_TRACES_SAMPLE_RATE**: Set to 1.0 to capture 100% of transactions (good for the lab)

### Save the File

Save `.env` and close your editor.

---

## Step 5: Verify Sentry Connection

Test that everything is configured correctly.

### Run the Shipped Connection Check

The repo already ships the check. Run it from the lab directory:

```bash
cd /path/to/Practical-Agentic-Coding/chapter-11/hands-on-lab
python integrations/test_sentry_connection.py
```

It runs these steps in order:

1. Loads `.env`.
2. Confirms the Sentry SDK is installed.
3. Checks that the DSN is set, and flags a placeholder.
4. Initializes the SDK.
5. Sends a test event.

Each passing step prints a checkmark. A failing step prints the exact fix.

### Check Sentry Dashboard

1. Go to **https://sentry.io/**
2. Log in if needed
3. Click on your project: **zero-downtime-deployer-lab**
4. Click **"Issues"** in the left sidebar
5. You should see your test event: "Test event from Zero-Downtime Deployer Lab"

If you see the event, Sentry is configured correctly.

---

## Step 6: Understanding the Sentry Dashboard

These are the parts of Sentry's interface the lab uses.

### Key Sections

**Issues**
- Shows all errors and messages captured
- Groups similar errors together
- Displays frequency and last seen time

**Explore** (Traces) and **Dashboards**
- Transaction traces
- Slow operations
- Performance trends

**Releases** (under **Explore**; the lab uses this)
- Track deployments
- Correlate errors with versions
- See which release introduced an error

**Alerts** (under **Monitors**)
- Configure notifications
- Set up email notifications (Slack and other integrations need the Team plan or higher; see sentry.io/pricing)
- Define alert rules

### Event Details

Click on your test event to see:

- **Error message and context**
- **Tags**: environment, server name, etc.
- **Breadcrumbs**: What led to the event
- **Additional data**: Custom context you send

---

## Common Setup Issues

### Issue: "Module 'sentry_sdk' not found"

**Cause**: Sentry SDK not installed

**Solution**:
```bash
pip install sentry-sdk
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### Issue: Events not appearing in dashboard

**Cause 1**: Wrong DSN
- **Check**: Verify DSN in `.env` matches Sentry dashboard
- **Solution**: Copy DSN again from Sentry → Settings → Projects → Client Keys

**Cause 2**: Network connectivity
- **Check**: Can you access https://sentry.io?
- **Solution**: Check firewall, proxy settings

**Cause 3**: Rate limiting (unlikely with free tier)
- **Check**: Are you over the free tier's event quota?
- **Solution**: Use sampling: `SENTRY_TRACES_SAMPLE_RATE=0.1`

### Issue: DSN shows "your-sentry-dsn" in error

**Cause**: Forgot to update `.env` file
**Solution**: Add your actual DSN from Sentry dashboard to `.env`

### Issue: "Invalid DSN" error

**Cause**: DSN format incorrect or contains extra characters
**Solution**:
- Make sure DSN is on one line
- No quotes around the DSN in `.env`
- No extra spaces

---

## Understanding Free Tier Limits

The lab's `SentryMonitor` sends one message each for deployment start,
rollback, and completion. A single deployment uses a handful of events.
Sentry's pricing page explains what counts against each quota. It also says
what happens when you reach it.

### Tips to Stay Under Limit

1. **Use sampling for transactions**:
   ```env
   SENTRY_TRACES_SAMPLE_RATE=0.1  # Only 10% of transactions
   ```

2. **Filter noisy errors** in Sentry dashboard:
   - Go to Settings → Inbound Filters
   - Add patterns to ignore

3. **Focus on errors**, not info messages in production

---

## Next Steps

Now that Sentry is configured:

1. **Complete Exercise 3**: Follow `exercise-3-sentry.md`
2. **Implement `sentry_integration.py`**: Add the skeleton code
3. **Test your integration**: Run deployments and see events in Sentry
4. **Explore dashboards**: Create custom views for your deployments

---

## Additional Resources

### Sentry Documentation
- **Main docs**: https://docs.sentry.io/
- **Python SDK**: https://docs.sentry.io/platforms/python/
- **Configuration**: https://docs.sentry.io/platforms/python/configuration/
- **Enriching events**: https://docs.sentry.io/platforms/python/enriching-events/

### Sentry Python SDK Features
- **Tags**: Categorize and filter events
- **Contexts**: Add custom data to events
- **Breadcrumbs**: Track user actions leading to errors
- **Releases**: Correlate errors with deployments
- **User context**: Track which users hit errors

## Support

### Getting Help

**Sentry Community**:
- GitHub Discussions: https://github.com/getsentry/sentry/discussions
- Discord: https://discord.gg/sentry

**Lab Issues**:
- Check `integrations/observability_setup.md`
- Review Exercise 3 instructions
- Test with `python integrations/test_sentry_connection.py`

### Upgrade Options (Optional)

If you need more than the free tier, check the current plans at sentry.io/pricing.
- **Business plan**: More events, longer retention
- **Enterprise**: Custom pricing

For this lab, the **free tier is enough**.

---

Next, go to Exercise 3 to connect Sentry to your deployer.
