
"""

## OBS: Nomenclature:

* A *single* "def" is a single row, dict, or tuple, providing a search_pattern and replace_pattern,
    and is used for a single search-replace operation.
* "def" or "definition" is typically used on the input side, while "operation" is used
* Synonyms: "def" = "definition" = "pattern definition" = "search replace operation definition"
* "defs" is a list of these pattern definitions.

* "directive" is a list of pattern definitions, and is used for registering "named directives".
    "directive_defs" is often used to distinguish this from "directive_name".


TODO: I should make the terms more clear or consistent. I use the following terms:
TODO: "defs" ("definitions"), "directives", and "operations" (and "directive_ops" and "directive_def").

* I think this is an evolutionary thing - first they were called "definitions"
   then "directives", and then "operations"?

* Also inconsistent use whether "directive" is *a single* search-replace, or the full list.
* `common.process_file()` has "directive" as a "list of search-replace operations".
    Here, "directive" is a "general, filetype-specific processing", e.g.
    "perform standard text replacements", or "perform latex-specifc operations".
* "Directive" is either:
    "directive_name" - e.g. 'latex_to_text'
    "directive_defs" - a list of
* "definitions" is mostly used on the input side, while "operations" is mostly used on the other end.
* See also `directives.py` for a nomenclature list.


TODO: You have a lot of things here that are defined but not really used anywhere,
TODO: e.g. the `PATTERN_TYPES`, `REGEX_TYPE`, and `FIXED_TYPE` constants.

"Substitute" or "Replace"?  (substitution or replacement)
* Generally treated as SYNONYMS, but slight syntactic differences.
* "Substitute" is usually temporary, and may hint inferior option: The PT teacher substituted for the Math teacher.
* Different rhetorical order: "Substitute new FOR old", vs "Replace old WITH new".
* Python: str.replace(old, new), but re.sub(search_pattern, substitute_pattern)
Refs:
* http://english.stackexchange.com/questions/216188/replace-vs-substitute

"""


import os
import re
from collections import namedtuple
import pickle
import json
import yaml
from itertools import zip_longest
from pprint import pprint

# TODO: Use a proper `enum` type
PATTERN_TYPES = [
    "REGEX",  # 0 or None
    "FIXED"   # 1
]
REGEX_TYPE = 0
FIXED_TYPE = 1

# "Replacement" == "Substitution"
REPLACEMENTTUPLEARGS = ('search_pat', 'replace_pat', 'type', 'comment')
ReplacementTuple = namedtuple('ReplacementTuple', REPLACEMENTTUPLEARGS)
SUBS_DEFAULTS_KEYS = ('replace_pat', 'type', 'comment')
SUBS_DEFAULTS_VALS = ("", 0, None)
SUBS_DEFAULTS_DICT = dict(zip(SUBS_DEFAULTS_KEYS, SUBS_DEFAULTS_VALS))
# Use .__new__.__defaults__ to set default values (for right-most arguments: 3-tuple = last three args are optional)
ReplacementTuple.__new__.__defaults__ = SUBS_DEFAULTS_VALS  # must be a tuple object


def substitute_patterns(string, directive, verbose=0):
    """ Perform all regex/string substitutions listed in directive (one by one).

    Args:
        string: The string to perform the search/replace operations on.
        directive: A list of `ReplacementTuple`s (namedtuple).
        verbose:

    Returns:

    """
    for operation in directive:
        # operation : ('search_pat', 'replace_pat', 'type', 'comment') namedtuple
        if operation.type == 1:
            if verbose > 0:
                print("Replacing fixed-string: %s --> %s" % (operation.search_pat, operation.replace_pat))
            string = string.replace(operation.search_pat, operation.replace_pat)
        else:
            if verbose > 0:
                print("Replacing using regex: %s --> %s" % (operation.search_pat, operation.replace_pat))
            string = re.sub(pattern=operation.search_pat, repl=operation.replace_pat or "", string=string)
    return string


