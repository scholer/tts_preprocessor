"""

Nomenclature:
-------------

Directive name: Name of a directive, e.g. 'latex_to_text'

Op / operation: A single operation, e.g. a substitution operation defined by a ReplacementTuple.
    Directive ops include:
        * Substitutions (regex or fixed-string)

Directive def: The full sequence of operations defining a directive, e.g. a list of ReplacementTuples.
    Wait, isn't it easier to just call this "directive ops" (plural)? I.e. a list of operations?

Transformation, directive transform: the functional expression/implementation of a directive, e.g.
    function(text) --> transformed_text


Obsolete nomenclature / not used:
* Directive group: Old name for "directive def", group because it has multiple "operations".
* subs_def: A ReplacementTuple.
* subs_defs: A list of ReplacementTuples.



"""

import os
from pprint import pprint
from argparse import ArgumentParser

# from .data import DEFAULT_FILE_DIRECTIVES
from tts_preprocessor.directives import REGISTERED_DIRECTIVE_DEFS, DEFAULT_FILE_DIRECTIVES
from .pattern_utils import load_patterns, substitute_patterns


def default_argparser(**ap_kwargs):
    ap = ArgumentParser(**ap_kwargs)

    ap.add_argument('inputfiles', nargs='+')  # Only one? Or maybe multiple?
    ap.add_argument('--patternsfile')
    ap.add_argument('-d', '--named-directive', nargs="+", action="append")  # Use standard/default named directives
    # ap.add_argument('--patternsformat')  # how to load patternsfile; yaml/json/txt/tsv/csv; default: tsv
    ap.add_argument('--outputfnfmt', default="{fnroot}.out{fnext}")
    ap.add_argument('--inputencoding', default='utf-8')
    ap.add_argument('--outputencoding', default='utf-8')
    ap.add_argument('--verbose', action="count", default=0)
    # argns = ap.parse_args()  # args, namespace

    return ap


def process_file(inputfile, directives, outputfnfmt=None, inputencoding=None, outputencoding=None, verbose=0):
    if inputencoding is None:
        inputencoding = 'utf-8'
    if outputencoding is None:
        outputencoding = inputencoding
    fnroot, fnext = os.path.splitext(inputfile)
    fnbasename = os.path.basename(inputfile)
    fnbase_noext = os.path.basename(fnroot)
    fndir = os.path.dirname(inputfile)
    with open(inputfile, encoding=inputencoding) as fp:
        print("Reading file:", inputfile)
        content = fp.read()

    # print(directives)
    # print()
    for directive_def in directives:
        print(directive_def)
        content = substitute_patterns(content, directive_def, verbose=verbose)
    # filepath = /mydirectory/myfile.ext
    # basename = myfile.ext  (or sometimes just `myfile` - os.path.basename() returns WITH extension)
    # filename = myfile.ext  (or sometimes just `myfile` and other times the whole filepath)
    # rootname = /mydirectory/myfile
    # so what to call `myfile`?
    # It is rootname of basename (and also basename of rootname)... So maybe baseroot(name) or rootbase(name)?
    # Or maybe just use `fnbase_noext` (for basename with no extension).
    outputfn = outputfnfmt.format(
        inputfile=inputfile, fnroot=fnroot, fnext=fnext, fnbasename=fnbasename, fndir=fndir, fnbase_noext=fnbase_noext,
        cwd=os.getcwd())
    with open(outputfn, mode='w', encoding=outputencoding) as fp:
        print("Writing file:", outputfn)
        fp.write(content)


def select_directives(patternsfile, named_directives, inputfile):
    """This depends on `data` module, `data` module depends on `pattern_utils`. Keep func here to void circular refs."""
    if patternsfile is not None:
        directive_defs = [load_patterns(patternsfile)]
    else:
        if not named_directives:
            fnbase, fnext = os.path.splitext(inputfile)
            inputfiletype = fnext.strip('.')
            if inputfiletype in DEFAULT_FILE_DIRECTIVES:
                named_directives = DEFAULT_FILE_DIRECTIVES[inputfiletype]
                print("Using %s directive (based on input file extension '%s')..." % (named_directives, inputfiletype,))
            else:
                named_directives = DEFAULT_FILE_DIRECTIVES["txt"]
                print("Could not determine which directive(s) to use; defaulting to %s patterns directive."
                      % (named_directives,))
        # print(named_directives)
        # print("\n\nREGISTERED_DIRECTIVE_DEFS:")
        # pprint(REGISTERED_DIRECTIVE_DEFS)
        # print("\n\n")

        directive_defs = [REGISTERED_DIRECTIVE_DEFS[name] for name in named_directives]
        # print("\n\ndirective_defs:")
        # print(directive_defs)
        # print("\n\n")
    return directive_defs


def process_all_inputfiles(
        inputfiles, patternsfile, named_directives, outputfnfmt,
        inputencoding=None, outputencoding=None, verbose=0):
    directives = select_directives(patternsfile, named_directives=named_directives, inputfile=inputfiles[0])
    # print("\nDirectives: (type: %s)" % (type(directives),))
    # pprint.pprint(directives)
    # print(directives)
    for inputfn in inputfiles:
        process_file(
            inputfn,
            directives,
            outputfnfmt=outputfnfmt,
            inputencoding=inputencoding,
            outputencoding=outputencoding,
            verbose=verbose,
        )


def main(argv=None, argns=None):
    if argns is None:
        ap = default_argparser()
        # ap.add_argument("--inputformat")  # Input is e.g. text, html, rtf, latex.
        # Edit, deprechated in favor of --named-directives parameter

        # inputformat/inputtype vs patternsformat:
        # * 'inputtype'/'inputformat': Used to select DEFAULT_PATTERN IF patternsfile is None
        # * * defaults to file extension: txt/html/rtf/tex
        # * 'patternsformat': Used by load_patterns() to select how to parse the patternsfile (text, yaml, or json format).
        argns = ap.parse_args(argv)
    # process_all_inputfiles(**vars(argns))
    # We allow multiple directives with or without multiple --named-directives:
    #   $ tts_preprocessor --named-directive TXT TEX --named-directive HTML
    # (that is, we've used both `nargs="+"` AND `action="append"` when specifying in `add_argument()`
    named_directives = argns.named_directive
    if named_directives is not None:
        named_directives = [directive for nargs in argns.named_directive for directive in nargs]
    process_all_inputfiles(
        inputfiles=argns.inputfiles,
        patternsfile=argns.patternsfile,
        named_directives=named_directives,
        outputfnfmt=argns.outputfnfmt,
        inputencoding=argns.inputencoding,
        outputencoding=argns.outputencoding,
        verbose=argns.verbose,
    )


if __name__ == '__main__':
    main()
