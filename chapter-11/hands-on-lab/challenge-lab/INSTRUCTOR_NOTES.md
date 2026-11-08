# Instructor Notes: Multi-Service Deployment Challenge Lab

## Overview

This challenge lab applies the canary deployment and rollback work from Exercises 1-2 to a multi-service deployment.

The concepts behind the lab: Chapter 11, Sections 11.6 and 11.7.

## Challenge Design

### Learning Objectives Alignment

**Primary Objectives** (from Exercises 1-2):
- Canary deployment with health validation
- Automatic rollback on failure detection
- Memory-informed decision making
- Zero-downtime deployment patterns

**Extended Objectives** (Challenge Lab):
- Dependency management in deployments
- Graph algorithms in practice (topological sort)
- Multi-service state tracking
- Coordinated rollback across services
- Transaction semantics (all-or-nothing)

### Lab Sequence

**Scaffolded Learning**:
1. Exercise 1: Single service canary deployment
2. Exercise 2: Single service automatic rollback
3. Challenge: Multi-service with coordination

**Progressive Difficulty**:
- Exercises: Guided implementation with TODOs
- Challenge: Open-ended problem requiring design decisions


## Document Structure

### 7 Supporting Documents

1. **README.md** - Challenge overview and motivation
2. **GETTING_STARTED.md** - Step-by-step workflow guide
3. **PROBLEM.md** - Detailed technical specifications
4. **HINTS.md** - Progressive hints (3 difficulty levels)
5. **APPROACH.md** - High-level solution strategy
6. **test_scenarios.md** - Test cases and verification
7. **.challenge-index.md** - Navigation guide

### How the Documents Fit Together

- What to build: README
- How to approach it: GETTING_STARTED, APPROACH
- Implementation details: HINTS, PROBLEM
- Testing: test_scenarios.md

Students see the overview first. Hints are available but optional. No solution is provided.

## Expected Student Journey

### Timeline (2-3 hours)

**Phase 1: Understanding (30 min)**
- Read README.md and PROBLEM.md
- Sketch dependency graph on paper
- Identify key components

**Phase 2: Design (30 min)**
- Plan data structures
- Choose algorithm (topological sort)
- Design state machine

**Phase 3: Implementation (60-90 min)**
- Build dependency graph
- Implement topological sort
- Add sequential deployment
- Integrate rollback coordination

**Phase 4: Testing (30 min)**
- Verify with test scenarios
- Debug issues
- Refine implementation

### Common Student Paths

**Fast Track** (2 hours):
- Experienced developers
- Skip GETTING_STARTED.md
- Go straight to PROBLEM.md
- Use hints minimally

**Standard Track** (3 hours):
- Most students
- Follow GETTING_STARTED.md
- Use Hint 1-2 when stuck
- Test thoroughly

**Supported Track** (3-4 hours):
- Students needing more guidance
- Read all documents
- Use all 3 hint levels
- Extensive testing and debugging

## Key Concepts to Assess

### Graph Algorithms
- Can student implement topological sort?
- Do they detect circular dependencies?
- Can they validate missing dependencies?

### State Management
- Does student track state explicitly?
- Are state transitions clear?
- Is state used to drive decisions?

### Coordination Logic
- Does deployment happen sequentially?
- Is rollback in correct (reverse) order?
- Are failures handled gracefully?

### Code Reuse
- Does student reuse Exercise 1-2 code?
- Is coordination separated from execution?
- Is the coordinator pattern applied?

## Common Student Mistakes

### Mistake 1: Reimplementing Deployment
**Symptom**: Student rewrites canary deployment logic
**Solution**: Point to Exercise 1 code, emphasize reuse

### Mistake 2: Wrong Rollback Order
**Symptom**: Rolling back in deployment order
**Solution**: Explain dependency consistency, point to HINTS.md

### Mistake 3: No State Tracking
**Symptom**: Confusion about what's deployed
**Solution**: Suggest explicit state object, refer to Hint 2

### Mistake 4: Ignoring Edge Cases
**Symptom**: Code breaks on circular dependencies
**Solution**: Point to test_scenarios.md, emphasize validation

### Mistake 5: Analysis Paralysis
**Symptom**: Stuck in design phase for hours
**Solution**: Encourage incremental implementation, use Hint 1

## Hint Usage Guidelines

### When Students Should Use Hints

**Hint 1 (Conceptual)**:
- After 30+ minutes stuck on approach
- Need problem decomposition help
- Unclear on overall strategy

**Hint 2 (Architectural)**:
- Have approach but stuck on design
- Need algorithm explanation
- Want design pattern guidance

**Hint 3 (Implementation)**:
- Design is clear but coding is hard
- Need code structure examples
- Want to verify approach

### When to Discourage Hint Usage

- First 30 minutes of challenge
- Before attempting to solve independently
- Before sketching approach on paper

### Hint Order

Ask students to open the hints in order: 1, 2, then 3. They should not jump
straight to Hint 3. If they are stuck, they should open the next hint.

## Assessment Criteria

### Correctness (40%)
- All test scenarios pass
- Deployment order is correct
- Rollback happens in reverse order
- Edge cases handled properly

### Code Quality (30%)
- Clean, readable code
- Proper abstractions
- Reuses existing code
- Good error handling

### Design (20%)
- Appropriate data structures
- Clear state management
- Separation of concerns
- Algorithm choice justified

### Testing (10%)
- Test coverage across all eleven scenarios
- Edge cases tested
- Test quality

## Extension Opportunities

### For Advanced Students

