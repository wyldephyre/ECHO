"""
Handoff Document Generator
Creates detailed session handoff documents for continuity across conversations
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class HandoffGenerator:
    """Generates handoff documents for session continuity"""
    
    def __init__(self, project_root: str):
        """
        Initialize handoff generator
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.handoffs_dir = self.project_root / "handoffs"
        self.handoffs_dir.mkdir(exist_ok=True)
    
    def generate_handoff(
        self,
        commander_profile: Dict,
        project_overview: Dict,
        session_accomplishments: List[str],
        current_state: Dict,
        next_steps: List[str],
        technical_reference: Dict,
        additional_notes: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Generate a handoff document
        
        Returns:
            Tuple of (filepath, markdown_content)
        """
        # Generate timestamp
        now = datetime.now()
        timestamp = now.strftime("%m-%d-%Y_%H%M")
        filename = f"handoff_{timestamp}.md"
        filepath = self.handoffs_dir / filename
        
        # Build markdown content
        content = self._build_markdown(
            commander_profile,
            project_overview,
            session_accomplishments,
            current_state,
            next_steps,
            technical_reference,
            additional_notes,
            timestamp
        )
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath), content
    
    def _build_markdown(
        self,
        commander_profile: Dict,
        project_overview: Dict,
        session_accomplishments: List[str],
        current_state: Dict,
        next_steps: List[str],
        technical_reference: Dict,
        additional_notes: Optional[str],
        timestamp: str
    ) -> str:
        """Build the markdown content"""
        
        md = f"""# Echo Bot - Session Handoff Document
**Generated:** {timestamp}

---

## 1. Commander Profile

**Callsign:** {commander_profile.get('callsign', 'Fyrebug/Corporal')}

**Key Context:**
- 100% disabled Marine Corps veteran
- ADHD, Bipolar 2, PTSD, TBI
- Communication style: Direct, no-bullshit Marine communication
- Voice-first interface preferred
- When unclear: **ASK for clarification - never assume**

**Working Style:**
{commander_profile.get('working_style', 'Prefers direct communication, no assumptions, ask when unclear')}

---

## 2. Project Overview

**Project Name:** {project_overview.get('name', 'Echo Bot')}

**Purpose:** {project_overview.get('purpose', 'Discord-based multi-AI worldbuilding bot for Nexus Arcanum')}

**Technical Stack:**
{self._format_list(project_overview.get('tech_stack', []))}

**Current Phase:** {project_overview.get('phase', 'Phase 1 - Foundation')}

**What's Built:**
{self._format_list(project_overview.get('built', []))}

**File Structure:**
{self._format_file_structure(project_overview.get('file_structure', []))}

---

## 3. Session Accomplishments

{self._format_list(session_accomplishments, numbered=True)}

**Key Decisions Made:**
{self._format_list(project_overview.get('decisions', []), numbered=True) if project_overview.get('decisions') else 'None documented'}

**Problems Solved:**
{self._format_list(project_overview.get('problems_solved', []), numbered=True) if project_overview.get('problems_solved') else 'None documented'}

---

## 4. Current State

**What's Working:**
{self._format_list(current_state.get('working', []), numbered=True)}

**What's Not Working:**
{self._format_list(current_state.get('not_working', []), numbered=True) if current_state.get('not_working') else 'All systems operational'}

**Pending Issues/Blockers:**
{self._format_list(current_state.get('blockers', []), numbered=True) if current_state.get('blockers') else 'None'}

---

## 5. Next Steps

**Immediate Priorities:**
{self._format_list(next_steps, numbered=True)}

**Future Phases:**
{self._format_list(project_overview.get('future_phases', []), numbered=True) if project_overview.get('future_phases') else 'Not specified'}

**Open Questions:**
{self._format_list(current_state.get('open_questions', []), numbered=True) if current_state.get('open_questions') else 'None'}

---

## 6. Technical Quick Reference

**API Keys Configured:**
{self._format_list(technical_reference.get('api_keys', []), numbered=True)}

**Key Commands:**
{self._format_list(technical_reference.get('commands', []), numbered=True)}

**Important File Paths:**
{self._format_list(technical_reference.get('file_paths', []), numbered=True)}

**Environment Variables:**
{self._format_list(technical_reference.get('env_vars', []), numbered=True)}

---

## 7. Additional Notes

{additional_notes if additional_notes else 'None'}

---

**End of Handoff Document**

*For the forgotten 99%, we rise.* 🔥
"""
        return md
    
    def _format_list(self, items: List[str], numbered: bool = False) -> str:
        """Format a list of items"""
        if not items:
            return "None"
        
        if numbered:
            return "\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])
        else:
            return "\n".join([f"- {item}" for item in items])
    
    def _format_file_structure(self, structure: List[str]) -> str:
        """Format file structure"""
        if not structure:
            return "Not documented"
        return "\n".join([f"  - {item}" for item in structure])
    
    def generate_specialist_handoff(
        self,
        task_name: str,
        assigned_droid: str,
        files_can_modify: List[str],
        files_cannot_modify: List[str],
        dependencies: List[str],
        task_description: Dict,
        integration_points: List[str],
        testing_requirements: List[str],
        reference_documents: Optional[List[str]] = None,
        code_patterns: Optional[List[str]] = None
    ) -> tuple[str, str]:
        """
        Generate a specialist handoff document using the template
        
        Args:
            task_name: Name of the task
            assigned_droid: Which specialist droid is assigned
            files_can_modify: List of files/methods this droid can modify
            files_cannot_modify: List of files that are off-limits
            dependencies: List of dependencies or blockers
            task_description: Dict with 'current_state', 'target_implementation', 'technical_details', 'example_usage'
            integration_points: List of how this work connects to the system
            testing_requirements: List of testing steps required
            reference_documents: Optional list of reference document paths
            code_patterns: Optional list of code patterns to follow
        
        Returns:
            Tuple of (filepath, markdown_content)
        """
        # Generate timestamp
        now = datetime.now()
        timestamp = now.strftime("%m-%d-%Y_%H%M")
        filename = f"handoff_{task_name.lower().replace(' ', '_')}_{timestamp}.md"
        filepath = self.handoffs_dir / filename
        
        # Build markdown content from template
        content = self._build_specialist_markdown(
            task_name=task_name,
            assigned_droid=assigned_droid,
            files_can_modify=files_can_modify,
            files_cannot_modify=files_cannot_modify,
            dependencies=dependencies,
            task_description=task_description,
            integration_points=integration_points,
            testing_requirements=testing_requirements,
            reference_documents=reference_documents or [],
            code_patterns=code_patterns or [],
            timestamp=timestamp
        )
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath), content
    
    def _build_specialist_markdown(
        self,
        task_name: str,
        assigned_droid: str,
        files_can_modify: List[str],
        files_cannot_modify: List[str],
        dependencies: List[str],
        task_description: Dict,
        integration_points: List[str],
        testing_requirements: List[str],
        reference_documents: List[str],
        code_patterns: List[str],
        timestamp: str
    ) -> str:
        """Build the specialist handoff markdown content"""
        
        # Format lists
        files_can_str = self._format_list(files_can_modify) if files_can_modify else "None specified"
        files_cannot_str = self._format_list(files_cannot_modify) if files_cannot_modify else "None"
        deps_str = self._format_list(dependencies) if dependencies else "None - can start immediately"
        integration_str = self._format_list(integration_points) if integration_points else "Not specified"
        testing_str = self._format_list(testing_requirements, numbered=True) if testing_requirements else "Not specified"
        refs_str = self._format_list(reference_documents) if reference_documents else "See `agent.md` for master context"
        patterns_str = self._format_list(code_patterns) if code_patterns else "Follow existing code patterns in similar files"
        
        md = f"""# Specialist Task Handoff - {task_name}
**Generated:** {timestamp}
**Assigned To:** {assigned_droid}
**Status:** Active

---

## ⚠️ CRITICAL SAFETY GUARDS

### Files You CAN Modify:
{files_can_str}

### Files You CANNOT Modify:
{files_cannot_str}

### Dependencies:
{deps_str}

### Testing Requirements:
{testing_str}

### Integration Points:
{integration_str}

### If Unsure:
**STOP and ask** - Don't assume, especially about:
- File structure changes
- Breaking changes to existing APIs
- Database/session state modifications
- Changes that affect multiple files

---

## TASK SPECIFIC CONTEXT

### Current State:
{task_description.get('current_state', 'Not specified')}

### Target Implementation:
{task_description.get('target_implementation', 'Not specified')}

### Technical Details:
{task_description.get('technical_details', 'Not specified')}

### Example Usage:
{task_description.get('example_usage', 'Not specified')}

---

## REFERENCE DOCUMENTS

- **Master Context:** See `agent.md` for project standards, coding conventions, and world lore
{refs_str}

---

## CODE PATTERNS TO FOLLOW

### Existing Patterns:
{patterns_str}

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
None yet

### Notes:
[Any additional notes, discoveries, or important information]

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
"""
        return md
    
    def generate_restart_handoff(
        self,
        original_handoff_path: str,
        progress_update: Dict,
        conversation_summary: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Generate a restart handoff from an existing handoff + progress update
        
        Args:
            original_handoff_path: Path to the original handoff file
            progress_update: Dict with keys:
                - work_completed: List[str]
                - work_in_progress: List[str]
                - blockers: List[str]
                - discoveries: List[str]
                - files_modified: List[str] (with notes)
                - next_steps: List[str]
                - context_summary: str
            conversation_summary: Optional summary of the conversation
        
        Returns:
            Tuple of (filepath, markdown_content)
        """
        # Read original handoff
        original_path = Path(original_handoff_path)
        if not original_path.exists():
            raise FileNotFoundError(f"Original handoff not found: {original_handoff_path}")
        
        original_content = original_path.read_text(encoding='utf-8')
        
        # Extract metadata from original
        task_match = re.search(r'# Specialist Task Handoff - (.+)', original_content)
        task_name = task_match.group(1).strip() if task_match else "Unknown Task"
        
        droid_match = re.search(r'\*\*Assigned To:\*\* (.+)', original_content)
        assigned_droid = droid_match.group(1).strip() if droid_match else "Unknown"
        
        # Generate new timestamp
        now = datetime.now()
        timestamp = now.strftime("%m-%d-%Y_%H%M")
        filename = f"handoff_{task_name.lower().replace(' ', '_').replace('(', '').replace(')', '')}_restart_{timestamp}.md"
        filepath = self.handoffs_dir / filename
        
        # Build restart handoff content
        content = self._build_restart_markdown(
            original_content=original_content,
            task_name=task_name,
            assigned_droid=assigned_droid,
            progress_update=progress_update,
            conversation_summary=conversation_summary,
            timestamp=timestamp,
            original_filename=original_path.name
        )
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath), content
    
    def _build_restart_markdown(
        self,
        original_content: str,
        task_name: str,
        assigned_droid: str,
        progress_update: Dict,
        conversation_summary: Optional[str],
        timestamp: str,
        original_filename: str
    ) -> str:
        """Build the restart handoff markdown content"""
        
        # Extract key sections from original
        safety_guards_match = re.search(
            r'## ⚠️ CRITICAL SAFETY GUARDS.*?(?=## TASK SPECIFIC CONTEXT)',
            original_content,
            re.DOTALL
        )
        safety_guards = safety_guards_match.group(0) if safety_guards_match else "## ⚠️ CRITICAL SAFETY GUARDS\n\n[See original handoff]"
        
        task_context_match = re.search(
            r'## TASK SPECIFIC CONTEXT.*?(?=## REFERENCE DOCUMENTS)',
            original_content,
            re.DOTALL
        )
        task_context = task_context_match.group(0) if task_context_match else "## TASK SPECIFIC CONTEXT\n\n[See original handoff]"
        
        ref_docs_match = re.search(
            r'## REFERENCE DOCUMENTS.*?(?=## CODE PATTERNS)',
            original_content,
            re.DOTALL
        )
        ref_docs = ref_docs_match.group(0) if ref_docs_match else "## REFERENCE DOCUMENTS\n\n[See original handoff]"
        
        code_patterns_match = re.search(
            r'## CODE PATTERNS TO FOLLOW.*?(?=## SAFETY CHECKLIST)',
            original_content,
            re.DOTALL
        )
        code_patterns = code_patterns_match.group(0) if code_patterns_match else "## CODE PATTERNS TO FOLLOW\n\n[See original handoff]"
        
        # Format progress update
        work_completed = self._format_list(progress_update.get('work_completed', []), numbered=True)
        work_in_progress = self._format_list(progress_update.get('work_in_progress', []), numbered=True)
        blockers = self._format_list(progress_update.get('blockers', []), numbered=True)
        discoveries = self._format_list(progress_update.get('discoveries', []), numbered=True)
        files_modified = self._format_list(progress_update.get('files_modified', []), numbered=True)
        next_steps = self._format_list(progress_update.get('next_steps', []), numbered=True)
        context_summary = progress_update.get('context_summary', 'Not provided')
        
        md = f"""# Specialist Task Handoff - {task_name} (RESTART)
**Generated:** {timestamp}
**Assigned To:** {assigned_droid}
**Status:** Active (Restart)
**Original Handoff:** {original_filename}

---

## 🔄 RESTART CONTEXT

This is a restart handoff. The original handoff was created earlier, and this document includes progress updates.

**Original Handoff:** See `{original_filename}` for full original context.

**Conversation Summary:**
{conversation_summary if conversation_summary else "Not provided"}

---

## PROGRESS UPDATE

### Work Completed Since Last Handoff:
{work_completed if work_completed else "None documented"}

### Work In Progress:
{work_in_progress if work_in_progress else "None"}

### Current Blockers:
{blockers if blockers else "None"}

### Important Discoveries:
{discoveries if discoveries else "None"}

### Files Modified:
{files_modified if files_modified else "None"}

### Next Immediate Steps:
{next_steps if next_steps else "Continue from where we left off"}

### Context Summary:
{context_summary}

---

{safety_guards}

---

{task_context}

---

{ref_docs}

---

{code_patterns}

---

## SAFETY CHECKLIST

Before making changes:
- [ ] Review this restart handoff and the original handoff
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

---

## PROGRESS TRACKING

### Completed:
- [ ] Task analysis complete
- [ ] Implementation started
- [ ] Core functionality working
- [ ] Testing complete
- [ ] Integration verified

### Blockers:
{blockers if blockers else "None"}

### Notes:
[Any additional notes, discoveries, or important information]

---

## NEXT STEPS FOR SPECIALIST

1. Review this restart handoff and the original handoff ({original_filename})
2. Review all reference documents
3. Understand the progress made so far
4. Continue implementation from where we left off
5. Update this handoff with new progress
6. Mark as complete when done

---

**End of Restart Handoff**

*For the forgotten 99%, we rise.* 🔥
"""
        return md

