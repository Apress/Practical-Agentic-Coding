# Integrations Quick Index

**Quick navigation guide for the integrations directory**

---

## Quick Start

### New to Exercise 3?
1. Start here: [`observability_setup.md`](./observability_setup.md) (15 min read)
2. Then follow: [`sentry_setup.md`](./sentry_setup.md) (10 min setup)
3. Verify: Run `python integrations/test_sentry_connection.py`
4. Implement: Complete TODOs in [`sentry_integration.py`](./sentry_integration.py)

### Want Visualization?
- Optional: [`grafana_setup.md`](./grafana_setup.md)
- Import dashboards from [`grafana_dashboards/`](./grafana_dashboards/)

---

## Documentation Files

### Essential Reading

**[`observability_setup.md`](./observability_setup.md)** - Read First
- Complete observability architecture
- How Prometheus, Sentry, and Grafana work together
- What you need for each exercise
- Data flow
- **Time**: 15 minutes
- **Audience**: Everyone

**[`sentry_setup.md`](./sentry_setup.md)** - Exercise 3 Required
- Step-by-step Sentry account creation
- Free Developer plan signup
- How to get your DSN
- Configuration and verification
- Troubleshooting common issues
- **Time**: 10-15 minutes
- **Audience**: Exercise 3 students

### Optional Reading

**[`grafana_setup.md`](./grafana_setup.md)** - Optional
- Local and cloud Grafana setup
- Dashboard import and customization
- Creating visualizations
- Alerting configuration
- **Time**: 15-20 minutes
- **Audience**: Advanced students

**[`README.md`](./README.md)** - Reference Guide
- Complete directory overview
- Integration patterns
- Usage instructions
- Testing procedures
- **Time**: 20 minutes
- **Audience**: All students

---

## Code Files

### Implementation

**[`sentry_integration.py`](./sentry_integration.py)** - Skeleton Code
- `SentryMonitor` class with TODOs
- Part 1: Initialize Sentry SDK
- Part 2: Report deployment events
- Part 3: Query error rates
- Part 4: Report rollbacks
- Includes test script at bottom
- **Usage**: Complete TODOs, then run directly to test
- **Test**: `python integrations/sentry_integration.py`

### Verification

**[`test_sentry_connection.py`](./test_sentry_connection.py)** - Setup Validator
- Checks environment configuration
- Verifies Sentry SDK installed
- Tests DSN validity
- Sends test events
- Provides clear error messages
- **Usage**: `python integrations/test_sentry_connection.py`
- **Run**: Before implementing integration

---

## Dashboard Files

### Templates

All located in [`grafana_dashboards/`](./grafana_dashboards/)

**[`deployment-metrics.json`](./grafana_dashboards/deployment-metrics.json)**
- Deployment success rates
- Duration tracking
- Frequency analysis
- **Metrics needed**: `deployment_total`, `deployment_duration_seconds`

**[`error-tracking.json`](./grafana_dashboards/error-tracking.json)**
- Error rate monitoring
- Correlation with deployments
- Top error types
- **Metrics needed**: `http_requests_total`, `sentry_errors_total`

**[`rollback-analysis.json`](./grafana_dashboards/rollback-analysis.json)**
- Rollback frequency
- MTTR (Mean Time to Rollback)
- Reason breakdown
- **Metrics needed**: `deployment_rollback_total`, `rollback_duration_seconds`

### Dashboard Guide

**[`grafana_dashboards/README.md`](./grafana_dashboards/README.md)**
- How to import dashboards
- Customization guide
- PromQL query examples
- Alerting setup

---

## By Use Case

### "I'm starting Exercise 3"
1. Read [`observability_setup.md`](./observability_setup.md)
2. Follow [`sentry_setup.md`](./sentry_setup.md)
3. Run [`test_sentry_connection.py`](./test_sentry_connection.py)
4. Complete TODOs in [`sentry_integration.py`](./sentry_integration.py)
5. Test: `python integrations/sentry_integration.py`

