""" Suggest new filenames for PDF based on metadata.
Prints a shell script with rename commands for PDF files in current directory.
"""
# Source for parsing of XMP:
# http://blog.matt-swain.com/post/25650072381/a-lightweight-xmp-parser-for-extracting-pdf-metadata-in

from __future__ import print_function
import re
from glob import glob
from collections import defaultdict
from xml.etree import ElementTree as ET
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdftypes import resolve1

RDF_NS = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
XML_NS = '{http://www.w3.org/XML/1998/namespace}'
NS_MAP = {
	'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf',
	'http://purl.org/dc/elements/1.1/': 'dc',
	'http://ns.adobe.com/xap/1.0/': 'xap',
	'http://ns.adobe.com/pdf/1.3/': 'pdf',
	'http://ns.adobe.com/xap/1.0/mm/': 'xapmm',
	'http://ns.adobe.com/pdfx/1.3/': 'pdfx',
	'http://prismstandard.org/namespaces/basic/2.0/': 'prism',
	'http://crossref.org/crossmark/1.0/': 'crossmark',
	'http://ns.adobe.com/xap/1.0/rights/': 'rights',
	'http://www.w3.org/XML/1998/namespace': 'xml'}
NONALPHA = re.compile('[^A-Za-z]')


def main():
	for filename in glob('*.pdf'):
		if len(NONALPHA.sub('', filename)) > 8:
			continue
		title = gettitle(filename)
		if not title:
			continue
		print("mv '%s' '%s.pdf'" % (
				filename.replace("'", "'\\''"),
				title.replace("'", "'\\''")))


def gettitle(filename):
	""" try to get PDF title from metadata """
	candidates = []
	try:
		parser = PDFParser(open(filename, 'rb'))
	except IOError:  # FIXME encoding errors
		#print('open failed: %s', filename)
		return
	doc = PDFDocument()
	try:
		parser.set_document(doc)
		doc.set_parser(parser)
		doc.initialize()
	except Exception as err:
		#print('initialize failed: %s; %s', filename, err)
		return

	# The "Info" metadata
	if doc.info and (doc.info[0].get('Author') or doc.info[0].get('Title')):
		author = doc.info[0].get('Author', '')
		title = doc.info[0].get('Title', '')
		if author or title:
			candidates.append(('%s - %s' % (author, title)
					).decode('latin1', 'replace'))

	# The XML metadata
	if 'Metadata' in doc.catalog:
		metadata = resolve1(doc.catalog['Metadata']).get_data()
		try:
			metadata = xmp_to_dict(metadata)
		except (AttributeError, Exception):  # FIXME
			#print('XMP failed: %s', filename)
			pass
		else:
			author = metadata.get('creator', '')
			title = metadata.get('title', '')
			if author or title:
				candidates.append(('%s - %s' % (author, title)
						).decode('utf8', 'replace'))

	return max(candidates, key=len) if candidates else None


class XmpParser(object):
	""" Parses an XMP string into a dictionary. Usage:

	>>> parser = XmpParser(xmpstring)
	>>> meta = parser.meta """
	def __init__(self, xmp):
		self.tree = ET.XML(xmp)
		self.rdftree = self.tree.find(RDF_NS+'RDF')

	@property
	def meta(self):
		""" A dictionary of all the parsed metadata. """
		meta = defaultdict(dict)
		for desc in self.rdftree.findall(RDF_NS+'Description'):
			for el in desc.getchildren():
				ns, tag =  self._parse_tag(el)
				value = self._parse_value(el)
				meta[ns][tag] = value
		return dict(meta)

	def _parse_tag(self, el):
		""" Extract the namespace and tag from an element. """
		ns = None
		tag = el.tag
		if tag[0] == "{":
			ns, tag = tag[1:].split('}', 1)
			if ns in NS_MAP:
				ns = NS_MAP[ns]
		return ns, tag

	def _parse_value(self, el):
		""" Extract the metadata value from an element. """
		if el.find(RDF_NS+'Bag') is not None:
			value = []
			for li in el.findall(RDF_NS+'Bag/'+RDF_NS+'li'):
				value.append(li.text)
		elif el.find(RDF_NS+'Seq') is not None:
			value = []
			for li in el.findall(RDF_NS+'Seq/'+RDF_NS+'li'):
				value.append(li.text)
		elif el.find(RDF_NS+'Alt') is not None:
			value = {}
			for li in el.findall(RDF_NS+'Alt/'+RDF_NS+'li'):
				value[li.get(XML_NS+'lang')] = li.text
		else:
			value = el.text
		return value


def xmp_to_dict(xmp):
	""" Shorthand function for parsing an XMP string into a python
	dictionary. """
	return XmpParser(xmp).meta


if __name__ == '__main__':
	main()
