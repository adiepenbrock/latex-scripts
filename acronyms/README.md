# LaTeX Acronym Management Tool

A comprehensive Python tool for managing LaTeX acronyms that provides two essential functionalities:
- **Sort** acronym definitions alphabetically by their abbreviations
- **Check** LaTeX files for acronym usage and identify missing or unused definitions
- **Remove** unused acronym definitions to keep your files clean

## Features

- ✅ **Alphabetical Sorting**: Automatically sorts acronym definitions by abbreviation
- 🔍 **Usage Analysis**: Finds missing definitions and unused acronyms across your LaTeX project
- 🗑️ **Cleanup Tool**: Removes unused acronym definitions to keep files organized
- 📁 **Recursive Search**: Scans entire directory trees for LaTeX files
- 🎯 **Comprehensive Detection**: Supports all common acronym package commands
- 📊 **Detailed Reports**: Clear summaries with file locations and line numbers
- 🛠️ **Flexible Output**: Sort in-place or to new files
- 🔒 **Safe Operations**: Automatic backups and dry-run mode for removals

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library)

## Usage

### Basic Syntax
```bash
acronyms <command> [options] <file>
```

### Sort Command

Sort acronym definitions alphabetically by their abbreviations:

```bash
# Sort acronyms in place
acronyms sort acronyms.tex

# Sort to a new file
acronyms sort acronyms.tex --output sorted_acronyms.tex
```

**Example**:
```latex
% Before sorting
\acro{xml}[XML]{Extensible Markup Language}
\acro{api}[API]{Application Programming Interface}
\acro{cpu}[CPU]{Central Processing Unit}

% After sorting
\acro{api}[API]{Application Programming Interface}
\acro{cpu}[CPU]{Central Processing Unit}
\acro{xml}[XML]{Extensible Markup Language}
```

### Check Command

Analyze LaTeX files for acronym usage and find issues:

```bash
# Check all .tex files in current directory
acronyms check acronyms.tex

# Check specific files
acronyms check acronyms.tex --files chapter1.tex chapter2.tex main.tex

# Check files in a specific directory
acronyms check acronyms.tex --directory /path/to/latex/project

# Search only current directory (no subdirectories)
acronyms check acronyms.tex --no-recursive
```

### Remove Command

Remove unused acronym definitions to keep your files clean:

```bash
# Preview what would be removed (safe mode)
acronyms remove acronyms.tex --dry-run

# Remove unused definitions (creates backup automatically)
acronyms remove acronyms.tex

# Remove without creating backup
acronyms remove acronyms.tex --no-backup

# Remove based on specific files only
acronyms remove acronyms.tex --files chapter1.tex chapter2.tex

# Remove based on specific directory
acronyms remove acronyms.tex --directory /path/to/latex/project
```

#### Safety Features:

- **Automatic Backup**: Creates `.backup` file before making changes
- **Dry Run Mode**: Preview changes with `--dry-run` before committing
- **Detailed Reporting**: Shows exactly what will be or was removed

## Supported Acronym Commands

The tool recognizes all common LaTeX acronym package commands:

| Command | Description |
|---------|-------------|
| `\ac{label}` | Standard acronym |
| `\acp{label}` | Plural form |
| `\acs{label}` | Short form only |
| `\acl{label}` | Long form only |
| `\acf{label}` | Full form (short + long) |
| `\Ac{label}` | Capitalized version |
| `\acrshort{label}` | Short form (alternative) |
| `\acrlong{label}` | Long form (alternative) |
| `\acrfull{label}` | Full form (alternative) |

## Expected File Format

### Acronym Definition File

The tool expects acronym definitions in this format:
```latex
\acro{label}[ABBREV]{Full Description}
```

**Example `acronyms.tex`**:
```latex
% Network and Internet
\acro{api}[API]{Application Programming Interface}
\acro{dns}[DNS]{Domain Name System}
\acro{http}[HTTP]{Hypertext Transfer Protocol}
\acro{url}[URL]{Uniform Resource Locator}

% Computing
\acro{cpu}[CPU]{Central Processing Unit}
\acro{gpu}[GPU]{Graphics Processing Unit}
\acro{ram}[RAM]{Random Access Memory}
\acro{ssd}[SSD]{Solid State Drive}
```

### LaTeX Usage Files

The tool scans any `.tex` files for acronym usage:
```latex
\documentclass{article}
\usepackage{acronym}

\begin{document}
The \ac{api} allows communication between different software components.
When using \acp{url}, ensure they follow \ac{http} standards.
\end{document}
```

