"""
Auto-generate Restart Handoff from Conversation Summary
Helps create restart handoffs quickly from conversation context
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional
from handoff_generator import HandoffGenerator

def parse_conversation_summary(summary_text: str) -> Dict:
    """
    Parse a conversation summary to extract progress information
    
    Args:
        summary_text: Text summary of the conversation
    
    Returns:
        Dict with progress_update structure
    """
    # This is a simple parser - you can enhance it with NLP if needed
    progress = {
        'work_completed': [],
        'work_in_progress': [],
        'blockers': [],
        'discoveries': [],
        'files_modified': [],
        'next_steps': [],
        'context_summary': summary_text
    }
    
    # Try to extract structured information if present
    lines = summary_text.split('\n')
    current_section = None
    
    for line in lines:
        line_lower = line.lower().strip()
        
        if 'completed' in line_lower or 'done' in line_lower or 'finished' in line_lower:
            if line.strip() and not line.strip().startswith('#'):
                progress['work_completed'].append(line.strip('- ').strip())
        elif 'in progress' in line_lower or 'working on' in line_lower:
            if line.strip() and not line.strip().startswith('#'):
                progress['work_in_progress'].append(line.strip('- ').strip())
        elif 'blocker' in line_lower or 'stuck' in line_lower or 'issue' in line_lower:
            if line.strip() and not line.strip().startswith('#'):
                progress['blockers'].append(line.strip('- ').strip())
        elif 'discover' in line_lower or 'found' in line_lower or 'learned' in line_lower:
            if line.strip() and not line.strip().startswith('#'):
                progress['discoveries'].append(line.strip('- ').strip())
        elif '.py' in line or 'file' in line_lower:
            if line.strip() and not line.strip().startswith('#'):
                progress['files_modified'].append(line.strip('- ').strip())
        elif 'next' in line_lower or 'todo' in line_lower:
            if line.strip() and not line.strip().startswith('#'):
                progress['next_steps'].append(line.strip('- ').strip())
    
    return progress

def interactive_restart_handoff(
    original_handoff_path: str,
    conversation_summary: Optional[str] = None
) -> str:
    """
    Interactively create a restart handoff
    
    Args:
        original_handoff_path: Path to original handoff
        conversation_summary: Optional conversation summary
    
    Returns:
        Path to created restart handoff
    """
    generator = HandoffGenerator(str(Path.cwd()))
    
    print("=" * 60)
    print("RESTART HANDOFF GENERATOR")
    print("=" * 60)
    print()
    
    # Parse conversation summary if provided
    if conversation_summary:
        print("Parsing conversation summary...")
        progress = parse_conversation_summary(conversation_summary)
    else:
        progress = {
            'work_completed': [],
            'work_in_progress': [],
            'blockers': [],
            'discoveries': [],
            'files_modified': [],
            'next_steps': [],
            'context_summary': ''
        }
    
    # Interactive prompts
    print("\nWork Completed (press Enter twice when done):")
    while True:
        item = input("  - ")
        if not item:
            break
        progress['work_completed'].append(item)
    
    print("\nWork In Progress (press Enter twice when done):")
    while True:
        item = input("  - ")
        if not item:
            break
        progress['work_in_progress'].append(item)
    
    print("\nBlockers (press Enter twice when done, or just Enter if none):")
    while True:
        item = input("  - ")
        if not item:
            break
        progress['blockers'].append(item)
    
    print("\nImportant Discoveries (press Enter twice when done):")
    while True:
        item = input("  - ")
        if not item:
            break
        progress['discoveries'].append(item)
    
    print("\nFiles Modified (format: filename.py - what changed, press Enter twice when done):")
    while True:
        item = input("  - ")
        if not item:
            break
        progress['files_modified'].append(item)
    
    print("\nNext Steps (press Enter twice when done):")
    while True:
        item = input("  - ")
        if not item:
            break
        progress['next_steps'].append(item)
    
    if not progress['context_summary']:
        print("\nContext Summary (brief 2-3 sentence summary):")
        progress['context_summary'] = input("  ")
    
    # Generate handoff
    print("\nGenerating restart handoff...")
    filepath, content = generator.generate_restart_handoff(
        original_handoff_path=original_handoff_path,
        progress_update=progress,
        conversation_summary=conversation_summary
    )
    
    print(f"\nOK: Restart handoff created: {filepath}")
    return filepath

def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description="Generate restart handoff from conversation summary"
    )
    parser.add_argument(
        "original_handoff",
        help="Path to original handoff file"
    )
    parser.add_argument(
        "--summary",
        help="Conversation summary text (or file path)"
    )
    parser.add_argument(
        "--summary-file",
        help="Path to file containing conversation summary"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive mode (prompts for all fields)"
    )
    parser.add_argument(
        "--json",
        help="Path to JSON file with progress update structure"
    )
    
    args = parser.parse_args()
    
    # Get conversation summary
    conversation_summary = None
    if args.summary_file:
        conversation_summary = Path(args.summary_file).read_text(encoding='utf-8')
    elif args.summary:
        # Check if it's a file path
        summary_path = Path(args.summary)
        if summary_path.exists():
            conversation_summary = summary_path.read_text(encoding='utf-8')
        else:
            conversation_summary = args.summary
    elif args.json:
        # Load from JSON
        with open(args.json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            conversation_summary = data.get('conversation_summary', '')
            progress_update = data.get('progress_update', {})
            
            generator = HandoffGenerator(str(Path.cwd()))
            filepath, content = generator.generate_restart_handoff(
                original_handoff_path=args.original_handoff,
                progress_update=progress_update,
                conversation_summary=conversation_summary
            )
            print(f"OK: Restart handoff created: {filepath}")
            return
    
    # Interactive or parse summary
    if args.interactive or not conversation_summary:
        filepath = interactive_restart_handoff(
            original_handoff_path=args.original_handoff,
            conversation_summary=conversation_summary
        )
    else:
        # Parse and generate
        generator = HandoffGenerator(str(Path.cwd()))
        progress = parse_conversation_summary(conversation_summary)
        
        filepath, content = generator.generate_restart_handoff(
            original_handoff_path=args.original_handoff,
            progress_update=progress,
            conversation_summary=conversation_summary
        )
        
        print(f"OK: Restart handoff created: {filepath}")
        print("\nReview and edit if needed to refine the extracted information.")

if __name__ == "__main__":
    main()

