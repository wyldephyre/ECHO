# Specialist Handoff Template Usage Guide

## Overview

The specialist handoff template is designed for delegating specific, isolated tasks to specialist AI agents (droids) while maintaining safety guards to prevent code conflicts and ensure quality.

## When to Use Specialist Handoffs

Use specialist handoffs when:
- A task is well-defined and isolated
- The task has clear file boundaries (can/cannot modify lists)
- The task can be worked on independently
- You want to parallelize work across multiple agents

Use general handoffs when:
- The work is exploratory or requires full project context
- Multiple systems need to be coordinated
- Architecture decisions need to be made
- The task boundaries are unclear

## Template Structure

### Critical Safety Guards Section
The most important section - defines what the specialist can and cannot touch:
- **Files You CAN Modify**: Explicit list of files/methods
- **Files You CANNOT Modify**: Off-limits files
- **Dependencies**: What must complete first
- **Testing Requirements**: How to verify work doesn't break things
- **Integration Points**: How the work connects to the system

### Task Specific Context
Provides the specialist with:
- Current state of the feature
- Target implementation goals
- Technical details and requirements
- Example usage

### Reference Documents
Links to:
- Master `agent.md` for standards
- Feature documentation
- Related handoffs
- Code examples

## Creating a Specialist Handoff

### Method 1: Using the Generator (Recommended)

```python
from handoff_generator import HandoffGenerator
from pathlib import Path

generator = HandoffGenerator(str(Path.cwd()))

filepath, content = generator.generate_specialist_handoff(
    task_name="Image Generation Implementation",
    assigned_droid="Image Generation Specialist",
    files_can_modify=[
        "ai_coordinator.py (only generate_image() method, lines 340-388)"
    ],
    files_cannot_modify=[
        "game_master/gm_commands.py",
        "game_master/gm_engine.py",
        "main.py"
    ],
    dependencies=[],
    task_description={
        "current_state": "generate_image() exists but returns None",
        "target_implementation": "Implement Gemini Imagen API integration",
        "technical_details": "Need to call Gemini Imagen API, return image URL/data",
        "example_usage": "Called from scene_images.py when key moment detected"
    },
    integration_points=[
        "scene_images.py line 59 calls ai_coordinator.generate_image()"
    ],
    testing_requirements=[
        "Run /nexus-test-list and verify all tests still pass",
        "Test image generation triggers at key moments in Discord"
    ],
    reference_documents=[
        "docs/AI_Game_Master_Feature_Doc.md",
        "agent.md"
    ],
    code_patterns=[
        "Follow async pattern in ai_coordinator.ask_mistral()",
        "Use same error handling as other AI methods"
    ]
)
```

### Method 2: Manual Creation

1. Copy `handoffs/templates/specialist_handoff_template.md`
2. Fill in all sections with task-specific information
3. Save to `handoffs/handoff_[task_name]_[timestamp].md`

## Best Practices

### 1. Be Specific About File Boundaries
**Good:**
```
Files You CAN Modify:
- ai_coordinator.py (only generate_image() method, lines 340-388)
```

**Bad:**
```
Files You CAN Modify:
- ai_coordinator.py
```

### 2. List All Dependencies
Even if there are none, state it explicitly:
```
Dependencies:
None - can start immediately
```

### 3. Provide Clear Testing Requirements
Give specific commands or steps:
```
Testing Requirements:
1. Run: python -m py_compile ai_coordinator.py
2. Test in Discord: /nexus-start → trigger key moment
3. Verify image appears in response
```

### 4. Document Integration Points
Show exactly where the work connects:
```
Integration Points:
- scene_images.py line 59: await ai_coordinator.generate_image(...)
- gm_commands.py line 159: image_data = await image_generator.generate_scene_image(...)
```

### 5. Reference Existing Patterns
Point to similar code:
```
Code Patterns:
- Follow async pattern in ai_coordinator.ask_mistral() (lines 59-117)
- Use same error handling as ask_claude() (lines 122-177)
```

## Starting a Specialist Conversation

When starting a new conversation with a specialist droid:

