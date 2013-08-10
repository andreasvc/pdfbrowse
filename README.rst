Web-based PDF viewer and browser
================================

The idea is to drop a bunch of PDFs into ``static/files/`` and have them indexed by ``tracker``.
This webapp allows to search and view them from within your browser.

Requires:

- Flask
- tracker
- PDF.js
- PDFMiner

Installation::

    apt-get install tracker tracker-utils python-pdfminer python-flask
    git clone --depth 1 git://github.com/andreasvc/pdfbrowse
    cd pdfbrowse/
    git clone --depth 1 git://github.com/mozilla/pdf.js.git pdfjs
    sh setup.sh

Place PDF files in ``static/files``, and add this directory to tracker's
watchlist using ``tracker-preferences``.

To run locally: ``python pdfbrowse.py``, access at http://localhost:5000

Or install through ``mod_wsgi``.