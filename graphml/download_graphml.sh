#!/bin/bash

# Hole die Webseite
curl http://www.topology-zoo.org/dataset.html > dataset.html

# Suche nach allen GraphML-Links und speichere sie in einer Textdatei
grep -o 'href=.*\.graphml' dataset.html | awk -F '"' '{print $4}' > links.txt

# Lade jeden gefundenen Link herunter und speichere ihn im aktuellen Verzeichnis
while read link; do
  wget "http://www.topology-zoo.org/$link" -O ${link##*/}
done < links.txt
