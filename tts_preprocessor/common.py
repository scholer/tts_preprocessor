"""




"""

import os
import pprint
from argparse import ArgumentParser

from .data import DEFAULT_PATTERNS, DEFAULT_FILE_DIRECTIVES, predefined_directives
from .pattern_utils import str_patterns_to_list, load_patterns, substitute_patterns


# formats_loaders = {
#     '.txt': str_patterns_to_list,
#     # '.yml': yaml.load if yaml else None,
#     '.json': json.loads
# }


def default_argparser(**ap_kwargs):
    ap = ArgumentParser(**ap_kwargs)

    ap.add_argument('inputfiles', nargs='+')  # Only one? Or maybe multiple?
    ap.add_argument('--patternsfile')
    ap.add_argument('-d', '--named-directive', nargs="+", action="append")  # Use standard/default named directives
    # ap.add_argument('--patternsformat')  # how to load patternsfile; yaml/json/txt/tsv/csv; default: tsv
    ap.add_argument('--outputfnfmt', default="{fnbase}.out{fnext}")
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
    fnbase, fnext = os.path.splitext(inputfile)
    with open(inputfile, encoding=inputencoding) as fp:
        print("Reading file:", inputfile)
        content = fp.read()

    content = substitute_patterns(content, directives, verbose=verbose)

    outputfn = outputfnfmt.format(inputfile=inputfile, fnbase=fnbase, fnext=fnext)
    with open(outputfn, mode='w', encoding=outputencoding) as fp:
        print("Writing file:", outputfn)
        fp.write(content)


def select_directives(patternsfile, named_directives, inputfile):
    """This depends on `data` module, `data` module depends on `pattern_utils`. Keep func here to void circular refs."""
    if patternsfile is not None:
        directives = load_patterns(patternsfile)
    elif named_directives:
        directives = []
        for name in named_directives:
            directives.append(predefined_directives[name])
    else:
        fnbase, fnext = os.path.splitext(inputfile)
        inputfiletype = fnext.strip('.')
        if inputfiletype in DEFAULT_FILE_DIRECTIVES:
            directive_name = DEFAULT_FILE_DIRECTIVES[inputfiletype]
            print("Using %s directive (based on input file extension '%s')..." % (directive_name, inputfiletype,))
        else:
            directive_name = DEFAULT_FILE_DIRECTIVES["txt"]
            print("Could not determine which directive(s) to use; defaulting to %s patterns directive."
                  % (directive_name,))
        directives = predefined_directives[directive_name]
        # directives = str_patterns_to_list(directives)
    return directives


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