## Example Output

### Sort Command Output
```
✅ Successfully sorted 12 acronym entries.
📝 Sorted order:
   API: Application Programming Interface
   CPU: Central Processing Unit
   DNS: Domain Name System
   GPU: Graphics Processing Unit
   HTTP: Hypertext Transfer Protocol
   RAM: Random Access Memory
   SSD: Solid State Drive
   URL: Uniform Resource Locator
```

### Check Command Output
```
LaTeX Acronym Usage Checker
========================================
Found 8 defined acronyms in 'acronyms.tex'
Checking 5 LaTeX files...

========================================
RESULTS
========================================

🔴 MISSING DEFINITIONS (2):

Acronym 'json' is used but not defined:
  📁 chapter2.tex:45
  📁 appendix.tex:12

Acronym 'rest' is used but not defined:
  📁 chapter3.tex:23

🟡 UNUSED DEFINITIONS (1):
  'obsolete' [OBS] - Obsolete Technology

✅ All other acronyms are properly defined and used!

📊 SUMMARY:
  • Defined acronyms: 8
  • Used acronyms: 7
  • Missing definitions: 2
  • Unused definitions: 1

💡 TIP: Add these missing acronym definitions to 'acronyms.tex':
  \acro{json}[???]{???}
  \acro{rest}[???]{???}
```

### Remove Command Output
```
LaTeX Acronym Unused Definition Remover
========================================
Found 8 defined acronyms in 'acronyms.tex'
Checking 5 LaTeX files...

🔍 Found 2 unused acronym definitions:
----------------------------------------
  'legacy' [LEG] - Legacy System Protocol
  'obsolete' [OBS] - Obsolete Technology

📁 Backup created: acronyms.tex.backup

✅ Successfully removed 2 unused acronym definitions
📝 Removed acronyms:
   [LEG] Legacy System Protocol
   [OBS] Obsolete Technology

📊 SUMMARY:
  • Original definitions: 8
  • Removed definitions: 2
  • Remaining definitions: 6
```

## Common Use Cases

### 1. Clean Up Acronym Definitions
```bash
# Sort your acronyms file for better organization
acronyms sort acronyms.tex
```

### 2. Pre-submission Check
```bash
# Ensure all acronyms are properly defined before submitting
acronyms check acronyms.tex --directory ./manuscript
```

### 3. Large Project Management
```bash
# Check a complex project with multiple subdirectories
acronyms check definitions/acronyms.tex --directory ./project-root
```

### 4. Specific File Analysis
```bash
# Check only specific chapters or sections
acronyms check acronyms.tex --files intro.tex methods.tex results.tex
```
### 5. Cleanup and Maintenance
```bash
# Preview what unused definitions would be removed
acronyms remove acronyms.tex --dry-run

# Clean up unused definitions after project completion
acronyms remove acronyms.tex

# Sort and clean up in one workflow
acronyms sort acronyms.tex
acronyms remove acronyms.tex
```

## Troubleshooting

### Common Issues

**"No acronym entries found"**
- Ensure your file uses the correct format: `\acro{label}[ABBREV]{Description}`
- Check that the file path is correct

**"No LaTeX files found"**
- Verify you're in the correct directory
- Use `--directory` to specify the path to your LaTeX files
- Ensure files have `.tex` extension

**"File not found" errors**
- Check file paths and permissions
- Ensure the acronym definition file exists

### File Encoding
The tool expects UTF-8 encoded files. If you encounter encoding issues:
```bash
# Convert file to UTF-8 if needed
iconv -f ISO-8859-1 -t UTF-8 acronyms.tex > acronyms_utf8.tex
```

## Best Practices

1. **Consistent Naming**: Use clear, descriptive labels for acronyms
2. **Regular Sorting**: Sort your acronyms file periodically for better organization
3. **Project-wide Checks**: Run usage checks before important milestones
4. **Version Control**: Keep your acronyms file under version control
5. **Documentation**: Include comments in your acronyms file to organize categories

## Integration with LaTeX

### Basic Setup
```latex
\usepackage{acronym}
\input{acronyms}  % Include your acronym definitions
```

### Usage in Document
```latex
% First use shows full form
The \ac{api} is essential...

% Subsequent uses show only abbreviation
We'll use the \ac{api} throughout...

% Force full form
The \acf{api} specification...

% Plural forms
Multiple \acp{api} are available...
```
