#!/usr/bin/env python3
"""
LaTeX Bibliography Management Tool

This script provides comprehensive bibliography management functionalities:
1. Check for unused references in .bib files and missing citations in .tex files
2. Remove unused bibliography entries to keep files clean
3. Verify URL availability for web references and update access dates
4. Comprehensive cleanup combining multiple operations
"""

import re
import os
import sys
import glob
import argparse
import urllib.request
import urllib.error
from datetime import datetime
from typing import Set, Dict, List, Tuple, Optional
from pathlib import Path

class BibliographyParser:
    """Handles parsing of BibTeX files and LaTeX citation commands."""
    
    def __init__(self):
        # Common citation commands in LaTeX
        self.citation_patterns = [
            r'\\cite\{([^}]+)\}',           # \cite{key}
            r'\\citep\{([^}]+)\}',          # \citep{key} (natbib)
            r'\\citet\{([^}]+)\}',          # \citet{key} (natbib)
            r'\\citealt\{([^}]+)\}',        # \citealt{key} (natbib)
            r'\\citealp\{([^}]+)\}',        # \citealp{key} (natbib)
            r'\\citeauthor\{([^}]+)\}',     # \citeauthor{key} (natbib)
            r'\\citeyear\{([^}]+)\}',       # \citeyear{key} (natbib)
            r'\\citeyearpar\{([^}]+)\}',    # \citeyearpar{key} (natbib)
            r'\\Cite\{([^}]+)\}',           # \Cite{key} (capitalized)
            r'\\Citep\{([^}]+)\}',          # \Citep{key} (capitalized)
            r'\\Citet\{([^}]+)\}',          # \Citet{key} (capitalized)
            r'\\autocite\{([^}]+)\}',       # \autocite{key} (biblatex)
            r'\\textcite\{([^}]+)\}',       # \textcite{key} (biblatex)
            r'\\parencite\{([^}]+)\}',      # \parencite{key} (biblatex)
            r'\\footcite\{([^}]+)\}',       # \footcite{key} (biblatex)
            r'\\fullcite\{([^}]+)\}',       # \fullcite{key} (biblatex)
        ]
    
    def parse_bib_file(self, bib_file: str) -> Dict[str, Dict[str, str]]:
        """
        Parse a BibTeX file and extract all entries.
        
        Args:
            bib_file: Path to the .bib file
            
        Returns:
            Dictionary mapping entry_key -> {field: value, ...}
        """
        entries = {}
        
        try:
            with open(bib_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: Bibliography file '{bib_file}' not found.")
            return {}
        except Exception as e:
            print(f"Error reading bibliography file: {e}")
            return {}
        
        # Pattern to match BibTeX entries
        # This is a simplified parser - for production use, consider using a proper BibTeX parser
        entry_pattern = r'@(\w+)\s*\{\s*([^,\s]+)\s*,\s*(.*?)\n\}'
        
        # Find all entries
        matches = re.finditer(entry_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            entry_type = match.group(1).lower()
            entry_key = match.group(2)
            fields_text = match.group(3)
            
            # Parse fields within the entry
            fields = {'entry_type': entry_type}
            
            # Simple field extraction (field = {value} or field = "value")
            field_pattern = r'(\w+)\s*=\s*[{"](.*?)["}](?:\s*,|\s*$)'
            field_matches = re.finditer(field_pattern, fields_text, re.DOTALL)
            
            for field_match in field_matches:
                field_name = field_match.group(1).lower()
                field_value = field_match.group(2).strip()
                fields[field_name] = field_value
            
            entries[entry_key] = fields
        
        return entries
    
    def find_citations_in_files(self, tex_files: List[str]) -> Dict[str, List[Tuple[str, int]]]:
        """
        Find all citations in LaTeX files.
        
        Args:
            tex_files: List of LaTeX file paths to check
            
        Returns:
            Dictionary mapping citation_key -> [(filename, line_number), ...]
        """
        citations = {}
        
        for file_path in tex_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except Exception as e:
                print(f"Warning: Could not read file '{file_path}': {e}")
                continue
            
            for line_num, line in enumerate(lines, 1):
                # Check each citation pattern
                for pattern in self.citation_patterns:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        # Handle multiple citations in one command (e.g., \cite{key1,key2,key3})
                        keys_string = match.group(1)
                        citation_keys = [key.strip() for key in keys_string.split(',')]
                        
                        for key in citation_keys:
                            if key:  # Skip empty keys
                                if key not in citations:
                                    citations[key] = []
                                citations[key].append((file_path, line_num))
        
        return citations
    
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

class BibliographyChecker:
    """Handles checking of bibliography usage and consistency."""
    
    def __init__(self):
        self.parser = BibliographyParser()
    
    def check_bibliography(self, bib_file: str, tex_files: List[str] = None, 
                          directory: str = ".", recursive: bool = True) -> Tuple[Set[str], Set[str]]:
        """
        Check bibliography usage and find unused/missing references.
        
        Args:
            bib_file: Path to the .bib file
            tex_files: Specific LaTeX files to check (if None, search directory)
            directory: Directory to search for LaTeX files
            recursive: Whether to search recursively
            
        Returns:
            Tuple of (unused_entries, missing_entries)
        """
        print("LaTeX Bibliography Usage Checker")
        print("=" * 40)
        
        # Parse bibliography file
        bib_entries = self.parser.parse_bib_file(bib_file)
        if not bib_entries:
            print("No bibliography entries found. Exiting.")
            return set(), set()
        
        print(f"Found {len(bib_entries)} entries in bibliography file '{bib_file}'")
        
        # Get LaTeX files to check
        if tex_files is None:
            tex_files = self.parser.get_latex_files(directory, recursive)
        
        if not tex_files:
            print("No LaTeX files found to check.")
            return set(), set()
        
        print(f"Checking {len(tex_files)} LaTeX files...")
        
        # Find citations
        citations = self.parser.find_citations_in_files(tex_files)
        
        # Analyze results
        defined_keys = set(bib_entries.keys())
        cited_keys = set(citations.keys())
        
        unused_entries = defined_keys - cited_keys
        missing_entries = cited_keys - defined_keys
        
        # Report results
        print("\n" + "=" * 40)
        print("RESULTS")
        print("=" * 40)
        
        if missing_entries:
            print(f"\n🔴 MISSING BIBLIOGRAPHY ENTRIES ({len(missing_entries)}):")
            print("-" * 40)
            for key in sorted(missing_entries):
                print(f"\nCitation '{key}' is used but not defined in bibliography:")
                for file_path, line_num in citations[key]:
                    print(f"  📁 {file_path}:{line_num}")
        else:
            print("\n✅ All citations have corresponding bibliography entries!")
        
        if unused_entries:
            print(f"\n🟡 UNUSED BIBLIOGRAPHY ENTRIES ({len(unused_entries)}):")
            print("-" * 40)
            for key in sorted(unused_entries):
                entry = bib_entries[key]
                title = entry.get('title', 'No title')
                author = entry.get('author', 'No author')
                print(f"  '{key}' - {title[:50]}{'...' if len(title) > 50 else ''}")
                print(f"    Author: {author}")
        else:
            print("\n✅ All bibliography entries are being cited!")
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"  • Bibliography entries: {len(defined_keys)}")
        print(f"  • Unique citations: {len(cited_keys)}")
        print(f"  • Missing entries: {len(missing_entries)}")
        print(f"  • Unused entries: {len(unused_entries)}")
        
        if missing_entries:
            print(f"\n💡 TIP: Add these missing bibliography entries to '{bib_file}'")
        
        return unused_entries, missing_entries

class BibliographyRemover:
    """Handles removal of unused bibliography entries."""
    
    def __init__(self):
        self.checker = BibliographyChecker()
    
    def remove_unused_entries(self, bib_file: str, tex_files: List[str] = None, 
                             directory: str = ".", recursive: bool = True, 
                             dry_run: bool = False, backup: bool = True) -> bool:
        """
        Remove unused bibliography entries from the .bib file.
        
        Args:
            bib_file: Path to the .bib file
            tex_files: Specific LaTeX files to check (if None, search directory)
            directory: Directory to search for LaTeX files
            recursive: Whether to search recursively
            dry_run: If True, only show what would be removed without making changes
            backup: If True, create a backup of the original file
            
        Returns:
            True if removal completed successfully, False otherwise
        """
        print("LaTeX Bibliography Unused Entry Remover")
        print("=" * 40)
        
        # Find unused entries
        unused_entries, missing_entries = self.checker.check_bibliography(
            bib_file, tex_files, directory, recursive
        )
        
        if not unused_entries:
            print("\n✅ No unused bibliography entries found!")
            return True
        
        if dry_run:
            print(f"\n🔬 DRY RUN MODE: No changes made to '{bib_file}'")
            print("💡 Run without --dry-run to actually remove these entries")
            return True
        
        # Read the original file
        try:
            with open(bib_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return False
        
        # Create backup if requested
        if backup:
            backup_file = f"{bib_file}.backup"
            try:
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"📁 Backup created: {backup_file}")
            except Exception as e:
                print(f"Warning: Could not create backup: {e}")
        
        # Remove unused entries
        for key in unused_entries:
            # Pattern to match the entire entry
            entry_pattern = rf'@\w+\s*\{{\s*{re.escape(key)}\s*,.*?\n\}}'
            content = re.sub(entry_pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Write the modified content back
        try:
            with open(bib_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"\n✅ Successfully removed {len(unused_entries)} unused bibliography entries")
            print(f"📝 Removed entries:")
            for key in sorted(unused_entries):
                print(f"   {key}")
            
            return True
            
        except Exception as e:
            print(f"Error writing file: {e}")
            return False

class URLVerifier:
    """Handles verification of URLs in bibliography entries."""
    
    def __init__(self):
        self.parser = BibliographyParser()
    
    def check_url_availability(self, url: str, timeout: int = 10) -> Tuple[bool, int, str]:
        """
        Check if a URL is accessible.
        
        Args:
            url: URL to check
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (is_available, status_code, error_message)
        """
        try:
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            request = urllib.request.Request(url)
            request.add_header('User-Agent', 'Mozilla/5.0 (Bibliography Checker)')
            
            with urllib.request.urlopen(request, timeout=timeout) as response:
                status_code = response.getcode()
                return True, status_code, ""
                
        except urllib.error.HTTPError as e:
            return False, e.code, str(e)
        except urllib.error.URLError as e:
            return False, 0, str(e)
        except Exception as e:
            return False, 0, str(e)
    
    def verify_urls(self, bib_file: str, update_dates: bool = True, 
                   backup: bool = True, timeout: int = 10) -> bool:
        """
        Verify URLs in bibliography entries and optionally update access dates.
        
        Args:
            bib_file: Path to the .bib file
            update_dates: If True, update note fields with current access date
            backup: If True, create a backup of the original file
            timeout: Timeout for URL checks in seconds
            
        Returns:
            True if verification completed successfully, False otherwise
        """
        print("LaTeX Bibliography URL Verifier")
        print("=" * 40)
        
        # Parse bibliography file
        bib_entries = self.parser.parse_bib_file(bib_file)
        if not bib_entries:
            print("No bibliography entries found. Exiting.")
            return False
        
        # Find entries with URLs
        url_entries = {}
        for key, entry in bib_entries.items():
            url = entry.get('url') or entry.get('howpublished', '')
            if url and ('http' in url or 'www.' in url):
                # Extract URL from howpublished field if needed
                if 'howpublished' in entry and 'url' not in entry:
                    url_match = re.search(r'https?://[^\s\}]+|www\.[^\s\}]+', url)
                    if url_match:
                        url = url_match.group()
                url_entries[key] = url
        
        if not url_entries:
            print("No URLs found in bibliography entries.")
            return True
        
        print(f"Found {len(url_entries)} entries with URLs")
        print("Checking URL availability...")
        
        # Check each URL
        results = {}
        available_count = 0
        
        for key, url in url_entries.items():
            print(f"  Checking {key}: {url[:60]}{'...' if len(url) > 60 else ''}")
            is_available, status_code, error = self.check_url_availability(url, timeout)
            results[key] = (is_available, status_code, error, url)
            
            if is_available:
                available_count += 1
                print(f"    ✅ Available (Status: {status_code})")
            else:
                print(f"    ❌ Not available (Error: {error})")
        
        # Report results
        print(f"\n📊 URL CHECK SUMMARY:")
        print(f"  • Total URLs checked: {len(url_entries)}")
        print(f"  • Available URLs: {available_count}")
        print(f"  • Unavailable URLs: {len(url_entries) - available_count}")
        
        # Update dates if requested
        if update_dates and available_count > 0:
            return self._update_access_dates(bib_file, results, backup)
        
        return True
    
    def _update_access_dates(self, bib_file: str, results: Dict, backup: bool) -> bool:
        """Update access dates for available URLs."""
        try:
            with open(bib_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return False
        
        # Create backup if requested
        if backup:
            backup_file = f"{bib_file}.backup"
            try:
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"📁 Backup created: {backup_file}")
            except Exception as e:
                print(f"Warning: Could not create backup: {e}")
        
        # Update entries with access dates
        current_date = datetime.now().strftime("%Y-%m-%d")
        updated_count = 0
        
        for key, (is_available, status_code, error, url) in results.items():
            if is_available:
                # Find the entry and update/add note field
                entry_pattern = rf'(@\w+\s*\{{\s*{re.escape(key)}\s*,.*?)\n\}}'
                
                def update_entry(match):
                    nonlocal updated_count
                    entry_content = match.group(1)
                    
                    # Check if note field exists
                    note_pattern = r'note\s*=\s*[{"](.*?)["}]'
                    note_match = re.search(note_pattern, entry_content, re.IGNORECASE | re.DOTALL)
                    
                    access_info = f"Accessed: {current_date}"
                    
                    if note_match:
                        # Update existing note
                        existing_note = note_match.group(1)
                        # Remove old access date if present
                        cleaned_note = re.sub(r'Accessed:\s*\d{4}-\d{2}-\d{2}', '', existing_note).strip()
                        if cleaned_note:
                            new_note = f"{cleaned_note}. {access_info}"
                        else:
                            new_note = access_info
                        entry_content = re.sub(note_pattern, f'note = "{{{new_note}}}"', entry_content, flags=re.IGNORECASE)
                    else:
                        # Add new note field
                        entry_content += f',\n  note = "{{{access_info}}}"'
                    
                    updated_count += 1
                    return entry_content + '\n}'
                
                content = re.sub(entry_pattern, update_entry, content, flags=re.DOTALL | re.IGNORECASE)
        
        # Write updated content
        try:
            with open(bib_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"\n✅ Updated access dates for {updated_count} entries")
            print(f"📅 Current date: {current_date}")
            
            return True
            
        except Exception as e:
            print(f"Error writing file: {e}")
            return False

def create_parser():
    """Create the argument parser for the bibliography tool."""
    parser = argparse.ArgumentParser(
        prog='bibliography',
        description="LaTeX Bibliography Management Tool - Check, clean, and verify bibliography entries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check bibliography usage
  bibliography check references.bib
  bibliography check references.bib --directory /path/to/latex/project
  bibliography check references.bib --files chapter1.tex chapter2.tex
  
  # Remove unused bibliography entries
  bibliography remove references.bib --dry-run
  bibliography remove references.bib
  bibliography remove references.bib --no-backup
  
  # Verify URL availability and update access dates
  bibliography verify references.bib
  bibliography verify references.bib --no-update-dates
  bibliography verify references.bib --timeout 5
  
  # Comprehensive cleanup
  bibliography clean references.bib
  bibliography clean references.bib --no-verify-urls
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Check command
    check_parser = subparsers.add_parser(
        'check',
        help='Check bibliography usage and find unused/missing entries'
    )
    check_parser.add_argument(
        'bib_file',
        help='BibTeX file containing bibliography entries'
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
        help='Remove unused bibliography entries from the .bib file'
    )
    remove_parser.add_argument(
        'bib_file',
        help='BibTeX file containing bibliography entries'
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
        help='Do not create a backup file before removing entries'
    )
    
    # Verify command
    verify_parser = subparsers.add_parser(
        'verify',
        help='Verify URL availability and update access dates'
    )
    verify_parser.add_argument(
        'bib_file',
        help='BibTeX file containing bibliography entries'
    )
    verify_parser.add_argument(
        '--no-update-dates',
        action='store_true',
        help='Do not update access dates for available URLs'
    )
    verify_parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not create a backup file before updating entries'
    )
    verify_parser.add_argument(
        '--timeout',
        type=int,
        default=10,
        help='Timeout for URL checks in seconds (default: 10)'
    )
    
    # Clean command (comprehensive)
    clean_parser = subparsers.add_parser(
        'clean',
        help='Comprehensive cleanup: remove unused entries and verify URLs'
    )
    clean_parser.add_argument(
        'bib_file',
        help='BibTeX file containing bibliography entries'
    )
    clean_parser.add_argument(
        '--files',
        nargs='+',
        help='Specific LaTeX files to check (if not provided, searches directory)'
    )
    clean_parser.add_argument(
        '--directory',
        default='.',
        help='Directory to search for LaTeX files (default: current directory)'
    )
    clean_parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not search subdirectories recursively'
    )
    clean_parser.add_argument(
        '--no-remove-unused',
        action='store_true',
        help='Do not remove unused bibliography entries'
    )
    clean_parser.add_argument(
        '--no-verify-urls',
        action='store_true',
        help='Do not verify URL availability'
    )
    clean_parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not create backup files'
    )
    clean_parser.add_argument(
        '--timeout',
        type=int,
        default=10,
        help='Timeout for URL checks in seconds (default: 10)'
    )
    
    return parser

