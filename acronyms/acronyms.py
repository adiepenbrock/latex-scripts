#!/usr/bin/env python3
"""
LaTeX Acronym Management Tool

This script provides three main functionalities:
1. Sort acronym definitions alphabetically by their abbreviations
2. Check LaTeX files for acronym usage and find missing/unused definitions
3. Remove unused acronym definitions to keep files clean
"""

import re
import os
import sys
import glob
import argparse
from typing import Set, Dict, List, Tuple
from pathlib import Path

class AcronymSorter:
    """Handles sorting of LaTeX acronym definitions."""
    
    @staticmethod
    def parse_acronym_line(line: str) -> Tuple[str, str, str, str]:
        """
        Parse an acronym line and extract its components.
        
        Args:
            line: A line containing \acro{label}[ABBREV]{Description}
            
        Returns:
            Tuple of (full_line, label, abbreviation, description) or None
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
    
    @staticmethod
    def sort_acronyms_in_file(input_file: str, output_file: str = None) -> bool:
        """
        Sort acronyms in a LaTeX file alphabetically by abbreviation.
        
        Args:
            input_file: Path to the input LaTeX file
            output_file: Path to the output file (if None, overwrites input file)
            
        Returns:
            True if successful, False otherwise
        """
        if output_file is None:
            output_file = input_file
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: File '{input_file}' not found.")
            return False
        except Exception as e:
            print(f"Error reading file: {e}")
            return False
        
        # Find acronym entries and their line indices
        acronym_entries = []
        acronym_indices = []
        
        for i, line in enumerate(lines):
            parsed = AcronymSorter.parse_acronym_line(line)
            if parsed:
                acronym_entries.append(parsed)
                acronym_indices.append(i)
        
        if not acronym_entries:
            print("No acronym entries found in the file.")
            return False
        
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
            
            print(f"✅ Successfully sorted {len(acronym_entries)} acronym entries.")
            print(f"📝 Sorted order:")
            for _, label, abbrev, desc in acronym_entries:
                print(f"   {abbrev}: {desc}")
            return True
                
        except Exception as e:
            print(f"Error writing file: {e}")
            return False

class AcronymChecker:
    """Handles checking of LaTeX acronym usage."""
    
    def __init__(self):
        # Common acronym package commands
        self.acronym_patterns = [
            r'\\ac\{([^}]+)\}',           # \ac{label}
            r'\\acp\{([^}]+)\}',          # \acp{label} (plural)
            r'\\acs\{([^}]+)\}',          # \acs{label} (short)
            r'\\acl\{([^}]+)\}',          # \acl{label} (long)
            r'\\acf\{([^}]+)\}',          # \acf{label} (full)
            r'\\acrshort\{([^}]+)\}',     # \acrshort{label}
            r'\\acrlong\{([^}]+)\}',      # \acrlong{label}
            r'\\acrfull\{([^}]+)\}',      # \acrfull{label}
            r'\\Ac\{([^}]+)\}',           # \Ac{label} (capitalized)
            r'\\Acp\{([^}]+)\}',          # \Acp{label} (capitalized plural)
            r'\\Acs\{([^}]+)\}',          # \Acs{label} (capitalized short)
            r'\\Acl\{([^}]+)\}',          # \Acl{label} (capitalized long)
            r'\\Acf\{([^}]+)\}',          # \Acf{label} (capitalized full)
            r'\\ACshort\{([^}]+)\}',      # \ACshort{label} (all caps short)
            r'\\AClong\{([^}]+)\}',       # \AClong{label} (all caps long)
            r'\\ACfull\{([^}]+)\}',       # \ACfull{label} (all caps full)
        ]
        
        # Pattern to match acronym definitions
        self.definition_pattern = r'\\acro\{([^}]+)\}\[([^\]]+)\]\{([^}]+)\}'
    
    def find_defined_acronyms(self, acronym_file: str) -> Dict[str, Tuple[str, str]]:
        """
        Extract all defined acronyms from the acronyms file.
        
        Args:
            acronym_file: Path to the file containing acronym definitions
            
        Returns:
            Dictionary mapping label -> (abbreviation, description)
        """
        defined_acronyms = {}
        
        try:
            with open(acronym_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: Acronym file '{acronym_file}' not found.")
            return {}
        except Exception as e:
            print(f"Error reading acronym file: {e}")
            return {}
        
        # Find all acronym definitions
        matches = re.findall(self.definition_pattern, content)
        for label, abbrev, desc in matches:
            defined_acronyms[label] = (abbrev, desc)
        
        return defined_acronyms
    
    def find_used_acronyms(self, latex_files: List[str]) -> Dict[str, List[Tuple[str, int]]]:
        """
        Find all used acronyms in LaTeX files.
        
        Args:
            latex_files: List of LaTeX file paths to check
            
        Returns:
            Dictionary mapping acronym_label -> [(filename, line_number), ...]
        """
        used_acronyms = {}
        
        for file_path in latex_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except Exception as e:
                print(f"Warning: Could not read file '{file_path}': {e}")
                continue
            
            for line_num, line in enumerate(lines, 1):
                # Check each acronym pattern
                for pattern in self.acronym_patterns:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        label = match.group(1)
                        if label not in used_acronyms:
                            used_acronyms[label] = []
                        used_acronyms[label].append((file_path, line_num))
        
        return used_acronyms
    
    def get_latex_files(self, directory: str = ".", recursive: bool = True) -> List[str]:
        """
        Get all LaTeX files in the specified directory.
        
        Args:
            directory: Directory to search in
            recursive: Whether to search recursively in subdirectories
            
        Returns:
            List of LaTeX file paths
        """
        if recursive:
            pattern = os.path.join(directory, "**", "*.tex")
            files = glob.glob(pattern, recursive=True)
        else:
            pattern = os.path.join(directory, "*.tex")
            files = glob.glob(pattern)
        
        return sorted(files)
    
    def check_acronyms(self, acronym_file: str, latex_files: List[str] = None, 
                      directory: str = ".", recursive: bool = True) -> bool:
        """
        Main function to check acronym usage.
        
        Args:
            acronym_file: Path to the acronyms definition file
            latex_files: Specific LaTeX files to check (if None, search directory)
            directory: Directory to search for LaTeX files
            recursive: Whether to search recursively
            
        Returns:
            True if check completed successfully, False otherwise
        """
        print("LaTeX Acronym Usage Checker")
        print("=" * 40)
        
        # Get defined acronyms
        defined_acronyms = self.find_defined_acronyms(acronym_file)
        if not defined_acronyms:
            print("No acronym definitions found. Exiting.")
            return False
        
        print(f"Found {len(defined_acronyms)} defined acronyms in '{acronym_file}'")
        
        # Get LaTeX files to check
        if latex_files is None:
            latex_files = self.get_latex_files(directory, recursive)
        
        if not latex_files:
            print("No LaTeX files found to check.")
            return False
        
        print(f"Checking {len(latex_files)} LaTeX files...")
        
        # Find used acronyms
        used_acronyms = self.find_used_acronyms(latex_files)
        
        # Analyze results
        defined_labels = set(defined_acronyms.keys())
        used_labels = set(used_acronyms.keys())
        
        missing_definitions = used_labels - defined_labels
        unused_definitions = defined_labels - used_labels
        
        # Report results
        print("\n" + "=" * 40)
        print("RESULTS")
        print("=" * 40)
        
        if missing_definitions:
            print(f"\n🔴 MISSING DEFINITIONS ({len(missing_definitions)}):")
            print("-" * 40)
            for label in sorted(missing_definitions):
                print(f"\nAcronym '{label}' is used but not defined:")
                for file_path, line_num in used_acronyms[label]:
                    print(f"  📁 {file_path}:{line_num}")
        else:
            print("\n✅ All used acronyms are properly defined!")
        
        if unused_definitions:
            print(f"\n🟡 UNUSED DEFINITIONS ({len(unused_definitions)}):")
            print("-" * 40)
            for label in sorted(unused_definitions):
                abbrev, desc = defined_acronyms[label]
                print(f"  '{label}' [{abbrev}] - {desc}")
        else:
            print("\n✅ All defined acronyms are being used!")
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"  • Defined acronyms: {len(defined_labels)}")
        print(f"  • Used acronyms: {len(used_labels)}")
        print(f"  • Missing definitions: {len(missing_definitions)}")
        print(f"  • Unused definitions: {len(unused_definitions)}")
        
        if missing_definitions:
            print(f"\n💡 TIP: Add these missing acronym definitions to '{acronym_file}':")
            for label in sorted(missing_definitions):
                print(f"  \\acro{{{label}}}[???]{{???}}")
        
        return True

class AcronymRemover:
    """Handles removal of unused LaTeX acronym definitions."""
    
    def __init__(self):
        # Reuse functionality from AcronymChecker
        self.checker = AcronymChecker()
    
    def remove_unused_acronyms(self, acronym_file: str, latex_files: List[str] = None, 
                              directory: str = ".", recursive: bool = True, 
                              dry_run: bool = False, backup: bool = True) -> bool:
        """
        Remove unused acronym definitions from the acronyms file.
        
        Args:
            acronym_file: Path to the acronyms definition file
            latex_files: Specific LaTeX files to check (if None, search directory)
            directory: Directory to search for LaTeX files
            recursive: Whether to search recursively
            dry_run: If True, only show what would be removed without making changes
            backup: If True, create a backup of the original file
            
        Returns:
            True if removal completed successfully, False otherwise
        """
        print("LaTeX Acronym Unused Definition Remover")
        print("=" * 40)
        
        # Get defined acronyms
        defined_acronyms = self.checker.find_defined_acronyms(acronym_file)
        if not defined_acronyms:
            print("No acronym definitions found. Exiting.")
            return False
        
        print(f"Found {len(defined_acronyms)} defined acronyms in '{acronym_file}'")
        
        # Get LaTeX files to check
        if latex_files is None:
            latex_files = self.checker.get_latex_files(directory, recursive)
        
        if not latex_files:
            print("No LaTeX files found to check.")
            return False
        
        print(f"Checking {len(latex_files)} LaTeX files...")
        
        # Find used acronyms
        used_acronyms = self.checker.find_used_acronyms(latex_files)
        
        # Analyze results
        defined_labels = set(defined_acronyms.keys())
        used_labels = set(used_acronyms.keys())
        unused_definitions = defined_labels - used_labels
        
        if not unused_definitions:
            print("\n✅ No unused acronym definitions found!")
            return True
        
        print(f"\n🔍 Found {len(unused_definitions)} unused acronym definitions:")
        print("-" * 40)
        for label in sorted(unused_definitions):
            abbrev, desc = defined_acronyms[label]
            print(f"  '{label}' [{abbrev}] - {desc}")
        
        if dry_run:
            print(f"\n🔬 DRY RUN MODE: No changes made to '{acronym_file}'")
            print("💡 Run without --dry-run to actually remove these definitions")
            return True
        
        # Read the original file
        try:
            with open(acronym_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading file: {e}")
            return False
        
        # Create backup if requested
        if backup:
            backup_file = f"{acronym_file}.backup"
            try:
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                print(f"📁 Backup created: {backup_file}")
            except Exception as e:
                print(f"Warning: Could not create backup: {e}")
        
        # Remove lines containing unused acronym definitions
        new_lines = []
        removed_count = 0
        
        for line in lines:
            # Check if this line contains an acronym definition
            match = re.match(r'\s*' + self.checker.definition_pattern, line)
            if match:
                label = match.group(1)
                if label in unused_definitions:
                    removed_count += 1
                    continue  # Skip this line (remove it)
            
            # Keep the line
            new_lines.append(line)
        
        # Write the modified content back to the file
        try:
            with open(acronym_file, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            print(f"\n✅ Successfully removed {removed_count} unused acronym definitions")
            print(f"📝 Removed acronyms:")
            for label in sorted(unused_definitions):
                abbrev, desc = defined_acronyms[label]
                print(f"   [{abbrev}] {desc}")
            
            # Final summary
            remaining_count = len(defined_labels) - len(unused_definitions)
            print(f"\n📊 SUMMARY:")
            print(f"  • Original definitions: {len(defined_labels)}")
            print(f"  • Removed definitions: {len(unused_definitions)}")
            print(f"  • Remaining definitions: {remaining_count}")
            
            return True
            
        except Exception as e:
            print(f"Error writing file: {e}")
            return False

def create_parser():
    """Create the argument parser for the acronyms tool."""
    parser = argparse.ArgumentParser(
        prog='acronyms',
        description="LaTeX Acronym Management Tool - Sort, check, and remove acronym definitions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sort acronyms alphabetically
  acronyms sort acronyms.tex
  acronyms sort acronyms.tex --output sorted_acronyms.tex
  
  # Check acronym usage
  acronyms check acronyms.tex
  acronyms check acronyms.tex --directory /path/to/latex/project
  acronyms check acronyms.tex --files chapter1.tex chapter2.tex
  acronyms check acronyms.tex --no-recursive
  
  # Remove unused acronym definitions
  acronyms remove acronyms.tex --dry-run
  acronyms remove acronyms.tex
  acronyms remove acronyms.tex --no-backup
  acronyms remove acronyms.tex --files chapter1.tex chapter2.tex
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Sort command
    sort_parser = subparsers.add_parser(
        'sort',
        help='Sort acronym definitions alphabetically by abbreviation'
    )
    sort_parser.add_argument(
        'input_file',
        help='LaTeX file containing acronym definitions'
    )
    sort_parser.add_argument(
        '--output', '-o',
        help='Output file (if not provided, overwrites input file)'
    )
    
    # Check command
    check_parser = subparsers.add_parser(
        'check',
        help='Check LaTeX files for acronym usage and find missing/unused definitions'
    )
    check_parser.add_argument(
        'acronym_file',
        help='LaTeX file containing acronym definitions'
    )
    check_parser.add_argument(
        '--files',
        nargs='+',
        help='Specific LaTeX files to check (if not provided, searches directory)'
    )
    check_parser.add_argument(
        '--directory',
        default='.',
        help='Directory to search for LaTeX files (default: current directory)'
    )
    check_parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not search subdirectories recursively'
    )
    
    # Remove command
    remove_parser = subparsers.add_parser(
        'remove',
        help='Remove unused acronym definitions from the acronyms file'
    )
    remove_parser.add_argument(
        'acronym_file',
        help='LaTeX file containing acronym definitions'
    )
    remove_parser.add_argument(
        '--files',
        nargs='+',
        help='Specific LaTeX files to check (if not provided, searches directory)'
    )
    remove_parser.add_argument(
        '--directory',
        default='.',
        help='Directory to search for LaTeX files (default: current directory)'
    )
    remove_parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not search subdirectories recursively'
    )
    remove_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be removed without making changes'
    )
    remove_parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not create a backup file before removing definitions'
    )
    
    return parser

def main():
    """Main function to handle command line arguments and execute commands."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'sort':
        sorter = AcronymSorter()
        success = sorter.sort_acronyms_in_file(args.input_file, args.output)
        sys.exit(0 if success else 1)
    
    elif args.command == 'check':
        checker = AcronymChecker()
        success = checker.check_acronyms(
            acronym_file=args.acronym_file,
            latex_files=args.files,
            directory=args.directory,
            recursive=not args.no_recursive
        )
        sys.exit(0 if success else 1)
    
    elif args.command == 'remove':
        remover = AcronymRemover()
        success = remover.remove_unused_acronyms(
            acronym_file=args.acronym_file,
            latex_files=args.files,
            directory=args.directory,
            recursive=not args.no_recursive,
            dry_run=args.dry_run,
            backup=not args.no_backup
        )
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

