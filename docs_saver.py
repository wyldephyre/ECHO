"""
Docs Saver Utility
Helper function to save content to docs folder
"""

from pathlib import Path
from datetime import datetime

def save_to_docs(content: str, filename: str, project_root: str = ".") -> tuple[str, str]:
    """
    Save content to docs folder
    
    Args:
        content: Content to save
        filename: Filename (will add .md if no extension)
        project_root: Project root directory
    
    Returns:
        Tuple of (filepath, confirmation_message)
    """
    docs_dir = Path(project_root) / "docs"
    docs_dir.mkdir(exist_ok=True)
    
    # Add .md extension if none provided
    if not filename.endswith(('.md', '.txt', '.json', '.yaml', '.yml')):
        filename += '.md'
    
    filepath = docs_dir / filename
    
    # Write content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    confirmation = f"✅ Saved to: {filepath}"
    
    return str(filepath), confirmation

