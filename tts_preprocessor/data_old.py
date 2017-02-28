

import os
import re
from pprint import pprint

from .pattern_utils import str_patterns_to_list

DATADIR = os.path.join(os.path.dirname(__file__), '_data')

predefined_pattern_strs = {}
predefined_directives = {}
for fn in os.listdir(DATADIR):
    if fn.endswith("patterns.txt"):
        # print("\n\n\n\n")
        # print(fn)
        fnbase, fnext = os.path.splitext(fn)
        content = open(os.path.join(DATADIR, fn)).read()
        pattern_name = os.path.basename(fnbase)
        # trip trailing ".patterns"
        pattern_name = re.sub(r"\.patterns(\.txt)?$", "", pattern_name)
        predefined_pattern_strs[pattern_name] = content
        predefined_directives[pattern_name] = str_patterns_to_list(content)

# print("\npredefined_pattern_strs:")
# pprint(predefined_pattern_strs)
# print("\npredefined_directives:")
# pprint(REGISTERED_DIRECTIVE_DEFS)

DEFAULT_TXT_PATTERNS = predefined_pattern_strs['default_txt']
DEFAULT_HTML_PATTERNS = predefined_pattern_strs['default_html']
DEFAULT_RTF_PATTERNS = predefined_pattern_strs['default_rtf']
DEFAULT_TEX_PATTERNS = predefined_pattern_strs['default_tex']
DEFAULT_LATEX_PATTERNS = predefined_pattern_strs['default_tex']


DEFAULT_PATTERNS = {
    'txt': DEFAULT_TXT_PATTERNS,
    'tex': DEFAULT_TEX_PATTERNS,
    'html': DEFAULT_HTML_PATTERNS,
}
DEFAULT_FILE_DIRECTIVES = {
    'txt': "default_txt",
    'tex': "default_tex",
    'html': "default_html",
    'rtf': "default_rtf",
}
# print("\nDEFAULT_PATTERNS:")
# pprint(DEFAULT_PATTERNS)
