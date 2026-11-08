# Exercise 2: Apprentice Pattern Capture

**File to edit**: `starter/capture.py`
**Tests**: `pytest starter/tests/test_capture.py -v`
**Reference**: Chapter 9, Section 9.6 (Phase 2)

## Goal

Implement `end_session()` and `_extract_heuristic()` in `ApprenticeCapture`.

## Steps

### _extract_heuristic(session)

1. Get first 3 actions: `first_checks = actions[:3]`
2. Collect search targets: `searches = [a.target for a in actions if a.type == "search"]`
3. Collect edit targets: `edits = [a.target for a in actions if a.type == "edit"]`
4. Derive the first check, guarding the empty case:
   `first_check = first_checks[0].target if first_checks else "unknown"`
5. Build the summary with the same guards. A session may record no search or
   no edit. For example, the exercise 4 verification sessions have no search
   action. Without fallbacks, `searches[0]` and `edits[-1]` raise
   `IndexError`:

   ```python
   summary = (
       f"Checked {first_check} first, "
       f"searched for {searches[0] if searches else 'nothing'}, "
       f"fixed in {edits[-1] if edits else 'unknown'}"
   )
   ```

6. Call `self._derive_pattern(first_checks, searches)` for the pattern
7. Return dict with summary, pattern, first_check, searches

### end_session(outcome)

1. Return `{}` if `self.current_session is None`
2. Set `self.current_session.outcome = outcome`
3. Save session, set `self.current_session = None`
4. Call `self._extract_heuristic(session)`
5. Store it as memory with `self.memory.remember()`:
   - Pass `infer=False`. Episodes must be stored verbatim, so identical
     sessions stay countable for Pattern Mining.
   - Pass metadata with `type="episode"`, `session_type`, `outcome`,
     `action_count`, and `first_check`.

   Exercise 4 groups on `session_type`, filters on `outcome`, and counts
   `first_check`. If any of those keys is missing, the miner finds nothing.
6. Return `{"episode": result, "heuristic": heuristic}`

## Verify

```bash
pytest starter/tests/test_capture.py -v
```