def main():
    """Main function to handle command line arguments and execute commands."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'check':
        checker = BibliographyChecker()
        unused, missing = checker.check_bibliography(
            bib_file=args.bib_file,
            tex_files=args.files,
            directory=args.directory,
            recursive=not args.no_recursive
        )
        # Exit with error code if there are issues
        sys.exit(0 if not unused and not missing else 1)
    
    elif args.command == 'remove':
        remover = BibliographyRemover()
        success = remover.remove_unused_entries(
            bib_file=args.bib_file,
            tex_files=args.files,
            directory=args.directory,
            recursive=not args.no_recursive,
            dry_run=args.dry_run,
            backup=not args.no_backup
        )
        sys.exit(0 if success else 1)
    
    elif args.command == 'verify':
        verifier = URLVerifier()
        success = verifier.verify_urls(
            bib_file=args.bib_file,
            update_dates=not args.no_update_dates,
            backup=not args.no_backup,
            timeout=args.timeout
        )
        sys.exit(0 if success else 1)
    
    elif args.command == 'clean':
        success = True
        
        # Remove unused entries if requested
        if not args.no_remove_unused:
            print("Step 1: Removing unused bibliography entries...")
            remover = BibliographyRemover()
            success &= remover.remove_unused_entries(
                bib_file=args.bib_file,
                tex_files=args.files,
                directory=args.directory,
                recursive=not args.no_recursive,
                dry_run=False,
                backup=not args.no_backup
            )
            print()
        
        # Verify URLs if requested
        if not args.no_verify_urls and success:
            print("Step 2: Verifying URL availability...")
            verifier = URLVerifier()
            success &= verifier.verify_urls(
                bib_file=args.bib_file,
                update_dates=True,
                backup=not args.no_backup,
                timeout=args.timeout
            )
        
        if success:
            print("\n🎉 Bibliography cleanup completed successfully!")
        else:
            print("\n❌ Bibliography cleanup completed with errors.")
        
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
