


"""

Version 2:

* Generalized the "directives" input, i.e. merged "--named-directive" and "--patternsfile" to "--directive".

* Now using callable directive TRANSFORMATIONS instead of directive definitions (list of search-replace tuples).

* Using generalized transformations means I can add specialized named functions, without having to rely on ugly
    "If directive is a list, call substitute_patterns(text, directive), else call directive(text)"-code


Regarding outputfnfmt args:
    filepath = /mydirectory/myfile.ext
    basename = myfile.ext  (or sometimes just `myfile` - os.path.basename() returns WITH extension)
    filename = myfile.ext  (or sometimes just `myfile` and other times the whole filepath)
    rootname = /mydirectory/myfile
    so what to call `myfile`?
    It is rootname of basename (and also basename of rootname)... So maybe baseroot(name) or rootbase(name)?
    Or maybe just use `fnbase_noext` (for basename with no extension).


"""

import os
import pprint
from argparse import ArgumentParser

from tts_preprocessor.directives import ensure_directive_is_registered
from tts_preprocessor.directives import DEFAULT_FILE_DIRECTIVES, REGISTERED_DIRECTIVE_DEFS, REGISTERED_TRANSFORMATIONS


def default_argparser(**ap_kwargs):
    ap = ArgumentParser(**ap_kwargs)
    ap.add_argument('inputfiles', nargs='+')  # Only one? Or maybe multiple?
    # ap.add_argument('--patternsfile')
    ap.add_argument('-d', '--directive', nargs="+", action="append", dest="directives",
                    help="A named directive or filename (assume filename, if a file with that name exists).")
    # ap.add_argument('--patternsformat')  # how to load patternsfile; yaml/json/txt/tsv/csv; default: tsv
    ap.add_argument('--outputfnfmt', default="{fnroot}.out{fnext}")
    ap.add_argument('--inputencoding', default='utf-8')
    ap.add_argument('--outputencoding', default='utf-8')
    ap.add_argument('--verbose', action="count", default=0)
    # argns = ap.parse_args()  # args, namespace
    return ap


def apply_transformations(text, transformations):
    for transform in transformations:
        text = transform(text)
    return text


def process_file(inputfile, transformations, outputfnfmt=None, inputencoding=None, outputencoding=None, verbose=0):
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

    for transform in transformations:
        content = transform(content)

    outputfn = outputfnfmt.format(
        inputfile=inputfile, fnroot=fnroot, fnext=fnext, fnbasename=fnbasename, fndir=fndir, fnbase_noext=fnbase_noext,
        cwd=os.getcwd())
    with open(outputfn, mode='w', encoding=outputencoding) as fp:
        print("Writing file:", outputfn)
        fp.write(content)


# def select_directives(named_directives, inputfile):
#     """This depends on `data` module, `data` module depends on `pattern_utils`. Keep func here to void circular refs."""
#     if named_directives:
#         for name in named_directives:
#             ensure_directive_is_registered(name)
#         directives = [REGISTERED_DIRECTIVE_DEFS[name] for name in named_directives]
#     else:
#         # Process using default directives based on file type:
#         fnbase, fnext = os.path.splitext(inputfile)
#         inputfiletype = fnext.strip('.')
#         if inputfiletype in DEFAULT_FILE_DIRECTIVES:
#             directive_name = DEFAULT_FILE_DIRECTIVES[inputfiletype]
#             print("Using %s directive (based on input file extension '%s')..." % (directive_name, inputfiletype,))
#         else:
#             directive_name = DEFAULT_FILE_DIRECTIVES["txt"]
#             print("Could not determine which directive(s) to use; defaulting to %s patterns directive."
#                   % (directive_name,))
#         directives = REGISTERED_DIRECTIVE_DEFS[directive_name]
#     return directives


def get_directive_transforms(directives, inputfile):
    """This depends on `data` module, `data` module depends on `pattern_utils`. Keep func here to void circular refs."""
    if directives:
        for name_or_file in directives:
            ensure_directive_is_registered(name_or_file)
    else:
        # Process using default directives based on file type:
        fnbase, fnext = os.path.splitext(inputfile)
        inputfiletype = fnext.strip('.')
        if inputfiletype in DEFAULT_FILE_DIRECTIVES:
            directives = DEFAULT_FILE_DIRECTIVES[inputfiletype]
            print("Using %s directive (based on input file extension '%s')..." % (directives, inputfiletype,))
        else:
            directives = DEFAULT_FILE_DIRECTIVES["txt"]
            print("Could not determine which directive(s) to use; defaulting to %s patterns directive."
                  % (directives,))
    directives = [REGISTERED_TRANSFORMATIONS[name] for name in directives]
    return directives


def process_all_inputfiles(
        inputfiles, directives, outputfnfmt,
        inputencoding=None, outputencoding=None, verbose=0):
    transformations = get_directive_transforms(directives=directives, inputfile=inputfiles[0])
    # print("\nDirectives: (type: %s)" % (type(directives),))
    # pprint.pprint(directives)
    # print(directives)
    for inputfn in inputfiles:
        process_file(
            inputfn,
            transformations=transformations,
            outputfnfmt=outputfnfmt,
            inputencoding=inputencoding,
            outputencoding=outputencoding,
            verbose=verbose,
        )


def main(argv=None, argns=None):
    if argns is None:
        ap = default_argparser()
        argns = ap.parse_args(argv)
    # We allow multiple directives with or without multiple --named-directives:
    #   $ tts_preprocessor --directive TXT TEX --directive HTML --directive myowndefs.txt
    # (that is, we've used both `nargs="+"` AND `action="append"` when specifying in `add_argument()`
    directives = argns.directives
    if directives is not None:
        directives = [directive for nargs in argns.directives for directive in nargs]
        print("Directives:", directives)
    process_all_inputfiles(
        inputfiles=argns.inputfiles,
        directives=directives,
        outputfnfmt=argns.outputfnfmt,
        inputencoding=argns.inputencoding,
        outputencoding=argns.outputencoding,
        verbose=argns.verbose,
    )


if __name__ == '__main__':
    main()
