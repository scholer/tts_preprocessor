
"""

Pre-process LaTeX files.



How to process:
* Regex processing
* Latex parsers


Python LaTeX parsers:
* Plastex, https://github.com/tiarno/plastex (actively maintained)  -- plasTeX SEEMS TO BE THE BETTER OPTION!
*   http://tiarno.github.io/plastex/tutorials/
* pylatexenc, https://github.com/phfaist/pylatexenc  (March, 2016)
    "Python library for encoding unicode to latex and for parsing LaTeX to generate unicode text"
    That seems very close to what I'm trying to achieve!
* texsoup, https://github.com/alvinwan/texsoup
    "parses valid LaTeX and provides a variety of BeautifulSoup-esque methods and Pythonic
     idioms for iterating and searching the parse tree"
* tex2py, https://github.com/alvinwan/tex2py
    "converts LaTeX into a Python parse tree, allowing navigation using the default or a custom hierarchy"
    Uses texsoup library.
    Seems like a personal summer project; the PYPI package doesn't even install..
* texla, https://github.com/WikiToLearn/texla
    "A minimal and easily extensible LaTeX parser."
    Not even on PYPI...


Latex converters:
* http://www.latex2html.org/, https://github.com/latex2html/latex2html/
* http://www.tug.org/applications/tex4ht/mn.html,
* http://hutchinson.belmont.ma.us/tth/
* Pandoc, e.g.:
    $ pandoc -f latex -t plain -o OUTPUTFN inputfile
  pandoc is actually pretty impressive. It should probably be your first alternative to look at in the future.
  Although: Does not handle "unusual" macros very well, e.g. \SI
*

Other Python LaTeX packages:
* mbr's latex, last update Oct 2016
    For calling latex from python, i.e. compiling .tex --> .pdf.
    Can also be used to template .tex files before compiling.
    https://github.com/mbr/latex, http://pythonhosted.org/latex/
* python-latex, https://github.com/omnidan/python-latex  ("summer project", all commits from July 2013)
    "Python modules for LaTeX parsing and management"
* PlasTEX has a pretty extensive command line interface,
    http://tiarno.github.io/plastex/plastex/sect0002.html
    http://tiarno.github.io/plastex/tutorials/


General text-extractor packages:
* https://github.com/deanmalmgren/textract, http://textract.readthedocs.io/ (does not support latex, only html etc.)
*

Other interesting projects to extract plain-text words from files:
* https://pypi.python.org/pypi/SpeechRecognition/ (extract words from .wav files)


Using Pandoc:
-------------
Refs:
* http://pandoc.org/scripting.html
* http://pandoc.org/demos.html
* http://pandoc.org/MANUAL.html
*

Problems with Pandoc:
* Very focused on Markdown, HTML, and to some degree LaTeX..
* Custom commands may be truncated, e.g. ```\epigraph{...}```
    Maybe use ```--parse-raw``` command line flag?
* Also, Haskell is weird.

Pandoc libraries (for calling pandoc):
* pypandoc - https://github.com/bebraw/pypandoc - Also just builds command line commands for subprocess.Popen
* pyandoc (not `pypandoc`) - light wrapper for Pandoc (just builds command line commands...)

Writing Pandoc filters:
* To use a filter with pandoc:
    $ pandoc --filter=./myscript.py
* pandocfilters python package: https://github.com/jgm/pandocfilters, https://github.com/jgm/pandoc/wiki/Pandoc-Filters
* panflute: http://scorreia.com/software/panflute/guide.html


Using PlasTeX:
--------------
* Parses LaTeX to XML-like DOM, generates XHTML output by default.
* Templating using Zope Page Template (ZPT). Or templating of your own choice.
* http://tiarno.github.io/plastex/plastex/sect0001.html
* http://tiarno.github.io/plastex/tutorials/  - setup for command line usage
* http://tiarno.github.io/plastex/plastex/
* https://github.com/tiarno/plastex



Using TexSoup:
--------------

1. Go through each element and either (a) discard, (b) print or (c) template the content.
    It seems like this is exactly what PlasTEX is also doing. But plasTEX is SO TECHNICAL,
    it may be easier/faster to roll your own than to try and understand plasTEX.


Using pylatexenc:
-----------------

Pros:
* Seems good for converting \alpha to α.

Cons:
* Is not good for converting e.g. footnotes, citations, graphics elements, etc to TTS-prepared text.
    Well, you can, but you would need to update e.g. pylatexenc.latexwalker.default_macro_dict and other things.
* All macros and environments must be hard-coded (defined in pylatexenc.latexwalker).
    Other libs, e.g. TexSoup or plasTeX don't seem to have this requirement.
    Edit: It will capture all macros, but only determine macro args if the macro is defined in macro_dict.
* Very sparse documentation. And no command line interface??
    Seems more of a "special use" library than generic "latex-to-text" library. (Mentions "database indexing" a lot.)


* pylatexenc.latexwalker module has all building blocks for parsing tex source to DOM.
            .latexwalker.default_macro_dict defines macro elements.
            .latexencode module has constants and functions for utf8->latex.
            .latex2text  module has definitions and functions for latex->utf8
            .latex2text.default_macro_dict has
            .latex2text.default_env_dict
            .latex2text.default_text_replacements

Approach using pylatexenc:
0. First use something else to deal with special environments.
    Actually, pylatexenc can be used pretty flexibly. For instance, latex2text has classes EnvDef and MacroDef
    with attributes `simplify_repl` and `discard`, which can be used for more flexible filtering and conversion.
    `simplify_repl` can be a callable, a %-formatted string template, or just a string.
    However, everything still has to be hardcoded for pylatexenc to recognize the macro/environment.

1. Then use pylatexenc to convert latex character macros (e.g. \alpha) to unicode:
        First update `env_dict`, `macro_dict`, and `text_replacement` dicts starting from the default in `latex2text`.
        Use a generic input system to configure.
        (nodelist, tpos, tlen) = latexwalker.get_latex_nodes(
            content, keep_inline_math=False, tolerant_parsing=False)
        latex2text.LatexNodes2Text(
            env_dict=env_dict, macro_dict=macro_dict, text_replacements=text_replacements,
            keep_inline_math=False, keep_comments=False,
        ).nodelist_to_text(nodelist)
2. Finally use functions from standard text_processing module to convert utf8 to better-sounding words, as-needed.



Nomenclature:

`directive` is used to designate a (often named) method of transformation.
A `directive` may be:
    * A list of regular expression patterns and regex substitution patterns.
    * A named list of the above
    * A function, e.g.
    * A named function, e.g. `pylatexenc_convert`

"""

