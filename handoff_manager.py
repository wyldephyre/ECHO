"""
Handoff Management Script
Tracks active vs completed handoffs, prevents conflicts, manages task assignments
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime

class HandoffManager:
    """Manages specialist handoff documents"""
    
    def __init__(self, project_root: str = "."):
        """
        Initialize handoff manager
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.handoffs_dir = self.project_root / "handoffs"
        self.status_file = self.handoffs_dir / ".handoff_status.json"
        self.handoffs_dir.mkdir(exist_ok=True)
        
        # Load or create status file
        self.status_data = self._load_status()
    
    def _load_status(self) -> Dict:
        """Load handoff status from JSON file"""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"handoffs": {}, "last_updated": None}
        return {"handoffs": {}, "last_updated": None}
    
    def _save_status(self):
        """Save handoff status to JSON file"""
        self.status_data["last_updated"] = datetime.now().isoformat()
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(self.status_data, f, indent=2)
    
    def _parse_handoff(self, filepath: Path) -> Optional[Dict]:
        """
        Parse a handoff markdown file to extract metadata
        
        Returns:
            Dict with task_name, status, assigned_droid, files_can_modify, files_cannot_modify
        """
        try:
            content = filepath.read_text(encoding='utf-8')
            
            # Extract task name from header
            task_match = re.search(r'# Specialist Task Handoff - (.+)', content)
            task_name = task_match.group(1).strip() if task_match else filepath.stem
            
            # Extract status
            status_match = re.search(r'\*\*Status:\*\* (.+)', content)
            status = status_match.group(1).strip() if status_match else "Unknown"
            
            # Extract assigned droid
            droid_match = re.search(r'\*\*Assigned To:\*\* (.+)', content)
            assigned_droid = droid_match.group(1).strip() if droid_match else "Unknown"
            
            # Extract files can modify
            can_modify_section = re.search(
                r'### Files You CAN Modify:\s*\n((?:- .+\n?)+)',
                content,
                re.MULTILINE
            )
            files_can_modify = []
            if can_modify_section:
                files_can_modify = [
                    line.strip('- ').strip()
                    for line in can_modify_section.group(1).split('\n')
                    if line.strip() and not line.strip().startswith('#')
                ]
            
            # Extract files cannot modify
            cannot_modify_section = re.search(
                r'### Files You CANNOT Modify:\s*\n((?:- .+\n?)+)',
                content,
                re.MULTILINE
            )
            files_cannot_modify = []
            if cannot_modify_section:
                files_cannot_modify = [
                    line.strip('- ').strip()
                    for line in cannot_modify_section.group(1).split('\n')
                    if line.strip() and not line.strip().startswith('#')
                ]
            
            # Extract dependencies
            deps_section = re.search(
                r'### Dependencies:\s*\n((?:.+\n?)+?)(?=###|$)',
                content,
                re.MULTILINE | re.DOTALL
            )
            dependencies = []
            if deps_section:
                deps_text = deps_section.group(1).strip()
                if deps_text and "None" not in deps_text:
                    dependencies = [line.strip('- ').strip() for line in deps_text.split('\n') if line.strip()]
            
            return {
                "task_name": task_name,
                "status": status,
                "assigned_droid": assigned_droid,
                "files_can_modify": files_can_modify,
                "files_cannot_modify": files_cannot_modify,
                "dependencies": dependencies,
                "filepath": str(filepath),
                "filename": filepath.name
            }
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            return None
    
    def _get_all_handoffs(self) -> List[Path]:
        """Get all handoff markdown files"""
        handoff_files = []
        for filepath in self.handoffs_dir.glob("handoff_*.md"):
            if filepath.name != "specialist_handoff_template.md":
                handoff_files.append(filepath)
        return handoff_files
    
    def _extract_file_paths(self, file_list: List[str]) -> Set[str]:
        """
        Extract actual file paths from file list strings
        Handles patterns like "ai_coordinator.py (only method X, lines Y-Z)"
        """
        file_paths = set()
        for item in file_list:
            # Extract the file path part (before any parentheses)
            file_path = item.split('(')[0].strip()
            if file_path:
                file_paths.add(file_path)
        return file_paths
    
    def list_active(self) -> List[Dict]:
        """List all active specialist handoffs"""
        active_handoffs = []
        for filepath in self._get_all_handoffs():
            parsed = self._parse_handoff(filepath)
            if parsed and parsed["status"].lower() in ["active", "in progress"]:
                active_handoffs.append(parsed)
        return active_handoffs
    
    def list_completed(self) -> List[Dict]:
        """List all completed handoffs"""
        completed_handoffs = []
        for filepath in self._get_all_handoffs():
            parsed = self._parse_handoff(filepath)
            if parsed and parsed["status"].lower() == "complete":
                completed_handoffs.append(parsed)
        return completed_handoffs
    
    def check_conflicts(self) -> Dict[str, List[str]]:
        """
        Check for file conflicts between active handoffs
        
        Returns:
            Dict mapping file paths to list of conflicting handoff names
        """
        active_handoffs = self.list_active()
        conflicts = {}
        
        # Build a map of files to handoffs
        file_to_handoffs = {}
        for handoff in active_handoffs:
            files_can_modify = self._extract_file_paths(handoff["files_can_modify"])
            for file_path in files_can_modify:
                if file_path not in file_to_handoffs:
                    file_to_handoffs[file_path] = []
                file_to_handoffs[file_path].append(handoff["task_name"])
        
        # Find conflicts (files modified by multiple handoffs)
        for file_path, handoff_names in file_to_handoffs.items():
            if len(handoff_names) > 1:
                conflicts[file_path] = handoff_names
        
        return conflicts
    
    def mark_complete(self, handoff_name: str) -> bool:
        """
        Mark a handoff as complete
        
        Args:
            handoff_name: Name of the handoff (task name or filename)
        
        Returns:
            True if successful, False otherwise
        """
        # Find the handoff file
        handoff_file = None
        for filepath in self._get_all_handoffs():
            parsed = self._parse_handoff(filepath)
            if parsed and (parsed["task_name"] == handoff_name or parsed["filename"] == handoff_name):
                handoff_file = filepath
                break
        
        if not handoff_file:
            print(f"Handoff '{handoff_name}' not found")
            return False
        
        # Update status in file
        try:
            content = handoff_file.read_text(encoding='utf-8')
            # Replace status line
            content = re.sub(
                r'\*\*Status:\*\* .+',
                '**Status:** Complete',
                content
            )
            handoff_file.write_text(content, encoding='utf-8')
            
            # Update status file
            parsed = self._parse_handoff(handoff_file)
            if parsed:
                self.status_data["handoffs"][parsed["filename"]] = {
                    "task_name": parsed["task_name"],
                    "status": "Complete",
                    "completed_at": datetime.now().isoformat()
                }
                self._save_status()
            
            print(f"Marked '{handoff_name}' as complete")
            return True
        except Exception as e:
            print(f"Error marking handoff complete: {e}")
            return False
    
    def generate_report(self) -> str:
        """Generate a status report of all handoffs"""
        active = self.list_active()
        completed = self.list_completed()
        conflicts = self.check_conflicts()
        
        report = []
        report.append("=" * 60)
        report.append("HANDOFF STATUS REPORT")
        report.append("=" * 60)
        report.append("")
        
        report.append(f"Active Handoffs: {len(active)}")
        if active:
            for handoff in active:
                report.append(f"  - {handoff['task_name']}")
                report.append(f"    Assigned: {handoff['assigned_droid']}")
                report.append(f"    Status: {handoff['status']}")
                report.append(f"    Files: {', '.join(handoff['files_can_modify'][:3])}...")
        else:
            report.append("  None")
        report.append("")
        
        report.append(f"Completed Handoffs: {len(completed)}")
        if completed:
            for handoff in completed:
                report.append(f"  - {handoff['task_name']}")
        else:
            report.append("  None")
        report.append("")
        
        if conflicts:
            report.append("WARNING: FILE CONFLICTS DETECTED:")
            for file_path, handoff_names in conflicts.items():
                report.append(f"  {file_path}:")
                for name in handoff_names:
                    report.append(f"    - {name}")
        else:
            report.append("OK: No file conflicts detected")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    """CLI interface for handoff manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage specialist handoff documents")
    parser.add_argument(
        "command",
        choices=["list", "active", "completed", "check", "complete", "report"],
        help="Command to execute"
    )
    parser.add_argument(
        "--name",
        help="Handoff name (for complete command)"
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Project root directory (default: current directory)"
    )
    
    args = parser.parse_args()
    manager = HandoffManager(args.root)
    
    if args.command == "list" or args.command == "active":
        active = manager.list_active()
        if active:
            print(f"\nActive Handoffs ({len(active)}):")
            print("-" * 60)
            for handoff in active:
                print(f"  {handoff['task_name']}")
                print(f"    Assigned: {handoff['assigned_droid']}")
                print(f"    Status: {handoff['status']}")
                print(f"    File: {handoff['filename']}")
                print()
        else:
            print("No active handoffs found")
    
    elif args.command == "completed":
        completed = manager.list_completed()
        if completed:
            print(f"\nCompleted Handoffs ({len(completed)}):")
            print("-" * 60)
            for handoff in completed:
                print(f"  {handoff['task_name']}")
                print(f"    File: {handoff['filename']}")
                print()
        else:
            print("No completed handoffs found")
    
    elif args.command == "check":
        conflicts = manager.check_conflicts()
        if conflicts:
            print("\nWARNING: FILE CONFLICTS DETECTED:")
            print("-" * 60)
            for file_path, handoff_names in conflicts.items():
                print(f"\n  {file_path}:")
                for name in handoff_names:
                    print(f"    - {name}")
            print()
        else:
            print("\nOK: No file conflicts detected")
    
    elif args.command == "complete":
        if not args.name:
            print("Error: --name required for complete command")
            print("Usage: python handoff_manager.py complete --name <handoff_name>")
            return
        manager.mark_complete(args.name)
    
    elif args.command == "report":
        print(manager.generate_report())


if __name__ == "__main__":
    main()

