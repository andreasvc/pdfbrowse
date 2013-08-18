""" Web interface to browse & search PDF files. """
# stdlib
import os
import re
import glob
from urllib import unquote
from subprocess import Popen, PIPE
from collections import OrderedDict
# Flask & co
from flask import Flask
from flask import request, render_template, redirect, url_for
from flask import send_from_directory

# path to a directory indexed by Tracker; all files under it will be exposed
FILESROOT = '~/Downloads'
LIMIT = 100  # number of search results to return

PDFEXT = re.compile(r'.+\.[Pp][Dd][Ff]$')
APP = Flask(__name__)

@APP.route('/')
def main():
	""" Redirect to avoid trailing slash hassles. """
	return redirect(url_for('index'))


@APP.route('/index')
def index():
	""" Entry page: search form + first X files. """
	prefix = os.path.expanduser(FILESROOT)
	if not prefix.endswith('/'):
		prefix += '/'
	files = ['files/' + a.decode('utf8')[len(prefix):]
			for a in glob.glob(prefix + '*')[:5]]
	files = {'/' + a: gettitle(a) for a in files if PDFEXT.match(a)}
	return render_template('index.html', files=files)


@APP.route('/search')
def search():
	""" Get search results from tracker. """
	prefix = '  file://' + os.path.expanduser(FILESROOT)
	if not prefix.endswith('/'):
		prefix += '/'
	query = request.args.get('q', None)
	if not query:
		return 'No query.'
	# --documents option does not match all PDF files on my system.
	proc = Popen(['tracker-search', query],
			shell=False, stdout=PIPE, stderr=PIPE)
	out, err = proc.communicate()
	if out:
		lines = ['files/' + a[len(prefix):] for a in
				unquote(out).decode('utf8').splitlines()
				if a.startswith(prefix)]
		results = OrderedDict(('/' + a, gettitle(a))
				for a in lines[:LIMIT])  # if PDFEXT.match(a))
	return render_template('index.html', files=results, query=query, err=err)


@APP.route('/favicon.ico')
def favicon():
	""" Serve the favicon. """
	return send_from_directory(os.path.join(APP.root_path, 'static'),
			'favicon.ico', mimetype='image/vnd.microsoft.icon')


@APP.route('/files/<path:filename>')
def download_file(filename):
	""" Serve a PDF. """
	return send_from_directory(os.path.expanduser(FILESROOT), filename)


def gettitle(filename):
	""" Get title from filename. """
	# filename minus 'files/' prefix and extension (if any)
	default = filename.split('/', 1)[-1].rsplit('.', 1)[0]
	return default


if __name__ == '__main__':
	APP.run(debug=True, host='0.0.0.0')
