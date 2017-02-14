

"""

Module for dealing with RTF content:



Copy/paste RTF and HTML to/from the system clipboard:
-----------------------------------------------------

Overview:
* richxerox – Rich text cut/copy/paste for Mac OS X.
* xerox – Only handles plain text.
* pyperclip – Only handles plain text.
* Xclipboard – Based on tkinter, about 10 LOC.
* win32clipboard — from pywin32 extension module
* jaraco.clipboard — Supports HTML on MacOS and HTML and images on Windows.



richxerox: Rich text cut/copy/paste for Mac OS X.
* https://pypi.python.org/pypi/richxerox
* https://bitbucket.org/jeunice/richxerox

win32clipboard:
* http://timgolden.me.uk/pywin32-docs/win32clipboard.html
* https://pypi.python.org/pypi/pywin32

Jaraco.clipboard:
* https://github.com/jaraco/jaraco.clipboard
* Uses jaraco.windows on Windows; richxerox on Mac OS, and pyperclip on Linux.
* https://github.com/jaraco/jaraco.windows


Using Qt:
* http://stackoverflow.com/questions/10055421/with-qclipboard-how-can-i-copy-rich-text-and-have-it-downgrade-to-plain-text-fo
* http://doc.qt.io/qt-5/qclipboard.html
* http://pyqt.sourceforge.net/Docs/PyQt4/qclipboard.html
* https://github.com/scholer/instaporter/blob/master/instaporter/clipboard.py
* https://pypi.python.org/pypi/shareboard

Other RTF on Mac OS X clipboard refs:
* https://genbastechthoughts.wordpress.com/2012/05/20/reading-urls-from-os-x-clipboard-with-pyobjc/
* http://blog.carlsensei.com/post/88897796
* https://developer.apple.com/reference/appkit/nspasteboard
* http://sigpipe.macromates.com/2009/03/09/uti-problems/
* http://daringfireball.net/2010/08/open_urls_in_safari_tabs
* `man pbpaste`
* https://www.daniweb.com/programming/software-development/code/487653/access-the-clipboard-via-tkinter

RTF on Windows:
* pywin32 / win32clipboard
* HtmlClipboard
* * http://code.activestate.com/recipes/474121-getting-html-from-the-windows-clipboard/
* * https://github.com/noahcoad/various-python-goodies/blob/master/HtmlClipboard.py
* * https://github.com/EnoraNedelec/Zotero_Pdf_Highlights_with_HtmlClipboard/blob/master/HtmlClipboard.py
* https://pypi.python.org/pypi/jaraco.clipboard
* QClipboard
* * http://stackoverflow.com/questions/10055421/with-qclipboard-how-can-i-copy-rich-text-and-have-it-downgrade-to-plain-text-fo



Other RTF on Windows refs
* http://stackoverflow.com/questions/17298897/how-can-i-copy-from-an-html-file-to-the-clipboard-in-python-in-formatted-text
* http://code.activestate.com/recipes/474121-getting-html-from-the-windows-clipboard/
* https://github.com/EnoraNedelec/Zotero_Pdf_Highlights_with_HtmlClipboard
* http://stackoverflow.com/questions/41660831/python-3-6-windows-retrieving-the-clipboard-cf-html-format
* https://msdn.microsoft.com/en-us/library/windows/desktop/ms649013(v=vs.85).aspx


RTF on Linux:
* gtk.Clipboard().wait_for_contents('text/html')).data
* http://askubuntu.com/questions/427704/how-can-i-edit-the-source-of-html-in-the-clipboard/427723


RTF and HTML on Sublime Text:
* https://packagecontrol.io/packages/RichTextFormat
* https://packagecontrol.io/packages/Markboard — Converts markdown text to RTF and adds it to the clipboard (abandoned).
* https://packagecontrol.io/search/clipboard
* https://github.com/anderson916/sublime-html2jade


"""
