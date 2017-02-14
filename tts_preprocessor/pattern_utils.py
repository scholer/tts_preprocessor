import json
import os
import re
from collections import namedtuple

PATTERN_TYPES = [
    "REGEX",  # 0 or None
    "FIXED"   # 1
]
ReplacementTuple = namedtuple('ReplacementTuple', ('search_pat', 'replace_pat', 'type', 'comment'))


def str_patterns_to_list(patterns_str, sep='\t'):
    """Convert standard 1-pattern-per-line text string to a list of (search, replace, type, comment) NamedTuples."""
    if sep is None:
        sep = '\t'

    patterns = [line.strip() for line in patterns_str.strip().split("\n")]  # Trim input:
    patterns = [line for line in patterns if line]  # Remove empty lines:
    patterns = [line for line in patterns if line[0] != '#']  # Remove comment lines:

    directives = []
    for line in patterns:
        directive_args = [None, None, None, None]
        # search_pat, replace_pat, pat_type, comment = None, None, None, None
        if '#' in line:
            # line, comment = line.split("#", 1)
            line, directive_args[-1] = line.split("#", 1)
        line_vals = line.strip(sep).split(sep)
        # print(directive_args)
        directive_args[:len(line_vals)] = line_vals[:3]  # At most 3 vals: search_pat, replace_pat, pat_type
        # print(directive_args)
        directives.append(ReplacementTuple(*directive_args))
    return directives


def load_patterns(filename, format=None, **kwargs):
    """Load patterns/directives from file."""
    with open(filename) as fp:
        content = fp.read()
    fnbase, fnext = os.path.splitext(filename)

    if fnext in ('.json',) or format == "json":
        directives = json.loads(content, **kwargs)
    elif fnext in ('.yml', '.yaml') or format == "yaml":
        import yaml
        directives = yaml.load(content, **kwargs)
    else:
        directives = str_patterns_to_list(content, **kwargs)
    return directives


def substitute_patterns(string, directives, verbose=0):
    """Perform all regex/string substitutions listed in directives (one by one)."""
    for directive in directives:
        # directive : ('search_pat', 'replace_pat', 'type', 'comment') namedtuple
        if directive.type == 1:
            string = string.replace(directive.search_pat, directive.replace_pat)
        else:
            if verbose > 0:
                print("Replacing using regex: %s --> %s" % (directive.search_pat, directive.replace_pat))
            string = re.sub(pattern=directive.search_pat, repl=directive.replace_pat or "", string=string)
    return string


