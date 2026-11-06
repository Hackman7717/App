#!/bin/sh
# Testkopie der App mit Zugang zu den internen Funktionen (window.__ev s=>eval(s) im Rahmen der App).
# Aufruf: ./mkt.sh <Checkout des Zweigs gh-pages> <Web-Ordner>   → <Web-Ordner>/AppT/
APP=${1:?Ordner mit index.html}; WWW=${2:?Web-Ordner}
rm -rf "$WWW/AppT" && mkdir -p "$WWW/AppT" && cp -r "$APP"/index.html "$APP"/sw.js "$APP"/manifest.webmanifest "$APP"/fonts "$APP"/icons "$WWW/AppT/"
python3 -I - "$WWW/AppT/index.html" <<'PY'
import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
a = "render();\nstoreInit();\n})();"
assert s.count(a) == 1, 'Ende der App nicht gefunden'
s = s.replace(a, "window.__ev=s=>eval(s);\n" + a)
open(p, 'w', encoding='utf-8').write(s)
PY
echo "Testkopie in $WWW/AppT"
