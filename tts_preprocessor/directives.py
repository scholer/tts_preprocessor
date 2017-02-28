
"""

Nomenclature:
-------------

Op / operation: A single operation, e.g. a substitution operation defined by a ReplacementTuple.
    Directive ops include:
        * Substitutions (regex or fixed-string)

Directive name: Name of a directive, e.g. 'latex_to_text'

Directive def: The full sequence of operations defining a directive, e.g. a list of ReplacementTuples.

Transformation, directive transform: the functional expression/implementation of a directive, e.g.
    function(text) --> transformed_text


Obsolete nomenclature / not used:
* Directive group: Old name for "directive def", group because it has multiple "operations".
* subs_def: A ReplacementTuple.
* subs_defs: A list of ReplacementTuples.

"""

import os
from functools import partial

from tts_preprocessor.pattern_utils import load_patterns_defs, substitute_patterns

# DATADIR = os.path.join(os.path.dirname(__file__))
DATADIR = os.path.join(os.path.dirname(__file__), 'data')
REGISTERED_DIRECTIVE_DEFS = {}
REGISTERED_TRANSFORMATIONS = {}


def register_directive_defs(directive_name, directives):
    REGISTERED_DIRECTIVE_DEFS[directive_name] = directives


# Transformation functions:
def register_subs_directive_func(directive_name, directive_list, verbose=0):
    REGISTERED_TRANSFORMATIONS[directive_name] = partial(substitute_patterns, directive=directive_list)


def register_directives_from_file(fn):
    # TODO: Make a lazy-loading function instead of loading all data on startup
    # Make sure to register both with the "simple" name and with the full filename/path.
    directives_name, directives = load_patterns_defs(fn)
    register_directive_defs(directives_name, directives)
    register_directive_defs(fn, directives)
    register_subs_directive_func(fn, directives)
    register_subs_directive_func(directives_name, directives)


def ensure_directive_is_registered(name_or_file):
    if os.path.isfile(name_or_file):
        # name_or_file, directive_defs = load_patterns_defs(name_or_file)
        # register_directive_defs(name_or_file, directive_defs)
        register_directives_from_file(name_or_file)
    else:
        assert name_or_file in REGISTERED_TRANSFORMATIONS
    return name_or_file


def load_directives_from_dir(directory):
    for root, dirs, files in os.walk(directory):
        # root: str, dirs: list, files: list
        for fn in files:
            fnroot, fnext = os.path.splitext(fn)
            if fn[0] in (".", "_") or fnext[:2] == "py":
                continue
            # print(root, fn)
            register_directives_from_file(os.path.join(root, fn))
load_directives_from_dir(DATADIR)


# A transformation is any function that takes a single text argument and transforms it.
# Add library-defined functional directive transformations:
from .latex_processing import pylatexenc_convert
FUNCTIONAL_TRANSFORMATIONS = {
    'pylatexenc': pylatexenc_convert
}
REGISTERED_TRANSFORMATIONS.update(FUNCTIONAL_TRANSFORMATIONS)


DEFAULT_FILE_DIRECTIVES = {
    # list of default directives (names) depending on file type:
    # To get transforms for fnext, do:
    # transforms = [REGISTERED_TRANSFORMATIONS[name] for name in DEFAULT_FILE_DIRECTIVES[fnext]]
    'txt': ["default_txt"],
    'tex': ["default_tex"],
    'html': ["default_html"],
    'rtf': ["default_rtf"],
}


def get_directive_transformation(directive):
    """Convert ambiguous "directive" (name/op-sequence/transformation) to unambiguous transformation function."""
    if hasattr(directive, '__call__'):
        return directive
    if isinstance(directive, str):
        if directive not in REGISTERED_TRANSFORMATIONS:
            register_subs_directive_func(directive_name=directive, directive_list=REGISTERED_DIRECTIVE_DEFS[directive])
        return REGISTERED_TRANSFORMATIONS[directive]
    else:
        # Assume directive is a list of substitution operation tuples:
        return partial(substitute_patterns, directive=directive)


# print("\npredefined_pattern_strs:")
# pprint(predefined_pattern_strs)
# print("\npredefined_directives:")
# pprint(REGISTERED_DIRECTIVE_DEFS)

# DEFAULT_TXT_PATTERNS = predefined_pattern_strs['default_txt']
# DEFAULT_HTML_PATTERNS = predefined_pattern_strs['default_html']
# DEFAULT_RTF_PATTERNS = predefined_pattern_strs['default_rtf']
# DEFAULT_TEX_PATTERNS = predefined_pattern_strs['default_tex']
# DEFAULT_LATEX_PATTERNS = predefined_pattern_strs['default_tex']


# DEFAULT_PATTERNS = {
#     'txt': DEFAULT_TXT_PATTERNS,
#     'tex': DEFAULT_TEX_PATTERNS,
#     'html': DEFAULT_HTML_PATTERNS,
# }
# print("\nDEFAULT_PATTERNS:")
# pprint(DEFAULT_PATTERNS)
