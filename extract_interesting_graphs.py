#!/usr/bin/env python

import os

from graph import DiGraph

# Pfad zum Ordner GraphML
path = 'graphml'

# Liste aller Dateien im Ordner GraphML
files = os.listdir(path)

graphs = []

# Durchlaufe alle Dateien und gebe sie aus
for file in files:
    if not file.endswith(".graphml"):
        continue

    try:
        graphs.append((file, DiGraph.from_graphml(f"graphml/{file}")))
    except Exception as e:
        print(f"Error for {file}: {e}")

for n, g in graphs:
    if len(g.nodes()) > 50:
        continue

    print(f"[{n}] nodes={len(g.nodes())}, edges={len(g.edges())}")
    # with open('tmp/interesting_graphs.txt', 'a') as fh:
    #     fh.write(f"{n}\n")
