# Chapter 11 Exercises - Zero-Downtime Deployer

These exercises walk you through the Zero-Downtime Deployer from Chapter 11, Section 11.6. You build canary validation and automatic rollback. Sentry integration is optional.

Why canary deployment and automatic rollback work: Chapter 11, Section 11.6.

---

## Overview

You implement three components of a CA/CD deployment pipeline:

1. **Exercise 1**: Canary Deployment with Health Validation (45-60 min)
2. **Exercise 2**: Automatic Rollback (35-50 min)
3. **Exercise 3**: Sentry Integration (30-75 min, Optional)

**Total Time**: about 2 to 4 hours including setup

---

## How to Use These Materials

### For Students

#### Start Here
1. **Read**: `VISUAL_OVERVIEW.md` - Get the big picture
2. **Begin**: `exercise-1-canary.md` - Start with canary deployment
3. **Reference**: `QUICK_REFERENCE.md` - Keep this open while coding
4. **Progress**: Complete exercises in order (1 → 2 → 3)

#### When You're Stuck
- Check the **Progressive Hints** sections (expandable in each exercise)
- Review **Common Pitfalls** sections
- Consult **Debugging Tips**
- Reference `QUICK_REFERENCE.md` for API patterns

#### Resources Included

| File | Purpose | When to Use |
|------|---------|-------------|
| `exercise-1-canary.md` | Main exercise: Canary validation | Working on Exercise 1 |
| `exercise-2-rollback.md` | Main exercise: Rollback logic | Working on Exercise 2 |
| `exercise-3-sentry.md` | Main exercise: Sentry integration | Working on Exercise 3 |
| `VISUAL_OVERVIEW.md` | One-page summary of all exercises | Before starting, for quick reference |
| `QUICK_REFERENCE.md` | API reference and common patterns | While coding (keep it open) |

### For Instructors

#### What the exercises give students

Each exercise has the same supports:
- **Visual diagrams**: architecture and flow, in ASCII so they render anywhere
- **Pseudo-code**: the algorithm in plain language before any Python
- **Progressive hints**: collapsed sections students open only when stuck
- **Common pitfalls**: the mistakes most students make, called out early
- **Success criteria**: an explicit checklist for "am I done?"
- **API examples**: usage patterns for the ready-to-use modules, without the solution

#### Teaching Strategies

**Self-Paced Labs**:
- Students work through at their own pace
- Hints provide support when needed
- No instructor intervention required for common issues

**Instructor-Led Sessions**:
- Use diagrams in presentation
- Live-code with pseudo-code as reference
- Point students to specific hints during lab time
- Use pitfalls section for "common mistakes" discussion

**Assessment**:
- Exercises remain valid assessments
- Hints don't provide complete solutions
- Can assess: problem-solving, code quality, debugging approach

---

## Exercise Structure

Each exercise follows this pattern:

### 1. Introduction
- Learning objectives
- A pointer to the book section that explains the concepts
- Architecture diagrams

### 2. Implementation Strategy
- Visual flow diagrams
- Pseudo-code algorithms
- Progressive hints (expandable)
- API usage examples

### 3. Step-by-Step Guide
- Numbered steps
- Code locations
- Configuration instructions
- Testing commands

### 4. Support Materials
- Common pitfalls (with code examples)
- Debugging tips
- Error scenarios
- Success criteria

### 5. Reference
- Success criteria
- API usage examples
- Next steps

---

## Getting Started

### Prerequisites

1. **Setup Complete**: Run `python verify_setup.py` in parent directory
2. **Dependencies Installed**: `pip install -r requirements.txt`
3. **Environment Configured**: `.env` file with required variables
4. **Memory System**: included with the lab. `memory_integration.py` is a
   simplified version of Chapter 9's DevMemory. You install nothing from
   Chapter 9

### Starting Exercise 1

```bash
# 1. Review the overview
cat VISUAL_OVERVIEW.md

# 2. Open the exercise
cat exercise-1-canary.md

# 3. Keep the quick reference handy
cat QUICK_REFERENCE.md

# 4. Start coding
vim ../starter/deployer.py  # or your editor

# 5. Test frequently
pytest ../starter/tests/test_deployer.py -v -k canary
```