1. **Attach the specialist handoff document**
2. **Attach `agent.md`** for master context
3. **Attach relevant code files** (the ones they can modify)
4. **Start with:** "Review the handoff document and continue where we left off"

Example:
```
I'm delegating the Image Generation task to you. Please:
1. Review handoff_image_gen_12-11-2025.md
2. Review agent.md for coding standards
3. Review ai_coordinator.py (focus on generate_image method)
4. Implement Gemini Imagen API integration
```

## Updating Progress

As the specialist works, they should update the handoff:
- Mark completed items in the Progress Tracking section
- Add blockers if encountered
- Add notes about discoveries or issues

## Marking Complete

When the task is done:
1. Update status to "Complete" in the handoff
2. Run `handoff_manager.py complete <handoff_name>` to archive
3. Verify all tests pass
4. Document any follow-up work needed

## Conflict Prevention

Before creating a new specialist handoff:
1. Run `handoff_manager.py check` to see active handoffs
2. Verify no file conflicts with existing active handoffs
3. If conflicts exist, either:
   - Wait for the conflicting handoff to complete
   - Adjust file boundaries
   - Coordinate with the other specialist

## Example Workflow

1. **Identify task**: "Implement image generation"
2. **Analyze boundaries**: What files can be modified? What's off-limits?
3. **Create handoff**: Use generator or template
4. **Start specialist conversation**: Attach handoff + agent.md + relevant files
5. **Specialist works**: Updates handoff with progress
6. **Verify completion**: Test, check integration, mark complete
7. **Archive**: Move to completed handoffs

## Troubleshooting

### Specialist modifies off-limits file
- Review the handoff - was the boundary clear?
- Check if the file was in the "cannot modify" list
- If unclear, update the handoff with more specific boundaries

### Conflicts detected
- Use `handoff_manager.py check` to see conflicts
- Coordinate with other specialists
- Adjust file boundaries if needed

### Task too complex
- Break into smaller specialist handoffs
- Or use a general handoff for coordination

## Creating Restart Handoffs

When a conversation is getting close to context limits, create a restart handoff to continue in a fresh conversation.

### Quick Method: Using the Auto-Generator

```bash
# From conversation summary text
python generate_restart_handoff.py handoffs/handoff_[task].md --summary "Work completed: X, Y, Z. Next steps: A, B"

# From summary file
python generate_restart_handoff.py handoffs/handoff_[task].md --summary-file conversation_summary.txt

# Interactive mode (prompts for all fields)
python generate_restart_handoff.py handoffs/handoff_[task].md --interactive

# From JSON file (structured data)
python generate_restart_handoff.py handoffs/handoff_[task].md --json progress.json
```

### Manual Method: Using the Generator Programmatically

```python
from handoff_generator import HandoffGenerator
from pathlib import Path

generator = HandoffGenerator(str(Path.cwd()))

filepath, content = generator.generate_restart_handoff(
    original_handoff_path="handoffs/handoff_image_gen_12-11-2025.md",
    progress_update={
        "work_completed": ["Researched API", "Created initial structure"],
        "work_in_progress": ["Implementing core method"],
        "blockers": [],
        "discoveries": ["API requires different endpoint"],
        "files_modified": ["ai_coordinator.py - added imports"],
        "next_steps": ["Complete implementation", "Test in Discord"],
        "context_summary": "About 50% complete. API research done."
    },
    conversation_summary="Worked on image generation. Found API details..."
)
```

### Restart Workflow

1. **Before context limit** (at ~70-80%): Ask AI to create conversation summary
2. **Generate restart handoff**: Use `generate_restart_handoff.py`
3. **Start new conversation**: Attach restart handoff + `agent.md` + relevant files
4. **Continue work**: Specialist reviews handoff and continues

## Related Documents

- `agent.md` - Master project context and standards
- `handoff_generator.py` - Code for generating handoffs
- `handoff_manager.py` - Tool for managing multiple handoffs
- `generate_restart_handoff.py` - Auto-generate restart handoffs from summaries
- `handoffs/templates/specialist_handoff_template.md` - The template itself

---

*For the forgotten 99%, we rise.* 🔥

