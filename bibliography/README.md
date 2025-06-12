# LaTeX Bibliography Management Tool

A comprehensive Python tool for managing LaTeX bibliography files that provides four essential functionalities:
- **Check** bibliography usage and identify unused entries or missing citations
- **Remove** unused bibliography entries to keep .bib files clean
- **Verify** URL availability for web references and update access dates
- **Clean** comprehensive cleanup combining removal and verification

## Features

- 🔍 **Usage Analysis**: Finds unused bibliography entries and missing citations across your LaTeX project
- 🗑️ **Cleanup Tool**: Removes unused bibliography entries to keep files organized
- 🌐 **URL Verification**: Checks if website references are still accessible
- 📅 **Access Date Updates**: Automatically updates access dates for available URLs
- 📁 **Recursive Search**: Scans entire directory trees for LaTeX files
- 🎯 **Comprehensive Detection**: Supports all common citation commands (cite, natbib, biblatex)
- 📊 **Detailed Reports**: Clear summaries with file locations and availability status
- 🔒 **Safe Operations**: Automatic backups and dry-run mode for all modifications
- 🚀 **Batch Processing**: Clean command combines multiple operations efficiently

## Installation

1. **Download the script**:
   ```bash
   curl -O https://example.com/bibliography
   # or download the bibliography file directly
   ```

2. **Make it executable**:
   ```bash
   chmod +x bibliography
   ```

3. **Optional**: Move to your PATH for global access:
   ```bash
   sudo mv bibliography /usr/local/bin/
   ```

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library)
- Internet connection (for URL verification)

## Usage

### Basic Syntax
```bash
bibliography <command> [options] <file>
```

Available commands: `check`, `remove`, `verify`, `clean`

### Check Command

Analyze bibliography usage and find issues:

```bash
# Check all .tex files in current directory
bibliography check references.bib

# Check specific files
bibliography check references.bib --files chapter1.tex chapter2.tex main.tex

# Check files in a specific directory
bibliography check references.bib --directory /path/to/latex/project

# Search only current directory (no subdirectories)
bibliography check references.bib --no-recursive
```

### Remove Command

Remove unused bibliography entries to keep your files clean:

```bash
# Preview what would be removed (safe mode)
bibliography remove references.bib --dry-run

# Remove unused entries (creates backup automatically)
bibliography remove references.bib

# Remove without creating backup
bibliography remove references.bib --no-backup

# Remove based on specific files only
bibliography remove references.bib --files chapter1.tex chapter2.tex

# Remove based on specific directory
bibliography remove references.bib --directory /path/to/latex/project
```

### Verify Command

Check URL availability and update access dates:

```bash
# Verify URLs and update access dates
bibliography verify references.bib

# Only check availability without updating dates
bibliography verify references.bib --no-update-dates

# Custom timeout for URL checks
bibliography verify references.bib --timeout 5

# Verify without creating backup
bibliography verify references.bib --no-backup
```

### Clean Command

Comprehensive cleanup combining multiple operations:

```bash
# Full cleanup: remove unused entries + verify URLs
bibliography clean references.bib

# Clean specific files only
bibliography clean references.bib --files chapter1.tex chapter2.tex

# Clean without URL verification
bibliography clean references.bib --no-verify-urls

# Clean without removing unused entries
bibliography clean references.bib --no-remove-unused

# Clean without any backups
bibliography clean references.bib --no-backup
```

## Supported Citation Commands

The tool recognizes all common LaTeX citation commands:

### Standard LaTeX
| Command | Description |
|---------|-------------|
| `\cite{key}` | Basic citation |

### Natbib Package
| Command | Description |
|---------|-------------|
| `\citep{key}` | Parenthetical citation |
| `\citet{key}` | Textual citation |
| `\citealt{key}` | Alternative citation |
| `\citealp{key}` | Alternative parenthetical |
| `\citeauthor{key}` | Author only |
| `\citeyear{key}` | Year only |
| `\citeyearpar{key}` | Year in parentheses |

### BibLaTeX Package
| Command | Description |
|---------|-------------|
| `\autocite{key}` | Automatic citation |
| `\textcite{key}` | Text citation |
| `\parencite{key}` | Parenthetical citation |
| `\footcite{key}` | Footnote citation |
| `\fullcite{key}` | Full citation |

## Expected File Format

### BibTeX File Format

The tool expects standard BibTeX format:
```bibtex
@article{key1,
  title = {Sample Article Title},
  author = {John Doe and Jane Smith},
  journal = {Journal of Examples},
  year = {2023},
  volume = {10},
  pages = {1--20},
  url = {https://example.com/article}
}

@misc{key2,
  title = {Web Resource Title},
  author = {Web Author},
  year = {2023},
  howpublished = {\url{https://example.com/resource}},
  note = {Accessed: 2023-12-01}
}

@inproceedings{key3,
  title = {Conference Paper},
  author = {Conference Author},
  booktitle = {Proceedings of Example Conference},
  year = {2023},
  pages = {50--60}
}
```

### LaTeX Citation Usage

The tool scans any `.tex` files for citations:
```latex
\documentclass{article}
\usepackage{natbib}

\begin{document}
According to \citet{key1}, the methodology described in \citep{key2,key3} 
shows promising results. For more details, see \cite{key1}.

\bibliographystyle{plainnat}
\bibliography{references}
\end{document}
```

