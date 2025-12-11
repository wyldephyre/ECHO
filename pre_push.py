"""
Pre-Push Workflow Script
Ensures code safety, generates dev logs, performs code review, and pushes to git
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

from devlog_generator import DevLogGenerator
from code_reviewer import CodeReviewer

class PrePushWorkflow:
    """Main pre-push workflow orchestrator"""
    
    def __init__(self, project_root: str = ".", dry_run: bool = False):
        """
        Initialize workflow
        
        Args:
            project_root: Root directory of the project
            dry_run: If True, don't actually push
        """
        self.project_root = Path(project_root)
        self.dry_run = dry_run
        self.devlog_gen = DevLogGenerator(str(project_root))
        self.code_reviewer = CodeReviewer(str(project_root))
        self.errors = []
        self.warnings = []
    
    def check_git_repo(self) -> bool:
        """Check if git repository exists"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                cwd=self.project_root
            )
            if result.returncode != 0:
                print("ERROR: Not a git repository. Initialize with: git init")
                return False
            return True
        except FileNotFoundError:
            print("ERROR: Git not found. Please install Git.")
            return False
    
    def check_git_status(self) -> bool:
        """Check git status for uncommitted changes"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode != 0:
                print("ERROR: Error checking git status")
                return False
            
            if not result.stdout.strip():
                print("INFO: No changes to commit")
                return False
            
            return True
        except Exception as e:
            print(f"ERROR: {e}")
            return False
    
    def check_syntax(self) -> bool:
        """Check syntax of Python files"""
        print("\n[CHECK] Checking syntax...")
        
        status = self.devlog_gen.get_git_status()
        if not status.get("is_repo"):
            return True  # Skip if not a repo
        
        python_files = []
        python_files.extend(status.get("modified", []))
        python_files.extend(status.get("added", []))
        
        syntax_errors = []
        for file_str in python_files:
            if not file_str.endswith('.py'):
                continue
            
            filepath = self.project_root / file_str
            if filepath.exists():
                issues = self.code_reviewer.check_syntax(filepath)
                syntax_errors.extend(issues)
        
        if syntax_errors:
            print("ERROR: Syntax errors found:")
            for issue in syntax_errors:
                print(f"   {issue.get('file')}:{issue.get('line')} - {issue.get('message')}")
            return False
        
        print("OK: Syntax check passed")
        return True
    
    def run_code_review(self) -> bool:
        """Run code review"""
        print("\n[REVIEW] Running code review...")
        
        review_results = self.code_reviewer.review_changed_files()
        
        critical = review_results.get("critical", [])
        warnings = review_results.get("warnings", [])
        info = review_results.get("info", [])
        
        print(f"   Files reviewed: {len(review_results.get('files_reviewed', []))}")
        print(f"   Critical issues: {len(critical)}")
        print(f"   Warnings: {len(warnings)}")
        print(f"   Info: {len(info)}")
        
        if critical:
            print("\nERROR: Critical issues found:")
            for issue in critical[:5]:
                print(f"   {issue.get('file')}:{issue.get('line')} - {issue.get('message')}")
            if len(critical) > 5:
                print(f"   ... and {len(critical) - 5} more")
            return False
        
        if warnings:
            print(f"\nWARNING: {len(warnings)} warnings found (non-blocking)")
        
        # Generate and save report
        report = self.code_reviewer.generate_report(review_results)
        report_path = self.project_root / "code_review_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"   Report saved to: {report_path}")
        
        print("OK: Code review passed")
        return True
    
    def generate_devlog(self, additional_notes: Optional[str] = None) -> Optional[str]:
        """Generate dev log"""
        print("\n[DEVLOG] Generating dev log...")
        
        try:
            filepath, content = self.devlog_gen.generate_devlog(
                additional_notes=additional_notes
            )
            print(f"OK: Dev log created: {filepath}")
            return filepath
        except Exception as e:
            print(f"WARNING: Error generating dev log: {e}")
            return None
    
    def check_secrets(self) -> bool:
        """Check for secrets in code"""
        print("\n[SECRETS] Checking for secrets...")
        
        status = self.devlog_gen.get_git_status()
        if not status.get("is_repo"):
            return True
        
        all_files = []
        all_files.extend(status.get("modified", []))
        all_files.extend(status.get("added", []))
        
        secret_issues = []
        for file_str in all_files:
            filepath = self.project_root / file_str
            if filepath.exists():
                issues = self.code_reviewer.check_secrets(filepath)
                secret_issues.extend(issues)
        
        if secret_issues:
            print("ERROR: Potential secrets found:")
            for issue in secret_issues:
                print(f"   {issue.get('file')}:{issue.get('line')} - {issue.get('message')}")
            print("   WARNING: Do not commit secrets! Use .env file instead.")
            return False
        
        print("OK: No secrets found")
        return True
    
    def stage_changes(self) -> bool:
        """Stage all changes"""
        print("\n[GIT] Staging changes...")
        
        try:
            result = subprocess.run(
                ["git", "add", "."],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode != 0:
                print(f"ERROR: Error staging changes: {result.stderr}")
                return False
            
            print("OK: Changes staged")
            return True
        except Exception as e:
            print(f"ERROR: {e}")
            return False
    
    def create_commit(self, message: Optional[str] = None) -> bool:
        """Create commit"""
        print("\n[GIT] Creating commit...")
        
        if not message:
            # Generate commit message from changes
            status = self.devlog_gen.get_git_status()
            analysis = self.devlog_gen.analyze_changes()
            
            files_count = len(analysis.get("files_changed", []))
            work_items = analysis.get("work_completed", [])[:3]
            
            if work_items:
                message = f"Update: {', '.join(work_items)}"
            else:
                message = f"Update: {files_count} file(s) changed"
        
        try:
            result = subprocess.run(
                ["git", "commit", "-m", message],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode != 0:
                if "nothing to commit" in result.stdout.lower():
                    print("INFO: Nothing to commit")
                    return True
                print(f"ERROR: Error creating commit: {result.stderr}")
                return False
            
            print(f"OK: Commit created: {message}")
            return True
        except Exception as e:
            print(f"ERROR: {e}")
            return False
    
    def push_to_remote(self, branch: Optional[str] = None) -> bool:
        """Push to remote repository"""
        if self.dry_run:
            print("\n[DRY RUN] Would push to remote")
            return True
        
        print("\n[GIT] Pushing to remote...")
        
        try:
            # Get current branch if not specified
            if not branch:
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root
                )
                if result.returncode == 0:
                    branch = result.stdout.strip()
                else:
                    branch = "main"
            
            result = subprocess.run(
                ["git", "push", "origin", branch],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode != 0:
                print(f"ERROR: Error pushing: {result.stderr}")
                return False
            
            print(f"OK: Pushed to origin/{branch}")
            return True
        except Exception as e:
            print(f"ERROR: {e}")
            return False
    
    def run_full_workflow(
        self,
        skip_review: bool = False,
        skip_devlog: bool = False,
        commit_message: Optional[str] = None,
        additional_notes: Optional[str] = None,
        branch: Optional[str] = None
    ) -> bool:
        """
        Run the full pre-push workflow
        
        Returns:
            True if successful, False otherwise
        """
        print("=" * 60)
        print("PRE-PUSH WORKFLOW")
        print("=" * 60)
        
        # Step 1: Check git repo
        if not self.check_git_repo():
            return False
        
        # Step 2: Check for changes
        if not self.check_git_status():
            return False
        
        # Step 3: Check syntax
        if not self.check_syntax():
            print("\nERROR: Syntax check failed. Fix errors before pushing.")
            return False
        
        # Step 4: Check for secrets
        if not self.check_secrets():
            print("\nERROR: Secret check failed. Remove secrets before pushing.")
            return False
        
        # Step 5: Code review
        if not skip_review:
            if not self.run_code_review():
                print("\nERROR: Code review failed. Fix critical issues before pushing.")
                response = input("\nContinue anyway? (y/N): ")
                if response.lower() != 'y':
                    return False
        else:
            print("\n[SKIP] Skipping code review")
        
        # Step 6: Generate dev log
        devlog_path = None
        if not skip_devlog:
            devlog_path = self.generate_devlog(additional_notes=additional_notes)
        else:
            print("\n[SKIP] Skipping dev log generation")
        
        # Step 7: Stage changes
        if not self.stage_changes():
            return False
        
        # Step 8: Create commit
        if not self.create_commit(message=commit_message):
            return False
        
        # Step 9: Push to remote
        if not self.push_to_remote(branch=branch):
            return False
        
        print("\n" + "=" * 60)
        print("OK: PRE-PUSH WORKFLOW COMPLETE")
        print("=" * 60)
        
        if devlog_path:
            print(f"[INFO] Dev log: {devlog_path}")
        
        return True


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description="Pre-push workflow: code review, dev log, and git push"
    )
    parser.add_argument(
        "--skip-review",
        action="store_true",
        help="Skip code review"
    )
    parser.add_argument(
        "--skip-devlog",
        action="store_true",
        help="Skip dev log generation"
    )
    parser.add_argument(
        "--review-only",
        action="store_true",
        help="Only run code review"
    )
    parser.add_argument(
        "--devlog-only",
        action="store_true",
        help="Only generate dev log"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run (don't actually push)"
    )
    parser.add_argument(
        "--commit-message",
        help="Custom commit message"
    )
    parser.add_argument(
        "--notes",
        help="Additional notes for dev log"
    )
    parser.add_argument(
        "--branch",
        help="Branch to push to (default: current branch)"
    )
    
    args = parser.parse_args()
    
    workflow = PrePushWorkflow(dry_run=args.dry_run)
    
    if args.review_only:
        # Just run code review
        workflow.run_code_review()
        return
    
    if args.devlog_only:
        # Just generate dev log
        workflow.generate_devlog(additional_notes=args.notes)
        return
    
    # Run full workflow
    success = workflow.run_full_workflow(
        skip_review=args.skip_review,
        skip_devlog=args.skip_devlog,
        commit_message=args.commit_message,
        additional_notes=args.notes,
        branch=args.branch
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

