# thesis-scripts

## `sorted_acronyms.py`
This script helps you keep your list of acronyms in LaTeX clean and well-organized by sorting them alphabetically based on their acronym keys.

### Use Case
Assume you have a LaTeX file `acronyms.tex` containing an unsorted list of acronyms inside an acronym environment, like so:

```TeX
\begin{acronym}[XXXXXXX]

\acro{rq}[RQ]{Research Question}
\acro{dpia}[DPIA]{Data Protection Impact Assessment}
\acro{uml}[UML]{Unified Modeling Language}
\acro{dsl}[DSL]{Domain-specific Language}
\acro{dsr}[DSR]{Design Research}
\acro{mde}[MDE]{Model-driven Engineering}
\acro{pbd}[PbD]{Privacy-by-Design}
\acro{gdpr}[GDPR]{General Data Protection Regulation}

\end{acronym}
```

To sort the acronyms alphabetically by their key (rq, dpia, uml, etc.), run the script:

```bash
$ python sorted_acronyms.py acronyms.tex
```
Make sure only the intended acronyms are present in the file or within the same environment block, as all matching `\acro{}` lines will be sorted regardless of their position.

### Requirements
- Python 3.6+
- No external dependencies

### Notes
- The script assumes all `\acro{}` entries are located within a single acronym environment in the file.
- The sorting is case-insensitive and based on the acronym key used in `\acro{...}`.

## License
This repository is licensed under the MIT License.

## Contributions
Contributions are welcome! Feel free to submit scripts that simplify or enhance LaTeX workflows.

