"""
Dev Log Generator
Auto-generates developer logs from git history and changes
"""

import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class DevLogGenerator:
    """Generates developer logs from git history"""
    
    def __init__(self, project_root: str = "."):
        """
        Initialize dev log generator
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.devlogs_dir = self.project_root / "devlogs"
        self.devlogs_dir.mkdir(exist_ok=True)
    
    def get_git_status(self) -> Dict:
        """
        Get current git status
        
        Returns:
            Dict with status information
        """
        try:
            # Check if git repo exists
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode != 0:
                return {"is_repo": False, "error": "Not a git repository"}
            
            # Parse status
            status_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            modified = []
            added = []
            deleted = []
            untracked = []
            
            for line in status_lines:
                if not line:
                    continue
                status = line[:2]
                filename = line[3:]
                
                if status[0] == 'M' or status[1] == 'M':
                    modified.append(filename)
                elif status[0] == 'A' or status[1] == 'A':
                    added.append(filename)
                elif status[0] == 'D' or status[1] == 'D':
                    deleted.append(filename)
                elif status == '??':
                    untracked.append(filename)
            
            return {
                "is_repo": True,
                "modified": modified,
                "added": added,
                "deleted": deleted,
                "untracked": untracked,
                "has_changes": len(status_lines) > 0
            }
        except FileNotFoundError:
            return {"is_repo": False, "error": "Git not found"}
        except Exception as e:
            return {"is_repo": False, "error": str(e)}
    
    def get_git_diff(self) -> str:
        """Get git diff of staged and unstaged changes"""
        try:
            result = subprocess.run(
                ["git", "diff", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            return result.stdout if result.returncode == 0 else ""
        except Exception:
            return ""
    
    def get_recent_commits(self, count: int = 5) -> List[Dict]:
        """Get recent commit history"""
        try:
            result = subprocess.run(
                ["git", "log", f"-{count}", "--pretty=format:%h|%s|%an|%ad", "--date=short"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode != 0:
                return []
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split('|', 3)
                if len(parts) >= 4:
                    commits.append({
                        "hash": parts[0],
                        "message": parts[1],
                        "author": parts[2],
                        "date": parts[3]
                    })
            
            return commits
        except Exception:
            return []
    
    def analyze_changes(self) -> Dict:
        """
        Analyze git changes to extract work completed
        
        Returns:
            Dict with analysis of changes
        """
        status = self.get_git_status()
        diff = self.get_git_diff()
        commits = self.get_recent_commits()
        
        # Analyze file changes
        files_changed = set()
        files_changed.update(status.get("modified", []))
        files_changed.update(status.get("added", []))
        files_changed.update(status.get("deleted", []))
        
        # Categorize files
        python_files = [f for f in files_changed if f.endswith('.py')]
        config_files = [f for f in files_changed if f.endswith(('.md', '.txt', '.json', '.yaml', '.yml'))]
        other_files = [f for f in files_changed if not (f.endswith('.py') or f.endswith(('.md', '.txt', '.json', '.yaml', '.yml')))]
        
        # Extract work patterns from diff
        work_completed = []
        if diff:
            # Look for function definitions (new features)
            new_functions = re.findall(r'^\+\s+def\s+(\w+)', diff, re.MULTILINE)
            if new_functions:
                work_completed.append(f"Added {len(new_functions)} new function(s): {', '.join(new_functions[:5])}")
            
            # Look for class definitions
            new_classes = re.findall(r'^\+\s+class\s+(\w+)', diff, re.MULTILINE)
            if new_classes:
                work_completed.append(f"Added {len(new_classes)} new class(es): {', '.join(new_classes)}")
            
            # Look for TODO/FIXME removals (completed work)
            completed_todos = re.findall(r'^-\s*#\s*(TODO|FIXME):\s*(.+)', diff, re.MULTILINE)
            if completed_todos:
                work_completed.append(f"Completed {len(completed_todos)} TODO/FIXME item(s)")
        
        # Extract from commit messages
        for commit in commits:
            msg = commit.get("message", "").lower()
            if any(keyword in msg for keyword in ["add", "implement", "create", "fix", "update"]):
                work_completed.append(commit.get("message", ""))
        
        return {
            "files_changed": list(files_changed),
            "python_files": python_files,
            "config_files": config_files,
            "other_files": other_files,
            "work_completed": work_completed[:10],  # Limit to 10 items
            "recent_commits": commits,
            "has_changes": status.get("has_changes", False)
        }
    
    def get_next_session_number(self) -> int:
        """Get the next session number for dev log"""
        session_files = list(self.devlogs_dir.glob("session_*.md"))
        if not session_files:
            return 1
        
        # Extract session numbers
        session_numbers = []
        for file in session_files:
            match = re.search(r'session_(\d+)', file.name)
            if match:
                session_numbers.append(int(match.group(1)))
        
        return max(session_numbers) + 1 if session_numbers else 1
    
    def generate_devlog(
        self,
        session_number: Optional[int] = None,
        additional_notes: Optional[str] = None,
        objectives: Optional[List[str]] = None,
        challenges: Optional[List[str]] = None,
        solutions: Optional[List[str]] = None
    ) -> Tuple[str, str]:
        """
        Generate a dev log entry
        
        Args:
            session_number: Session number (auto-incremented if not provided)
            additional_notes: Additional notes to include
            objectives: List of objectives
            challenges: List of challenges encountered
            solutions: List of solutions implemented
        
        Returns:
            Tuple of (filepath, markdown_content)
        """
        # Get session number
        if session_number is None:
            session_number = self.get_next_session_number()
        
        # Analyze changes
        analysis = self.analyze_changes()
        
        # Get current date
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        # Generate filename
        filename = f"session_{session_number:02d}_devlog.md"
        filepath = self.devlogs_dir / filename
        
        # Build dev log content
        content = self._build_devlog_markdown(
            session_number=session_number,
            date=date_str,
            time=time_str,
            analysis=analysis,
            additional_notes=additional_notes,
            objectives=objectives,
            challenges=challenges,
            solutions=solutions
        )
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath), content
    
    def _build_devlog_markdown(
        self,
        session_number: int,
        date: str,
        time: str,
        analysis: Dict,
        additional_notes: Optional[str],
        objectives: Optional[List[str]],
        challenges: Optional[List[str]],
        solutions: Optional[List[str]]
    ) -> str:
        """Build the dev log markdown content"""
        
        # Format lists
        def format_list(items, default="None"):
            if not items:
                return default
            return "\n".join([f"- {item}" for item in items])
        
        files_changed = format_list(analysis.get("files_changed", []))
        work_completed = format_list(analysis.get("work_completed", []), "No work items extracted")
        python_files = format_list(analysis.get("python_files", []))
        
        objectives_str = format_list(objectives, "Not specified")
        challenges_str = format_list(challenges, "None")
        solutions_str = format_list(solutions, "None")
        
        md = f"""# Developer's Log - Session {session_number:02d}

