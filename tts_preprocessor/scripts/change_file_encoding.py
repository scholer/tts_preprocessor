
"""
Module for changing encoding of files.

See also:
    `iconv` - unix tool to convert text encodings:
        $ iconv -f CP1252 -t utf-8 inputfile


"""


import os
import argparse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputencoding")  # , default="utf-8")  # or use chardet
    ap.add_argument("outputencoding")  # , default="utf-8")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--outputfnfmt", default="{fnbase}.{outputencoding}{fnext}")  #   {inputfn}.out
    ap.add_argument("inputfiles", nargs="+")

    argns = ap.parse_args()

    inputfiles = argns.inputfiles
    inputencoding = argns.inputencoding
    outputencoding = argns.outputencoding
    outputfnfmt = argns.outputfnfmt
    overwrite = argns.overwrite

    try:
        import chardet
    except ImportError as e:
        print("Module `chardet` not available; will use 'utf8' as default encoding (when not specified).")

    for inputfn in inputfiles:
        _encoding = inputencoding
        fnbase, fnext = os.path.splitext(inputfn)
        outputfn = outputfnfmt.format(inputfn=inputfn, fnbase=fnbase, fnext=fnext,
                                      inputencoding=inputencoding, outputencoding=outputencoding)
        if os.path.exists(outputfn) and not overwrite:
            answer = input("File %s exists. Overwrite? " % outputfn)
            if not answer or answer.lower()[0] != 'y':
                print(" - Skipping file: %s" % outputfn)
                continue
        if _encoding is None:
            # Use chardet
            # OBS: Not actually very good at detecting e.g. Danish characters in Windows-1252 / CP1252.
            with open(inputfn, 'rb') as fp:
                file_bytes = fp.read()
                try:
                    _encoding = chardet.detect(file_bytes)['encoding']
                except KeyError:
                    print("Could not detect encoding of file %s\n - skipping.." % inputfn)
                    continue
                # For large files, you can also create a detector and use detector.feed(fp)
        with open(inputfn, encoding=_encoding) as fp:
            print("Reading %s" % inputfn)
            content = fp.read()
        with open(outputfn, mode='w', encoding=outputencoding) as fp:
            print("(Re-)writing content to file:", outputfn)
            fp.write(content)
            print(" - Done!")


if __name__ == '__main__':
    main()