### "I want to visualize metrics"
1. Read [`grafana_setup.md`](./grafana_setup.md)
2. Start Grafana: `docker compose up -d grafana`
3. Import dashboards from [`grafana_dashboards/`](./grafana_dashboards/)
4. Reference [`grafana_dashboards/README.md`](./grafana_dashboards/README.md)

### "My Sentry setup isn't working"
1. Run [`test_sentry_connection.py`](./test_sentry_connection.py)
2. Check troubleshooting in [`sentry_setup.md`](./sentry_setup.md)
3. Verify DSN in `.env` file
4. Review common issues in [`README.md`](./README.md)

### "I want to understand the architecture"
1. Read [`observability_setup.md`](./observability_setup.md)
2. Review integration patterns in [`README.md`](./README.md)
3. Examine code structure in [`sentry_integration.py`](./sentry_integration.py)

### "I'm creating custom dashboards"
1. Read [`grafana_dashboards/README.md`](./grafana_dashboards/README.md)
2. Study example templates in [`grafana_dashboards/`](./grafana_dashboards/)
3. Reference PromQL examples
4. Export and save your custom dashboards

---

## Checklists

### Exercise 3 Setup Checklist
- [ ] Read `observability_setup.md`
- [ ] Created Sentry account (free tier)
- [ ] Got DSN from Sentry dashboard
- [ ] Added DSN to `.env` file
- [ ] Ran `test_sentry_connection.py` successfully
- [ ] All tests passed
- [ ] Seen test events in Sentry dashboard

### Implementation Checklist
- [ ] Completed Part 1: `__init__` method
- [ ] Completed Part 2: `report_deployment_start` and `report_deployment_complete`
- [ ] Completed Part 3: `get_error_rate` (simulated or API)
- [ ] Completed Part 4: `report_rollback`
- [ ] Ran `python integrations/sentry_integration.py`
- [ ] Test events appear in Sentry
- [ ] Integrated into `starter/deployer.py`

### Grafana Setup Checklist (Optional)
- [ ] Read `grafana_setup.md`
- [ ] Started Grafana (local or cloud)
- [ ] Logged into Grafana
- [ ] Added Prometheus data source
- [ ] Imported `deployment-metrics.json`
- [ ] Imported `error-tracking.json`
- [ ] Imported `rollback-analysis.json`
- [ ] Dashboards showing data

---

## Search by Topic

### Account Setup
- Sentry: [`sentry_setup.md`](./sentry_setup.md)
- Grafana: [`grafana_setup.md`](./grafana_setup.md)

### Architecture
- Overview: [`observability_setup.md`](./observability_setup.md)
- Patterns: [`README.md`](./README.md)

### Implementation
- Skeleton code: [`sentry_integration.py`](./sentry_integration.py)
- Testing: [`test_sentry_connection.py`](./test_sentry_connection.py)

### Visualization
- Setup: [`grafana_setup.md`](./grafana_setup.md)
- Dashboards: [`grafana_dashboards/`](./grafana_dashboards/)
- Guide: [`grafana_dashboards/README.md`](./grafana_dashboards/README.md)

### Troubleshooting
- Sentry: [`sentry_setup.md`](./sentry_setup.md) (Common Issues section)
- General: [`README.md`](./README.md) (Troubleshooting section)
- Dashboards: [`grafana_dashboards/README.md`](./grafana_dashboards/README.md) (Troubleshooting section)

---

## What each file is for

| File | Type | Purpose |
|------|------|---------|
| `observability_setup.md` | Doc | How Prometheus, Sentry, and Grafana fit together |
| `sentry_setup.md` | Doc | Creating the account, project, and DSN |
| `grafana_setup.md` | Doc | Running and configuring Grafana (optional) |
| `README.md` | Doc | Full reference for this directory |
| `sentry_integration.py` | Code | `SentryMonitor` scaffold, TODOs are Exercise 3 |
| `test_sentry_connection.py` | Code | Verifies your DSN and SDK before you start |
| `grafana_dashboards/*.json` | Config | Three importable dashboards |
| `grafana_dashboards/README.md` | Doc | How to import and read them |

