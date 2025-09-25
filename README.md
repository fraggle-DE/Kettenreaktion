# Kettenreaktion
Script zur Erstellung Kettenreaktions-SVG und -PDF (Original von rkschlotte)

## Voraussetzungen
1. Getestet wurde unter Linux (Lubuntu 22.04), für das folgende Installationen notwendig sind:
```
sudo apt install graphviz python3 librsvg2-bin
pip install svgutils
```

(librsvg2-bin - enthält rsvg-convert zur Konvertierung der .svg Dateien)  
(svgutils - wird im Pythonscript implant_legend als Modul importiert)


2. Für den Zugriff auf die OKAPI muss ein API-Key (es wird Authentication Level 1 benutzt) angefordert werden.
Informationen zur OKAPI gibt es [hier](https://www.opencaching.de/okapi/introduction.html)


3. Der OKAPI-Key muss dem System bekannt gemacht werden. Hier die dauerhafte Methode, die auch einen Neustart übersteht: In der Datei $HOME/.bashrc folgende Zeile am Ende einfügen ('xxxxxxxxxx' durch den Consumer Key ersetzen) und ggf. offene Shells schließen und neu öffnen:

```
export OKAPI_CONSUMER_KEY=xxxxxxxxxx
```


## Script starten und Grafiken/PDFs erzeugen
Es gibt ein Kommando, das alle einzelnen Kommandos enthält. Es aktualisiert gegebenenfalls die OKAPI-Daten, erstellt SVGs und PDFs und öffnet sie:
```
make all
```