---

## Learning Path

### Recommended Order

```text
Setup (verify_setup.py)
    ↓
Exercise 1: Canary Validation
    ├─ Learn: Monitoring, thresholds, fail-fast
    ├─ Difficulty: Intermediate
    └─ Time: 45-60 minutes
    ↓
Exercise 2: Automatic Rollback
    ├─ Learn: Self-healing, state management, escalation
    ├─ Difficulty: Intermediate-Advanced
    └─ Time: 35-50 minutes
    ↓
Exercise 3: Sentry Integration (Optional)
    ├─ Learn: Observability, external integration
    ├─ Difficulty: Intermediate-Advanced
    └─ Time: 30-75 minutes
```

### Skill Progression

**After Exercise 1**, you can:
- Implement threshold-based validation
- Work with async/await patterns
- Query and use DevMemory
- Make data-driven deployment decisions

**After Exercise 2**, you can:
- Build self-healing systems
- Manage complex state transitions
- Handle failure scenarios gracefully
- Implement escalation logic

**After Exercise 3**, you can:
- Integrate with external services
- Implement bi-directional communication
- Use production observability tools
- Design complete CA/CD pipelines

---

## Support & Resources

### When You're Stuck

**Try This First**:
1. Read the error message carefully
2. Check `QUICK_REFERENCE.md` for API patterns
3. Review the relevant hint section
4. Look at **Common Pitfalls** in the exercise
5. Try debugging with print statements

**Ask for Help When**:
- Stuck for 10+ minutes on the same issue
- Error message is unclear
- You are confused about a concept, not only the syntax
- After trying at least one approach

### Common Issues

#### Exercise 1
- **Missing `await`**: Add `await` before async calls
- **Infinite loop**: Add `await asyncio.sleep(10)`
- **Threshold logic**: Check if using `>` or `<` correctly
- **DevMemory empty**: Expected on first run

#### Exercise 2
- **Wrong version**: Roll back to stable, not failed version
- **Not checking results**: Always check if operations succeeded
- **No stable version**: Handle `None` case
- **Missing escalation**: Critical failures must escalate

#### Exercise 3
- **Module not found**: `pip install sentry-sdk`
- **Events not appearing**: Check if using real or placeholder DSN
- **Sync vs async**: Sentry SDK calls are synchronous (no `await`)

---

## Success Indicators

### You're on the Right Track When:
- Code runs without exceptions
- Some tests are passing
- You can explain what your code does
- You're handling errors appropriately
- Debug prints show expected values

### You're Done When:
- All tests pass
- Code handles edge cases
- You understand why it works
- You can explain the architecture
- You could teach it to another student

---

## What You'll Build

### Complete System Architecture

```text
┌─────────────────────────────────────────────────────┐
│           Zero-Downtime Deployment System            │
└─────────────────────────────────────────────────────┘

Inputs:                     Outputs:
─────────                   ─────────
• Service name              • Deployment success/failure
• Version to deploy         • Detailed validation results
• Deployment config         • Rollback actions taken
                           • Observability events

Components:
───────────
1. Canary Validator (Exercise 1)
   ├─ Metric collection
   ├─ Threshold checking
   ├─ Memory-informed decisions
   └─ Fail-fast detection

2. Automatic Rollback (Exercise 2)
   ├─ State management
   ├─ Traffic shifting
   ├─ Health verification
   └─ Escalation handling

3. Sentry Integration (Exercise 3)
   ├─ Event reporting
   ├─ Error tracking
   ├─ Deployment correlation
   └─ Production observability

Integration Points:
──────────────────
• DevMemory: Learn from past deployments
• HealthMonitor: Real-time metrics
• Infrastructure: Kubernetes operations
• Sentry: Error tracking and alerting
```

---

## Learning Outcomes

By completing these exercises, you will:

### Technical Skills
- Implement canary deployment patterns
- Build self-healing systems
- Work with async/await in Python
- Integrate external observability tools
- Handle complex error scenarios
- Design resilient CA/CD pipelines

### Conceptual Understanding
- Progressive rollout strategies
- Threshold-based validation
- State machine design
- Escalation patterns
- Memory-informed decision making
- Production observability

### Professional Practices
- Fail-fast principles
- Self-healing architecture
- Error budget management
- Deployment correlation
- Graceful degradation
- Human escalation patterns

---

## Going Further

### Extension Challenges

After completing all exercises, try:

1. **Blue-Green Deployment**
   - Implement alternative deployment strategy
   - Compare with canary approach
   - Handle database migrations

2. **Progressive Rollout**
   - Gradual traffic shifting: 10% → 25% → 50% → 100%
   - Validate at each stage
   - Roll back from any stage

3. **Deployment Dashboard**
   - Real-time deployment status
   - Metric visualization
   - Rollback history

4. **Multi-Service Deployments**
   - Deploy multiple services together
   - Handle inter-service dependencies
   - Coordinate rollbacks

5. **Advanced Sentry Integration**
   - Real Sentry API queries (not simulated)
   - Webhook receivers for alerts
   - Automated error analysis
   - Sentry Seer integration

---

## Feedback & Contribution

### Found an Issue?

If you encounter:
- Confusing instructions
- Incorrect information
- Missing dependencies
- Unclear diagrams

Please report it to your instructor or create an issue in the companion repository.

### Suggestions for Improvement

We welcome feedback on:
- Exercise clarity
- Hint effectiveness
- Difficulty progression
- Additional topics to cover

---

## Completion Checklist

Track your progress:

### Exercise 1: Canary Validation
- [ ] Read exercise description
- [ ] Reviewed architecture diagrams
- [ ] Implemented `validate_canary()`
- [ ] Added threshold adjustment (the guide's `_adjust_thresholds()` helper, or inline as in `complete/`)
- [ ] All tests passing
- [ ] Understand why it works

### Exercise 2: Automatic Rollback
- [ ] Read exercise description
- [ ] Reviewed state machine diagram
- [ ] Implemented `rollback()`
- [ ] Found the stable version (the guide's `_get_stable_version()` helper, or inline as in `complete/`)
- [ ] Implemented `_escalate_rollback_failure()`
- [ ] All tests passing
- [ ] Understand state transitions

### Exercise 3: Sentry Integration
- [ ] Set up Sentry account (or using placeholder)
- [ ] Configured DSN
- [ ] Implemented `SentryMonitor` class
- [ ] Integrated with deployer
- [ ] Events appearing in dashboard (if real DSN)
- [ ] All tests passing
- [ ] Understand bi-directional integration

### Overall
- [ ] Can explain the complete system
- [ ] Could teach concepts to peers
- [ ] Understand production implications
- [ ] Ready for CA/CD in practice

---

## Quick Links

- **Main Lab Directory**: `../`
- **Starter Code**: `../starter/`
- **Complete Reference**: `../complete/`
- **Tests**: `../starter/tests/`
- **Setup Verification**: `../verify_setup.py`

---

## Need Help?

### Documentation
- `VISUAL_OVERVIEW.md` - One-page system overview
- `QUICK_REFERENCE.md` - API and pattern reference
- `../starter/README.md` - Module-by-module API details

### In Each Exercise
- Progressive Hints sections
- Common Pitfalls sections
- Debugging Tips sections
- Success Criteria checklists

### Testing
```bash
# Exercise 1
pytest ../starter/tests/test_deployer.py -v -k canary

# Exercise 2
pytest ../starter/tests/test_deployer.py -v -k rollback

# Exercise 3 (no Sentry tests in the suite; this checks your DSN and SDK)
python ../integrations/test_sentry_connection.py

# All tests
pytest ../starter/tests/ -v
```

---

**Tip**: Make sure you understand each concept before you move on.

---

**Chapter**: 11 - Zero-Downtime Deployer
**Exercises**: 3 (2 required, 1 optional)