def pattern_defs_to_tuples(defs, options):
    """ Convert a list of pattern definitions (dicts or lists/tuples) to ReplacementTuple (namedtuple).

    This basically ensures that `defs` is converted to the proper format, ready for consumption by
    `substitute_patterns()`.

    Args:
        defs: list of pattern definitions (list of dicts or lists/tuples).
            defs can also be a dict, mapping {search_pat: replace_pat}.
        options: This can be used to set e.g. default value.
            For example, pass `options={"type": FIXED_TYPE}` to use fixed strings as the default value.

    Returns:

        directive_ops: A list of `ReplacementTuple`s (namedtuple).

    """
    if options is None:
        options = {}
    defaults = SUBS_DEFAULTS_DICT.copy()
    if 'defaults' in options:
        defaults.update(options['defaults'])
    if 'type' in options:
        defaults['type'] = options['type']
    directive_ops = []
    if isinstance(defs, dict):
        # defs is a simple dict, mapping {search_pat: replace_pat}
        # OR {search_pat: (replace_pat, type, comment)-tuple}
        # convert dict to list of defs:
        defs = [[key] + val if isinstance(val, (list, tuple)) else [key, val] for key, val in defs.items()]

    for definition in defs:
        def_default = defaults.copy()
        if not isinstance(definition, dict):
            # Assume sequence of ('search_pat', 'replace_pat', 'type', 'comment')
            def_default.update(zip(REPLACEMENTTUPLEARGS, definition))
        else:
            def_default.update(definition)
        operation = ReplacementTuple(**def_default)
        directive_ops.append(operation)

    return directive_ops


def tsv_to_list(tsv_input, sep=None, trim_line_comments=True):
    """ Read tab-separated input, return as a list of rows (lists).

    Args:
        tsv_input: Tab-separated input, either as text string, a file-like object, or an iterable.
        sep: The separator to use, defaulting to TAB.
        trim_line_comments: Will remove "# comment" for all lines.

    Returns:
        A list of rows.
    """
    if sep is None:
        sep = "\t"
    if hasattr(tsv_input, 'read'):
        tsv_input = tsv_input.read()
    if isinstance(tsv_input, str):
        lines = [line.strip() for line in tsv_input.strip().split("\n")]  # Trim input:
    else:
        lines = [line.strip() for line in tsv_input]
    lines = [line for line in lines if line]  # Remove empty lines:
    # Support configuring file options with an initial comment line:
    # first_line = lines[0]
    # if first_line and first_line[0:3] == "# {":
    #     first_line = first_line.strip("# ")
    #     options = yaml.load(first_line)
    lines = [line for line in lines if line[0] != '#']  # Remove comment lines:
    if trim_line_comments:
        # Remove trailing line comments: val1, val2, val3  # this is a end-of-line comment
        lines = [line.split('#', 1)[0] for line in lines]
    rows = [line.strip(sep).split(sep) for line in lines]
    return rows


def extract_first_line_config(input, commentchar="#"):
    """ Extract per-file configuration line.
    The first line must begin with "# {"  (i.e. a hash symbol, a space, and an opening brace).
    This can be used to create pattern definition files, where

    Args:
        input:
        commentchar:

    Returns:

    """
    if isinstance(input, str):
        input = input.strip().split("\n")[0]  # Select the first non-empty line.
    elif hasattr(input, 'readline'):
        # Assume file-like object:
        # This isn't completely fool-proof:
        # * There is a chance that this will skip the first non-comment line.
        # * There is also a chance that the first line is empty.
        # * But pattern definition files should always contain a comment at the top,
        #   and the first-line-config should always be at the very first line anyways.
        input = input.readline().strip()
    else:
        # Assume list of lines:
        input = input[0]
    if input and input[0] == commentchar and input[:3] == "# {":
        input = input.strip("# ")
        try:
            config = yaml.load(input)
        except yaml.scanner.ScannerError as e:
            print("Error extracting yaml-config from first comment line:", e)
            print(input)
            config = {}
    else:
        config = {}
    return config


def parse_pattern_txt_defs_to_list(patterns_str, sep='\t', options=None, extract_config_line=True):
    """Convert standard 1-pattern-per-line text string to a list of (search, replace, type, comment) NamedTuples."""
    if options is None:
        options = {}
    if extract_config_line:
        options.update(extract_first_line_config(patterns_str))
    pat_def_rows = tsv_to_list(patterns_str, sep)
    directive_ops = pattern_defs_to_tuples(pat_def_rows, options=options)
    return directive_ops


