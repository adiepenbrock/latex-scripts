#!/usr/bin/env python3
"""
LaTeX Acronym Sorter

This script reads a LaTeX file containing acronym definitions and sorts them
alphabetically by their abbreviations (the content in square brackets).
"""

import re
import sys
from typing import List, Tuple

def parse_acronym_line(line: str) -> Tuple[str, str, str, str]:
    """
    Parse an acronym line and extract its components.
    
    Args:
        line: A line containing \acro{label}[ABBREV]{Description}
        
    Returns:
        Tuple of (full_line, label, abbreviation, description)
    """
    # Regex pattern to match \acro{label}[ABBREV]{Description}
    pattern = r'\\acro\{([^}]+)\}\[([^\]]+)\]\{([^}]+)\}'
    match = re.match(r'\s*' + pattern, line)
    
    if match:
        label = match.group(1)
        abbreviation = match.group(2)
        description = match.group(3)
        return (line.strip(), label, abbreviation, description)
    return None

def sort_acronyms_in_file(input_file: str, output_file: str = None):
    """
    Sort acronyms in a LaTeX file alphabetically by abbreviation.
    
    Args:
        input_file: Path to the input LaTeX file
        output_file: Path to the output file (if None, overwrites input file)
    """
    if output_file is None:
        output_file = input_file
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Find acronym entries and their line indices
    acronym_entries = []
    acronym_indices = []
    
    for i, line in enumerate(lines):
        parsed = parse_acronym_line(line)
        if parsed:
            acronym_entries.append(parsed)
            acronym_indices.append(i)
    
    if not acronym_entries:
        print("No acronym entries found in the file.")
        return
    
    # Sort acronym entries by abbreviation (case-insensitive)
    acronym_entries.sort(key=lambda x: x[2].upper())
    
    # Replace the original acronym lines with sorted ones
    for i, (original_line, label, abbrev, desc) in enumerate(acronym_entries):
        if i < len(acronym_indices):
            # Reconstruct the line with original indentation
            original_line_at_index = lines[acronym_indices[i]]
            leading_whitespace = len(original_line_at_index) - len(original_line_at_index.lstrip())
            whitespace = original_line_at_index[:leading_whitespace]
            
            new_line = f"{whitespace}\\acro{{{label}}}[{abbrev}]{{{desc}}}\n"
            lines[acronym_indices[i]] = new_line
    
    # Write the sorted content to output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"Successfully sorted {len(acronym_entries)} acronym entries.")
        print(f"Sorted order:")
        for _, label, abbrev, desc in acronym_entries:
            print(f"  {abbrev}: {desc}")
            
    except Exception as e:
        print(f"Error writing file: {e}")

def main():
    """Main function to handle command line arguments and run the sorter."""
    if len(sys.argv) < 2:
        print("Usage: python acronym_sorter.py <input_file> [output_file]")
        print("If output_file is not provided, the input file will be overwritten.")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    sort_acronyms_in_file(input_file, output_file)

if __name__ == "__main__":
    main()
