#!/usr/bin/env python

import os

from graph import DiGraph

# List of files in the graphml folder
files = os.listdir('graphml')

# Created graphs
graphs = []

for file in files:
    if not file.endswith(".graphml"):
        continue

    try:
        graphs.append((file, DiGraph.from_graphml(f"graphml/{file}")))
    except Exception as e:
        print(f"Error for {file}: {e}")

node_counts = 0
for n, g in graphs:
    # Criteria which graphs are not extracted to be used for simulation
    if len(g.nodes()) > 50:
        continue

    node_counts += 1

    # print(f"[{n}] nodes={len(g.nodes())}, edges={len(g.edges())}")
    # with open('tmp/interesting_graphs.txt', 'a') as fh:
    #     fh.write(f"{n}\n")
print(node_counts)