def load_patterns_defs(filename, format=None, name=None, **kwargs):
    """ Load substitution (replacement) definitions/patterns from file.

    This supports both simple "text-definitions", but can also be used to dump
    a complete "workspace settings" to file (json, yaml, or pickle).

    Args:
        filename:
        format:
        name:
        **kwargs:

    Returns:

    If the file is a "full workspace" JSON, YAML or Pickle file, it is expected to
    contain a single dict, with the following keys:
        "substitutions":
        "options":
    """

    fnbase, fnext = os.path.splitext(filename)
    if format is None and fnext:
        format = fnext[1:].lower()
    mode = 'rb' if format == 'pickle' else 'r'

    with open(filename, mode=mode) as fp:

        if format in ("json", "yaml", "yml", "pickle"):
            # Structured data formats, a dict with keys 'substitutions', 'options', etc.
            if format == "json":
                # directives = json.loads(content, **kwargs)
                data = json.loads(fp, **kwargs)
            elif format in ('yml', 'yaml'):
                # directives = yaml.load(content, **kwargs)
                data = yaml.load(fp, **kwargs)
            elif format == "pickle":
                data = pickle.load(fp, **kwargs)
            else:
                raise ValueError("Unknown format: '%s' for file '%s'" % (format, filename))
            options = data.get('options', {})
            options.update(kwargs)
            subs_defs = data['substitutions']
            if name is None:
                name = options.get('name')
            directives = pattern_defs_to_tuples(subs_defs, options)
        elif format[:2] == "py":
            pass
        else:
            # Data is a list of substitutions with optional first-line config:
            # directives = str_patterns_to_list(fp.read(), options=options)
            directives = parse_pattern_txt_defs_to_list(fp.read())  # OBS: This will not load line comments
    if name is None:
        # Use filename as directive-group name:
        name = os.path.basename(filename).split(".", 1)[0]
    # print("\n%s" % (name,))
    # pprint(directives)
    # print()
    return name, directives


# OLD!! - replaced by `parse_pattern_txt_defs_to_list`
def str_patterns_to_list(patterns_str, sep='\t', options=None):
    """Convert standard 1-pattern-per-line text string to a list of (search, replace, type, comment) NamedTuples."""
    if sep is None:
        sep = '\t'

    patterns = [line.strip() for line in patterns_str.strip().split("\n")]  # Trim input:
    patterns = [line for line in patterns if line]  # Remove empty lines:

    first_line = patterns[0]
    if first_line and first_line[0:3] == "# {":
        first_line = first_line.strip("# ")
        options = yaml.load(first_line)

    patterns = [line for line in patterns if line[0] != '#']  # Remove comment lines:

    directives = []
    for line in patterns:
        directive_args = [None, None, None, None]  # Alternatively, set ReplacementTuple.__new__.__defaults__
        # search_pat, replace_pat, pat_type, comment = None, None, None, None
        if '#' in line:
            # line, comment = line.split("#", 1)
            line, directive_args[-1] = line.split("#", 1)
        line_vals = line.strip(sep).split(sep)
        # print(directive_args)
        directive_args[:len(line_vals)] = line_vals[:3]  # At most 3 vals: search_pat, replace_pat, pat_type
        # print(directive_args)
        # directives.append(ReplacementTuple(*directive_args))
    # Run through pattern_defs_to_tuples to set defaults:
    if options:
        directives = pattern_defs_to_tuples(directives, options)
    return directives


# OLD!!
def load_patterns(filename, format=None, name=None, **kwargs):
    """Load patterns/directives from file."""
    with open(filename) as fp:
        content = fp.read()
    fnbase, fnext = os.path.splitext(filename)

    if fnext in ('.json',) or format == "json":
        directives = json.loads(content, **kwargs)
    elif fnext in ('.yml', '.yaml') or format == "yaml":
        directives = yaml.load(content, **kwargs)
    else:
        directives = str_patterns_to_list(content, **kwargs)
    return directives