## Example Output

### Check Command Output
```
LaTeX Bibliography Usage Checker
========================================
Found 15 entries in bibliography file 'references.bib'
Checking 8 LaTeX files...

========================================
RESULTS
========================================

🔴 MISSING BIBLIOGRAPHY ENTRIES (2):

Citation 'smith2024' is used but not defined in bibliography:
  📁 chapter2.tex:45
  📁 conclusions.tex:12

Citation 'jones2023' is used but not defined in bibliography:
  📁 chapter3.tex:23

🟡 UNUSED BIBLIOGRAPHY ENTRIES (3):
  'obsolete2020' - Old Method for Data Analysis
    Author: Dr. Obsolete
  'unused2021' - Unused Reference Work
    Author: Never Cited
  'draft2022' - Work in Progress Paper
    Author: Still Writing

✅ All other citations have corresponding bibliography entries!

📊 SUMMARY:
  • Bibliography entries: 15
  • Unique citations: 12
  • Missing entries: 2
  • Unused entries: 3

💡 TIP: Add these missing bibliography entries to 'references.bib'
```

### Verify Command Output
```
LaTeX Bibliography URL Verifier
========================================
Found 8 entries with URLs
Checking URL availability...
  Checking example2023: https://example.com/research/article...
    ✅ Available (Status: 200)
  Checking web2022: https://oldsite.com/page...
    ❌ Not available (Error: HTTP Error 404: Not Found)
  Checking github2023: https://github.com/user/repo...
    ✅ Available (Status: 200)

📊 URL CHECK SUMMARY:
  • Total URLs checked: 8
  • Available URLs: 6
  • Unavailable URLs: 2

📁 Backup created: references.bib.backup

✅ Updated access dates for 6 entries
📅 Current date: 2023-12-15
```

### Clean Command Output
```
Step 1: Removing unused bibliography entries...
[... check and remove output ...]

Step 2: Verifying URL availability...
[... URL verification output ...]

🎉 Bibliography cleanup completed successfully!
```

## Common Use Cases

### 1. Pre-submission Check
```bash
# Ensure all citations are properly defined before submitting
bibliography check references.bib --directory ./manuscript
```

### 2. Periodic Maintenance
```bash
# Clean up bibliography file periodically
bibliography clean references.bib
```

### 3. URL Health Check
```bash
# Verify all web references are still accessible
bibliography verify references.bib
```

### 4. Large Project Management
```bash
# Check a complex project with multiple subdirectories
bibliography check references.bib --directory ./project-root
```

### 5. Collaborative Projects
```bash
# Check specific chapters before merging
bibliography check references.bib --files chapter1.tex chapter2.tex
```

### 6. Thesis/Dissertation Preparation
```bash
# Comprehensive cleanup before final submission
bibliography clean references.bib --timeout 15
```

## Troubleshooting

### Common Issues

**"No bibliography entries found"**
- Ensure your .bib file uses standard BibTeX format
- Check that entry keys are properly formatted
- Verify file encoding (should be UTF-8)

**"No LaTeX files found"**
- Verify you're in the correct directory
- Use `--directory` to specify the path to your LaTeX files
- Ensure files have `.tex` extension

**URL verification timeouts**
- Increase timeout with `--timeout` option
- Some sites may block automated requests
- Check your internet connection

**BibTeX parsing issues**
- The tool uses a simplified BibTeX parser
- Ensure proper braces `{}` or quotes `""` around field values
- Check for unbalanced braces in entries

### File Encoding
The tool expects UTF-8 encoded files. If you encounter encoding issues:
```bash
# Convert file to UTF-8 if needed
iconv -f ISO-8859-1 -t UTF-8 references.bib > references_utf8.bib
```

## Best Practices

1. **Regular Maintenance**: Run checks periodically during writing
2. **Use Dry-Run**: Always preview changes with `--dry-run` first
3. **Keep Backups**: Use version control for your bibliography files
4. **URL Maintenance**: Verify URLs before important submissions
5. **Consistent Format**: Maintain consistent BibTeX formatting
6. **Access Dates**: Keep access dates current for web references
7. **Organization**: Group related entries with comments in your .bib file

## Advanced Usage

### Automation Scripts
```bash
#!/bin/bash
# Daily bibliography maintenance script

echo "Running bibliography check..."
bibliography check references.bib

echo "Cleaning up unused entries..."
bibliography remove references.bib

echo "Verifying URLs weekly..."
if [ $(date +%u) -eq 1 ]; then  # Monday only
    bibliography verify references.bib
fi

echo "Bibliography maintenance complete!"
```

### Integration with LaTeX Workflow
```bash
# Pre-compilation check
bibliography check references.bib && pdflatex main.tex && bibtex main && pdflatex main.tex
```

## URL Field Recognition

The tool recognizes URLs in these BibTeX fields:
- `url = {https://example.com}`
- `howpublished = {\url{https://example.com}}`
- `howpublished = {Available at: https://example.com}`

## Access Date Format

When updating access dates, the tool:
- Uses ISO format: `YYYY-MM-DD`
- Updates existing `note` fields or creates new ones
- Preserves existing note content
- Format: `"Original note. Accessed: 2023-12-15"`

