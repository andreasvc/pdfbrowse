Web-based PDF viewer and browser
================================

This is a frontend to Tracker for searching PDFs and viewing them in your
browser with PDF.js. A use case is when you need to find a paper but
they all have names like ``10.1.1.53.1442.pdf`` or ``sdarticle (45).pdf``.

Requires:

- Flask
- tracker
- PDF.js
- node (to build PDF.js)

Installation::

    apt-get install tracker tracker-utils python-pdfminer python-flask nodejs
    git clone --depth 1 git://github.com/andreasvc/pdfbrowse
    cd pdfbrowse/
    sh setup.sh

Edit ``pdfbrowse.py`` and enter a directory in tracker's
watchlist. Note that all files under this directory will be accessible through
the application.

To run locally: ``python pdfbrowse.py``, access at http://localhost:5000

Or install through ``mod_wsgi``.