**Bonus Challenges** (mentioned in README.md):
1. Parallel deployment of independent services
2. Partial rollback (only affected services)
3. Health check retries before failure
4. Deployment visualization
5. Progressive traffic rollout

**Real-World Extensions**:
- Deploy to actual Kubernetes cluster
- Add Prometheus metrics
- Integrate with Sentry for errors
- Build CLI interface
- Create deployment dashboard

### For Struggling Students

**Simplified Version**:
- Reduce to 2 services instead of 3
- Provide graph construction code
- Focus only on happy path first
- Skip edge case handling initially

**Additional Support**:
- Pair programming sessions
- Office hours walkthrough
- Walk through the single-service solution in `../complete/deployer.py` together,
  since the challenge reuses it
- Step-by-step debugging guide

## Connection to Book Chapters

### Chapter 9: Agent Memory and Context Models
- Memory integration in deployment decisions
- Recording coordination events
- Learning from past failures

### Chapter 10: Orchestrating Multiple AI Agents
- Coordination patterns
- Distributed decision making
- Service orchestration

### Chapter 11: Integrating Agentic Coding with DevOps and Cloud Infrastructure
- Canary deployment (Exercise 1, Section 11.6)
- Automatic rollback (Exercise 2, Section 11.6)
- Multi-service coordination (this challenge, Section 11.7)

### Chapter 12: Security, Privacy, and Ethical Considerations
- Deployment approval gates
- Audit trails
- Policy enforcement

## Tips for Running the Lab

### Pre-Lab Preparation
- Verify all students completed Exercises 1-2
- Check environment setup working
- Review graph algorithm basics
- Prepare debugging strategies

### During Lab Session
- **First 15 minutes**: Quick review of graph algorithms
- **30 minutes in**: Check student progress on design
- **90 minutes in**: Offer hint guidance to stuck students
- **Final 30 minutes**: Testing and debugging support

### Post-Lab Debrief
- Discuss different solution approaches
- Review common mistakes and fixes
- Connect patterns to real-world systems
- Preview next chapter applications

## FAQ: Instructor Edition

### Q: Is there a reference implementation for this challenge?
**A**: No. The design decisions are the exercise. Students build on the single-service deployer in `../complete/`. If you write your own multi-service solution for the session, hold it back until students finish. Present it as one design among several. Do not present it as the answer.

### Q: How much help should I give?
**A**: Point to the relevant hints. Do not give solutions. Ask guiding questions. Let students work through the problem.

### Q: What if students can't implement topological sort?
**A**: Point them to Hint 2 for the algorithm. A quick whiteboard explanation can help.

### Q: Should students work alone or in pairs?
**A**: Pairs work well for this challenge. Solo is also fine. Avoid groups >2.

### Q: How do I evaluate incomplete solutions?
**A**: Assess design quality, code structure, and what they did complete. Partial credit for good design even if incomplete.

### Q: Student says "this is too hard"?
**A**: Acknowledge it. Break the work into smaller steps. Point to the GETTING_STARTED.md workflow. Consider the simplified version.

## Success Metrics

### Student Success Indicators
- Can explain topological sort
- Understands coordinator pattern
- Recognizes when to reuse vs. rewrite
- Thinks about state management
- Tests edge cases proactively

### Lab Success Indicators
- Most students complete the core challenge
- Students report increased confidence
- Pattern recognition transfers to other problems
- Students connect concepts to real systems

## Troubleshooting Guide

### Issue: "Tests keep failing"
**Debug Steps**:
1. Check deployment order calculation
2. Verify rollback order is reversed
3. Confirm state tracking updates
4. Test graph algorithm separately

### Issue: "I don't understand the problem"
**Solution**:
1. Draw dependency graph together
2. Walk through one example manually
3. Reference PROBLEM.md specifications
4. Relate to real-world deployment

### Issue: "My code is getting messy"
**Solution**:
1. Suggest refactoring to methods
2. Point to coordinator pattern
3. Show clear separation of concerns
4. Reference clean code practices

### Issue: "How do I test this?"
**Solution**:
1. Point to test_scenarios.md
2. Suggest starting with Scenario 1 (happy path)
3. Add print statements for debugging
4. Test each component separately

## Time Management Advice

### If Running Over Time
1. Focus on happy path first (Scenario 1)
2. Skip bonus challenges
3. Defer edge cases to homework
4. Provide code snippets for struggling parts

### If Students Finish Early
1. Suggest bonus challenges
2. Code review and refactoring
3. Performance optimization
4. Documentation improvements

## Learning Outcomes Verification

### Knowledge Check Questions
1. "Explain why rollback must be in reverse order"
2. "How does topological sort work?"
3. "Why coordinate rollback instead of individual rollback?"
4. "What makes this a 'transaction' pattern?"

### Practical Demonstration
1. Deploy 3 services successfully
2. Show rollback when middle service fails
3. Detect circular dependency
4. Handle missing dependency

## Related Materials

### Prerequisites to Review
- Graph data structures
- Topological sort algorithm
- State machines
- Async/await patterns

### Follow-Up Topics
- Kubernetes operators
- CI/CD pipeline design
- Infrastructure-as-Code
- Service mesh patterns

## Final Notes

This lab is harder than Exercises 1-2. The hints and the supporting documents give students support when they need it.

**Message to students**: "This challenge applies Exercises 1-2 to several services. It is harder, but you have the tools you need. Open the hints in order when you are stuck. Your code does not need to be perfect."

---

**Questions?** Review the .challenge-index.md for document navigation, or reference specific sections above for common issues.
