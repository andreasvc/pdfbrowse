""" Web interface to browse & search PDF files. """
# stdlib
import os
import glob
from subprocess import Popen, PIPE
#from datetime import datetime, timedelta
#from functools import wraps
# Flask & co
from flask import Flask
from flask import request, render_template, redirect, url_for
#from flask import send_from_directory
#from werkzeug.contrib.cache import SimpleCache
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdftypes import resolve1
from xmp import xmp_to_dict

APP = Flask(__name__)


@APP.route('/')
def main():
	""" Redirect to avoid trailing slash hassles. """
	return redirect(url_for('index'))


@APP.route('/index')
def index():
	""" Entry page: search form + first X files. """
	# FIXME: support subdirectories
	files = {'/' + a: gettitle(a)
			for a in glob.glob('static/files/*')[:5]}
	return render_template('index.html', files=files)


@APP.route('/search')
def view():
	""" View a PDF file. """
	query = request.args.get('q', None)
	if query:
		proc = Popen(['tracker-search', query],
				shell=False, stdout=PIPE)
		out, _err = proc.communicate()
		if not out:
			return 'No results.'
		prefix = '  file://%s/static/files/' % os.getcwd()
		results = ['static/files/' + a[len(prefix):]
				for a in out.splitlines() if a.startswith(prefix)]
		results = {'/' + a: gettitle(a) for a in results}
		return render_template('index.html', files=results)
	return 'No query.'


#@APP.route('/favicon.ico')
#def favicon():
#	""" Serve the favicon. """
#	return send_from_directory(os.path.join(APP.root_path, 'static'),
#			'favicon.ico', mimetype='image/vnd.microsoft.icon')


def gettitle(filename):
	""" Get title from PDF metadata or return filename. """
	# try to get PDF title from metadata
	parser = PDFParser(open(filename, 'rb'))
	doc = PDFDocument()
	parser.set_document(doc)
	doc.set_parser(parser)
	doc.initialize()

	# The "Info" metadata
	if doc.info and (doc.info[0].get('Author') or doc.info[0].get('Title')):
		return '%s - %s' % (doc.info[0]['Author'], doc.info[0]['Title'])

	# The XML metadata
	if 'Metadata' in doc.catalog:
		metadata = resolve1(doc.catalog['Metadata']).get_data()
		metadata = xmp_to_dict(metadata)
		return '%s - %s' % (metadata.get('creator', ''),
				metadata.get('title', ''))

	# return filename minus '.pdf'
	return filename.split('/', 2)[-1][:-4]

if __name__ == '__main__':
	APP.run(debug=True, host='0.0.0.0')
