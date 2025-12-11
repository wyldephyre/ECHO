# Specialist Task Handoff - [TASK_NAME]
**Generated:** [TIMESTAMP]
**Assigned To:** [SPECIALIST_DROID]
**Status:** Active | In Progress | Blocked | Complete

---

## ⚠️ CRITICAL SAFETY GUARDS

### Files You CAN Modify:
[List specific files and methods this droid can touch]
- Example: `ai_coordinator.py` (only `generate_image()` method, lines 340-388)
- Example: `config.py` (only add new config variables, don't modify existing)

### Files You CANNOT Modify:
[List files that are off-limits]
- Example: `main.py` (other droid working on this)
- Example: `game_master/gm_engine.py` (core logic, don't touch)

### Dependencies:
[What other work must complete first, or what this work depends on]
- Example: "Wait for primary droid to finish testing before implementing"
- Example: "None - can start immediately"

### Testing Requirements:
[How to verify your work doesn't break things]
- Example: "Run `/nexus-test-list` and verify all tests still pass"
- Example: "Test manually in Discord: `/nexus-start` → `/nexus-action`"
- Example: "Run: `python -m py_compile [your_file].py` to check syntax"

### Integration Points:
[How your work connects to the rest of the system]
- Example: "Your `generate_image()` will be called from `gm_commands.py` line 159"
- Example: "This feature integrates with existing `session_manager` in `game_master/session_state.py`"

### If Unsure:
**STOP and ask** - Don't assume, especially about:
- File structure changes
- Breaking changes to existing APIs
- Database/session state modifications
- Changes that affect multiple files

---

## TASK SPECIFIC CONTEXT

### Current State:
[What exists now, what's working, what's not]

### Target Implementation:
[What needs to be built, expected behavior, success criteria]

### Technical Details:
[Specific implementation notes, API requirements, code patterns to follow]

### Example Usage:
[How the feature will be used once complete]

---

## REFERENCE DOCUMENTS

- **Master Context:** See `agent.md` for project standards, coding conventions, and world lore
- **Feature Documentation:** [Link to relevant feature docs, e.g., `docs/AI_Game_Master_Feature_Doc.md`]
- **Related Handoffs:** [Link to other active handoffs if dependencies exist]
- **Code Examples:** [Link to similar implementations in codebase]

---

## CODE PATTERNS TO FOLLOW

### Existing Patterns:
[Reference specific code examples from the codebase]
- Example: "Follow the pattern in `ai_coordinator.ask_mistral()` for async AI calls"
- Example: "Use the same error handling pattern as `gm_engine.process_player_action()`"

### Coding Standards:
- Type hints required: `async def method(self, param: str) -> Optional[str]:`
- Docstrings required: Every function needs a docstring explaining purpose, args, returns
- Logging: Use `logger.info()`, `logger.error()` - never `print()`
- Error handling: Try/except with meaningful error messages
- Async/await: All Discord and AI operations must be async

### File Organization:
- New features in separate files/cogs when appropriate
- Keep `main.py` minimal - delegate to modules
- Follow existing directory structure

---

## SAFETY CHECKLIST

Before making changes:
- [ ] Read `agent.md` for coding standards and world context
- [ ] Review existing code patterns in similar files
- [ ] Check if any other handoffs mention this file (use `handoff_manager.py check`)
- [ ] Understand the integration points
- [ ] Verify dependencies are met

Before committing:
- [ ] Run existing tests: `/nexus-test-list` → `/nexus-test-run` (if applicable)
- [ ] Test manually in Discord if applicable
- [ ] Verify no syntax errors: `python -m py_compile [your_file].py`
- [ ] Check logs for errors: Review `echo_bot.log`
- [ ] Verify integration points still work

If you encounter issues:
- [ ] Document the problem in this handoff
- [ ] Check if it's a dependency issue
- [ ] Ask for clarification rather than guessing

---

## PROGRESS TRACKING

### Completed:
- [ ] Task analysis complete
- [ ] Implementation started
- [ ] Core functionality working
- [ ] Testing complete
- [ ] Integration verified

### Blockers:
[List any blockers or issues encountered]

### Notes:
[Any additional notes, discoveries, or important information]

---

## PROGRESS UPDATE (For Restart Conversations)

### Work Completed Since Last Handoff:
[List what was accomplished in this session]

### Work In Progress:
[What's partially complete or currently being worked on]

### Current Blockers:
[What's stopping progress, if anything]

### Important Discoveries:
[Things learned that affect the task or implementation approach]

### Files Modified:
[List files changed with brief notes about what changed]

### Next Immediate Steps:
1. [First priority action]
2. [Second priority action]
3. [Third priority action]

### Context Summary:
[Brief summary of where we are in the task - 2-3 sentences]

---

## NEXT STEPS FOR SPECIALIST

1. Review this handoff and all reference documents
2. Understand the safety guards and file boundaries
3. Review existing code patterns
4. Implement the feature following coding standards
5. Test thoroughly
6. Update this handoff with progress
7. Mark as complete when done

---

**End of Specialist Handoff**

*For the forgotten 99%, we rise.* 🔥