**Date:** {date}  
**Time:** {time}  
**Session:** Session {session_number:02d}  
**Developer:** Fyrebug (WPMG)

## Overview
Development session for Echo Bot project.

## Objectives
{objectives_str}

## Work Completed
{work_completed}

**Files Changed:** {len(analysis.get('files_changed', []))}
- Python files: {len(analysis.get('python_files', []))}
- Config/docs: {len(analysis.get('config_files', []))}
- Other: {len(analysis.get('other_files', []))}

**Key Files Modified:**
{python_files if python_files != "None" else "None"}

## Challenges Encountered
{challenges_str}

## Solutions Implemented
{solutions_str}

## Notes & Observations
{additional_notes if additional_notes else "No additional notes"}

## Next Steps
- [ ] Review and test changes
- [ ] Continue with next feature/task
- [ ] Update documentation if needed

## Technical Details
- **Environment:** Windows 10, Python 3.10+
- **Dependencies:** See requirements.txt
- **Key Files Modified:** {', '.join(analysis.get('python_files', [])[:5]) if analysis.get('python_files') else 'None'}

## Git Status
- **Files Changed:** {len(analysis.get('files_changed', []))}
- **Recent Commits:** {len(analysis.get('recent_commits', []))}

---
*End of Session {session_number:02d} Log*

*For the forgotten 99%, we rise.* 🔥
"""
        return md