---

## Learning Path

### Beginner (Exercise 3 Start)
1. [`observability_setup.md`](./observability_setup.md) - See how the pieces fit
2. [`sentry_setup.md`](./sentry_setup.md) - Set up account
3. [`test_sentry_connection.py`](./test_sentry_connection.py) - Verify setup
4. [`sentry_integration.py`](./sentry_integration.py) - Implement TODOs

### Intermediate (Exercise 3 Complete)
1. [`README.md`](./README.md) - Integration patterns
2. Complete all TODOs in `sentry_integration.py`
3. Test with real deployments
4. View events in Sentry dashboard

### Advanced (Optional)
1. [`grafana_setup.md`](./grafana_setup.md) - Add visualization
2. [`grafana_dashboards/README.md`](./grafana_dashboards/README.md) - Learn dashboarding
3. Import and customize dashboards
4. Create custom metrics and visualizations
5. Set up alerting

---

## Quick Commands

### Testing
```bash
# Verify Sentry connection
python integrations/test_sentry_connection.py

# Test Sentry integration
python integrations/sentry_integration.py

# Check Prometheus
curl http://localhost:9090/-/healthy
```

### Grafana
```bash
# Start local Grafana
docker compose up -d grafana

# Open Grafana
open http://localhost:3000

# Stop Grafana
docker compose stop grafana
```

### Deployment Testing
```bash
# Run the deployer end to end (mock infrastructure); with SentryMonitor
# wired into your deployer, events fire during these runs
pytest starter/tests/test_integration.py -v
```

---

## External Resources

### Official Documentation
- **Sentry**: https://docs.sentry.io/platforms/python/
- **Prometheus**: https://prometheus.io/docs/
- **Grafana**: https://grafana.com/docs/

### Signup Links
- **Sentry Free Tier**: https://sentry.io/signup/
- **Grafana Cloud**: https://grafana.com/auth/sign-up/create-user

### Community
- **Sentry Discussions**: https://github.com/getsentry/sentry/discussions
- **Grafana Community**: https://community.grafana.com/

---

## Getting Help

### In Order of Preference

1. **Run test scripts** - They provide specific error messages
2. **Check troubleshooting sections** - In relevant docs
3. **Review this index** - Find the right guide
4. **Read README** - Full reference
5. **Check external docs** - Official documentation

### Common Issues Quick Links

| Issue | Solution |
|-------|----------|
| Sentry events not appearing | [`sentry_setup.md`](./sentry_setup.md#common-setup-issues) |
| DSN placeholder error | [`test_sentry_connection.py`](./test_sentry_connection.py) output |
| Grafana "No Data" | [`grafana_dashboards/README.md`](./grafana_dashboards/README.md#troubleshooting) |
| Import errors | [`README.md`](./README.md#common-issues) |
| Prometheus not running | [`observability_setup.md`](./observability_setup.md#troubleshooting) |

---

## Success Criteria

You're ready to proceed when:

- [x] Sentry account created and DSN obtained
- [x] `test_sentry_connection.py` passes all checks
- [x] Test events visible in Sentry dashboard
- [x] TODOs in `sentry_integration.py` completed
- [x] Integration test successful
- [x] Events from deployer appear in Sentry

Optional (Grafana):
- [ ] Grafana running and accessible
- [ ] Prometheus data source connected
- [ ] Dashboards imported and showing data

---

## Notes

### For Students
- All materials use placeholders - you can complete exercises without real services
- Sentry integration is optional but recommended for Exercise 3
- Grafana is completely optional for visualization
- Get the code working first, then add real services

### For Instructors
- Materials tested in clean environment
- Placeholder mode works without external dependencies
- Clear progression: understand → setup → implement → verify
- All external signups are free tier

---

**Need to start?** Go to [`observability_setup.md`](./observability_setup.md) to understand the architecture, then follow [`sentry_setup.md`](./sentry_setup.md) to begin Exercise 3.

**Questions?** Check [`README.md`](./README.md) for the full reference and troubleshooting.
