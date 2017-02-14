
"""

See rtf_preprocessing for general things.


HTML-to-text:
* https://github.com/aaronsw/html2text





"""


from .data import DEFAULT_HTML_PATTERNS
from .common import process_all_inputfiles, default_argparser


def main(argv=None, argns=None):
    if argns is None:
        ap = default_argparser()
        argns = ap.parse_args(argv)
    process_all_inputfiles(
        inputfiles=argns.inputfiles,
        patternsfile=argns.patternsfile,
        outputfnfmt=argns.outputfnfmt,
        inputformat='html',
        patternsformat=argns.patternsformat)


