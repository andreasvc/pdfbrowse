mkdir -p static/files
if [ -d pdfjs/ ]; then
	cd pdfjs
	git pull
else
	git clone --depth 1 git://github.com/mozilla/pdf.js.git pdfjs
	cd pdfjs
fi
nodejs make generic \
&& cp -r build/generic/build/ build/generic/web/ ../static/
# minify etc.

