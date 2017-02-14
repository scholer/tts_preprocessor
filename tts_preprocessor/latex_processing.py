
"""

Pre-process LaTeX files.



How to process:
* Regex processing
* Latex parsers


Python LaTeX parsers:
* Plastex, https://github.com/tiarno/plastex (actively maintained)  -- plasTeX SEEMS TO BE THE BETTER OPTION!
* * http://tiarno.github.io/plastex/tutorials/
* python-latex, https://github.com/omnidan/python-latex  (last update 2013)
* mbr's latex, https://github.com/mbr/latex (last update Oct 2016)
* pylatexenc, https://github.com/phfaist/pylatexenc  (March, 2016)

Latex converters:
* http://www.latex2html.org/, https://github.com/latex2html/latex2html/
* http://www.tug.org/applications/tex4ht/mn.html,
* http://hutchinson.belmont.ma.us/tth/
* Pandoc (not sure, but it probably can), e.g.
    $ pandoc -f latex -t plain -o OUTPUTFN inputfile
  pandoc is actually pretty impressive. It should probably be your first alternative to look at in the future.
  Although: Does not handle "unusual" macros very well, e.g. \SI



"""


from .common import substitute_patterns
from tts_preprocessor.pattern_utils import str_patterns_to_list, substitute_patterns
from .data import DEFAULT_TEX_PATTERNS


def substitute_latex(string, directives=None):
    if directives is None:
        directives = str_patterns_to_list(DEFAULT_TEX_PATTERNS)

    # Do latex-specific pre-processing:

    # Perform standard regex/string substitutions:
    string = substitute_patterns(string, directives)

    # Do latex-specific post-transformations:

    return string






