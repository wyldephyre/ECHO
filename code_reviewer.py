"""
Code Reviewer
Performs static analysis and code review on changed files
"""

import subprocess
import re
import ast
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class CodeReviewer:
    """Performs code review and static analysis"""
    
    def __init__(self, project_root: str = "."):
        """
        Initialize code reviewer
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.issues = []
    
    def check_syntax(self, filepath: Path) -> List[Dict]:
        """
        Check Python file syntax
        
        Args:
            filepath: Path to Python file
        
        Returns:
            List of syntax issues
        """
        issues = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            
            try:
                ast.parse(source, filename=str(filepath))
            except SyntaxError as e:
                issues.append({
                    "type": "syntax_error",
                    "severity": "critical",
                    "file": str(filepath),
                    "line": e.lineno,
                    "message": f"Syntax error: {e.msg}",
                    "suggestion": "Fix syntax error before committing"
                })
        except Exception as e:
            issues.append({
                "type": "file_error",
                "severity": "critical",
                "file": str(filepath),
                "message": f"Could not read file: {str(e)}"
            })
        
        return issues
    
    def check_imports(self, filepath: Path) -> List[Dict]:
        """
        Check for import issues
        
        Args:
            filepath: Path to Python file
        
        Returns:
            List of import issues
        """
        issues = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(filepath))
            
            # Check for imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    else:
                        imports.append(node.module or "")
            
            # Check for common issues
            # Unused imports would require more complex analysis
            # For now, just check if imports are valid syntax
            
        except Exception as e:
            # Syntax errors already caught by check_syntax
            pass
        
        return issues
    
    def check_secrets(self, filepath: Path) -> List[Dict]:
        """
        Check for potential secrets in code
        
        Args:
            filepath: Path to file
        
        Returns:
            List of potential secret issues
        """
        issues = []
        secret_patterns = [
            (r'api[_-]?key\s*=\s*["\']([^"\']+)["\']', "API key found"),
            (r'password\s*=\s*["\']([^"\']+)["\']', "Password found"),
            (r'token\s*=\s*["\']([^"\']+)["\']', "Token found"),
            (r'secret\s*=\s*["\']([^"\']+)["\']', "Secret found"),
        ]
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern, message in secret_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Check if it's in a comment or .env reference
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line = content[line_start:match.end()].strip()
                    
                    # Skip if it's a comment or .env reference
                    if line.startswith('#') or '.env' in line or 'os.getenv' in line or 'os.environ' in line:
                        continue
                    
                    issues.append({
                        "type": "potential_secret",
                        "severity": "critical",
                        "file": str(filepath),
                        "line": content[:match.start()].count('\n') + 1,
                        "message": message,
                        "suggestion": "Use environment variables or .env file instead"
                    })
        except Exception:
            pass
        
        return issues
    
    def check_common_issues(self, filepath: Path) -> List[Dict]:
        """
        Check for common code issues
        
        Args:
            filepath: Path to Python file
        
        Returns:
            List of common issues
        """
        issues = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                # Check for print statements (should use logging)
                if re.search(r'\bprint\s*\(', line) and not line.strip().startswith('#'):
                    issues.append({
                        "type": "print_statement",
                        "severity": "warning",
                        "file": str(filepath),
                        "line": i,
                        "message": "Print statement found - use logger instead",
                        "suggestion": "Replace with logger.info(), logger.error(), etc."
                    })
                
                # Check for TODO/FIXME
                if re.search(r'\b(TODO|FIXME|XXX|HACK)\b', line, re.IGNORECASE):
                    issues.append({
                        "type": "todo_comment",
                        "severity": "info",
                        "file": str(filepath),
                        "line": i,
                        "message": f"TODO/FIXME comment found: {line.strip()}",
                        "suggestion": "Address before final commit or document in dev log"
                    })
                
                # Check for hardcoded paths
                if re.search(r'["\']([A-Z]:\\|/home/|/Users/)', line):
                    issues.append({
                        "type": "hardcoded_path",
                        "severity": "warning",
                        "file": str(filepath),
                        "line": i,
                        "message": "Hardcoded path found",
                        "suggestion": "Use Path or relative paths"
                    })
        
        except Exception:
            pass
        
        return issues
    
    def review_file(self, filepath: Path) -> List[Dict]:
        """
        Perform full review on a file
        
        Args:
            filepath: Path to file
        
        Returns:
            List of all issues found
        """
        all_issues = []
        
        if filepath.suffix != '.py':
            return all_issues
        
        all_issues.extend(self.check_syntax(filepath))
        all_issues.extend(self.check_imports(filepath))
        all_issues.extend(self.check_secrets(filepath))
        all_issues.extend(self.check_common_issues(filepath))
        
        return all_issues
    
    def review_changed_files(self) -> Dict:
        """
        Review all changed files
        
        Returns:
            Dict with review results
        """
        # Get changed files from git
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            changed_files = []
            if result.returncode == 0 and result.stdout:
                changed_files = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            
            # Also check untracked Python files
            result = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0 and result.stdout:
                untracked = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                changed_files.extend([f for f in untracked if f.endswith('.py')])
        except Exception:
            changed_files = []
        
        # Review each file
        all_issues = []
        files_reviewed = []
        
        for file_str in changed_files:
            filepath = self.project_root / file_str
            if filepath.exists() and filepath.suffix == '.py':
                issues = self.review_file(filepath)
                all_issues.extend(issues)
                files_reviewed.append(str(filepath))
        
        # Categorize issues
        critical = [i for i in all_issues if i.get("severity") == "critical"]
        warnings = [i for i in all_issues if i.get("severity") == "warning"]
        info = [i for i in all_issues if i.get("severity") == "info"]
        
        return {
            "files_reviewed": files_reviewed,
            "total_issues": len(all_issues),
            "critical": critical,
            "warnings": warnings,
            "info": info,
            "all_issues": all_issues,
            "passed": len(critical) == 0
        }
    
    def generate_report(self, review_results: Dict) -> str:
        """
        Generate code review report
        
        Args:
            review_results: Results from review_changed_files()
        
        Returns:
            Markdown report
        """
        critical = review_results.get("critical", [])
        warnings = review_results.get("warnings", [])
        info = review_results.get("info", [])
        
        report = []
        report.append("# Code Review Report")
        report.append("")
        report.append(f"**Files Reviewed:** {len(review_results.get('files_reviewed', []))}")
        report.append(f"**Total Issues:** {review_results.get('total_issues', 0)}")
        report.append(f"**Status:** {'❌ FAILED' if critical else '✅ PASSED' if not warnings else '⚠️ WARNINGS'}")
        report.append("")
        
        if critical:
            report.append("## 🔴 Critical Issues")
            report.append("")
            for issue in critical:
                report.append(f"### {issue.get('file', 'Unknown')}:{issue.get('line', '?')}")
                report.append(f"- **Type:** {issue.get('type', 'unknown')}")
                report.append(f"- **Message:** {issue.get('message', 'No message')}")
                report.append(f"- **Suggestion:** {issue.get('suggestion', 'Review and fix')}")
                report.append("")
        
        if warnings:
            report.append("## ⚠️ Warnings")
            report.append("")
            for issue in warnings[:10]:  # Limit to 10 warnings
                report.append(f"- **{issue.get('file', 'Unknown')}:{issue.get('line', '?')}** - {issue.get('message', 'No message')}")
            if len(warnings) > 10:
                report.append(f"- ... and {len(warnings) - 10} more warnings")
            report.append("")
        
        if info:
            report.append("## ℹ️ Info")
            report.append(f"- {len(info)} informational items (TODO comments, etc.)")
            report.append("")
        
        if not critical and not warnings:
            report.append("✅ No issues found!")
        
        return "\n".join(report)



