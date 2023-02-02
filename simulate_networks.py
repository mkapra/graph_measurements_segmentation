#!/usr/bin/env python

from graph import DiGraph, before_after_calculations
import json
import threading
import random


def read_graphml_files():
    with open('tmp/interesting_graphs.txt') as fh:
        lines = [line.rstrip() for line in fh]

    return [(line, DiGraph.from_graphml(f"graphml/{line}")) for line in lines]


def process_graph(name, G, results):
    print(f"-- Processing graph {name}")
    rand_ports = [random.randrange(1, 65535) for i in range(50)]
    G_simulation, G_attack, stats = G.simulate_traffic(amount_of_rules=50, rand_ports=rand_ports)
    print("Finished processing")

    results.append(
        (
            before_after_calculations(
                f"{name} simulated",
                f"{name} simulated + attack",
                G_simulation,
                G_attack
            ),
            stats
        )
    )


def main():
    graphs = read_graphml_files()
    thread_list = []
    results = []

    for name, graph in graphs:
        thread = threading.Thread(target=process_graph, args=(name, graph, results))
        thread_list.append(thread)

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()

    # results = [process_graph(name, graph) for name, graph in graphs]
    with open('tmp/networks_simulation_results_realistic.json', 'a') as fh:
        fh.write(json.dumps(results))


if __name__ == "__main__":
    main()