import os
import argparse
# import pylatexenc
import pylatexenc.latex2text
import pylatexenc.latexwalker


from .common import substitute_patterns
from tts_preprocessor.pattern_utils import str_patterns_to_list, substitute_patterns
from .data import DEFAULT_TEX_PATTERNS


def substitute_latex(string, directives=None):
    """"""
    if directives is None:
        directives = [str_patterns_to_list(DEFAULT_TEX_PATTERNS)]

    # Do latex-specific pre-processing:

    # Perform standard regex/string substitutions:
    string = substitute_patterns(string, directives)

    # Do latex-specific post-transformations:

    return string


def pylatexenc_convert(tex):  # , extra_env_defs=None, extra_macro_defs=None, extra_text_replacements=None):
    # from importlib import reload
    # reload(pylatexenc)
    # reload(pylatexenc.latexwalker)
    # reload(pylatexenc.latex2text)
    from pylatexenc.latex2text import EnvDef, MacroDef
    from pylatexenc.latexwalker import MacrosDef

    env_repr_dict = pylatexenc.latex2text.default_env_dict.copy()
    # if extra_env_defs:
    #     env_repr_dict.update(extra_env_defs)

    macro_repr_dict = pylatexenc.latex2text.default_macro_dict.copy()
    macro_repr_keys = ("macname", "simplify_repl", "discard")
    # Can't use string input, need to have True/False column.
    extra_macro_reprs = [ # """
        ("includegraphics",	None,			True),
        ("cite",		None,				True),
        ("footnote",	None,				True),

        ("chapter",		"\n\nChapter: %s\n",False),
        ("section",		"\nSection: %s\n",	False),
        ("subsection",	"\n%s:\n",			False),
        ("subsubsection","\n%s:\n",			False),
        ("paragraph",	"\n%s:",			False),
        ("caption",		"\nCaption: %s\n",	False),
        ("epigraph",	"\nQuote: %s\n",	False),

        ("%",			"percent",			False),
        ("percent",		"percent",			False),
        ("prime",		"prime",			False),
        ("degree",		"degree",			False),

        ("SI",			"%s %s",			False),
        ("SIrange",		"from %s to %s ",	False),
        # ("SIrange",		" from %s to %s ",	False),
        ("autoref",		"see reference: ",	False),
    ]
    greek = (
        'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa',
        'lambda', 'mu', 'nu', 'xi', 'omicron', 'pi', 'rho', 'sigma', 'tau', 'upsilon', 'phi',
        'chi', 'psi', 'omega')
    for letter in greek:
        extra_macro_reprs.append((letter, letter, False))
    # """
    # extra_macro_reprs = [
    #     line.replace('\\n', '\n').split("\t")
    #     for line in extra_macro_reprs.strip().split("\n")
    #     if line and line[0] != "#"
    # ]
    extra_macro_reprs = [dict(zip(macro_repr_keys, row)) for row in extra_macro_reprs]
    extra_macro_reprs = {d['macname']: MacroDef(**d) for d in extra_macro_reprs}
    macro_repr_dict.update(extra_macro_reprs)

    # Define the extra macros for latexwalker (to capture macro arguments):
    numargs = {
        "SI": 2,
        "SIrange": 2,
        "%": 0,
        "percent": 0,
    }
    extra_macro_defs = {
        macname: MacrosDef(macname=macname, optarg=True, numargs=numargs.get(macname, 1))
        for macname in extra_macro_reprs
    }
    macro_node_defs = pylatexenc.latexwalker.default_macro_dict  # .copy()
    macro_node_defs.update(extra_macro_defs)

    text_replacements = list(pylatexenc.latex2text.default_text_replacements)
    # Probably better to have these in separate file, unless regex.
    extra_text_replacements = [
        # (search, replace) tuple, regex or fixed-string, using regex.sub() or str.replace()
        # Mac TTS has problems when words contains hyphens; generally just replace hyphen with space or en-dash
        # ("-", "—"),
        ("-", " "),
        ("   ", " "),
        ("  ", " "),
        ("  ", " "),
        (" .", "."),
        (" , ", ", "),
        ("\n ", "\n"),

        ("3'", "3 prime"),
        ("5'", "5 prime"),
        ("2'", "2 prime"),
        ("5′", "5 prime"),
        ("3′", "3 prime"),
        ("2′", "2 prime"),
        ("T_m", "melting temperature"),
        ("%", "percent"),
        ("∼", "approximately"),
        (" nt", " nucleotide"),
        (" nts", " nucleotides"),
        ("et al.", "an co-workers"),
        ("e.g.", "for example"),
        ("i.e.", "that is,"),

        # Hyphens, etc:
        ("---", "—"),  # em-dash
        # ("--", "—"),  # en-dash
        ("--", "-"),  # hyphen

        # Other;
        ("°", " degree "),  # hyphen

        # Specialized:
        ("OH", "hydroxyl"),
        (" KL", " kissing loop"),
        (" MB", " molecular beacon"),
        (" bp", " base-pair"),
        (" kbp",  "kilo base pairs"),
        (" kb", " kilo bases"),
        ("K+", " potassium ions"),
        ("Na+", " sodium ions"),
        ("Mg2+", "magnesium"),
        ("Mg 2+", "magnesium"),

        ("G-quadruplex", "G quadruplex"),
        ("G-tetrad", "G tetrad"),
        ("G-tetrads", "G tetrads"),
        ("siRNA", "SI RNA"),  # space or hyphen
        ("dsRNA", "double stranded RNA"),  # space or hyphen
        ("dsDNA", "double stranded DNA"),  # space or hyphen
        # ("TALENs", "Ta-lens"),
        # 3,5-difluoro-4-hydroxybenzylidene

    ]
    if extra_text_replacements:
        text_replacements.extend(extra_text_replacements)

    parser = pylatexenc.latexwalker.LatexWalker(
        tex, macro_dict=macro_node_defs,
        keep_inline_math=False,  # True
        tolerant_parsing=False,
        strict_braces=False
    )
    (nodelist, tpos, tlen) = parser.get_latex_nodes(
        stop_upon_closing_brace=None,
        stop_upon_end_environment=None,
        stop_upon_closing_mathmode=None
    )

    # (nodelist, tpos, tlen) = pylatexenc.latexwalker.get_latex_nodes(
    #     tex, keep_inline_math=False, tolerant_parsing=False)

    text = pylatexenc.latex2text.LatexNodes2Text(
        env_dict=env_repr_dict,
        macro_dict=macro_repr_dict,
        text_replacements=text_replacements,
        keep_inline_math=False,  # False = "replace $ with ' '"
        keep_comments=False,
    ).nodelist_to_text(nodelist, sep=" ")
    return text


def main():

    ap = argparse.ArgumentParser()
    ap.add_argument('texfile', nargs="+")
    ap.add_argument('-o', '--outputfnfmt', default="{texfile}.txt")
    ap.add_argument('--input-encoding', default="utf-8")

    argns = ap.parse_args()

    for file in argns.texfile:
        print("\nReading tex from file:", file)
        try:
            with open(file, encoding=argns.input_encoding) as fp:
                tex = fp.read()
        except IOError as e:
            print(e.__class__.__name__, e, " - skipping this file...")
            continue
        try:
            text = pylatexenc_convert(tex)
        except pylatexenc.latexwalker.LatexWalkerParseError as e:
            print(e.__class__.__name__, e)
            print(" - skipping this file (%s)..." % (file,))
            continue
        outputfile = argns.outputfnfmt.format(texfile=file, inputfn=file, ext=".txt")
        with open(outputfile, "w") as fp:
            fp.write(text)
        print("Text written to file:", os.path.abspath(outputfile))


if __name__ == '__main__':
    main()
