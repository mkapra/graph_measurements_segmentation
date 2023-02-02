# Connectivity Graph Measurements

This project provides some scripts to be able to measure the metrics defined in
the paper "Towards a Zero-Trust Micro-segmentation Network Security Strategy:
An Evaluation Framework" [^1] on different connectivity graphs.

## Connectivity Graph

A connectivity graph represents a network graph with weights on the edges.
The weights on the edges represent the amount of the services that are allowed
in the direction of the edge [^1].

## Structure of this repository

### graph.py

[graph.py](./graph.py) is not a script. It is the library that is used by
nearly every script in this repository. It provides the methods on the graphs
for calculating the metrics and some other helping functions.

## Directories

The directories are structured as follows:

* [dot/](./dot/): Contains some graphs in dot format
* [graphml/](./graphml/): All the graphs in this folder are downloaded from the
  topology zoo [^2]
* [tmp/](./tmp/): In this directory all the results produced by the scripts are stored
* [rules/](./rules/): This directory contains some sample rules that can be applied to
  the connectity graphs.

### General scripts

[graphml/download_graphml.sh](./graphml/download_graphml.sh): Downloads all the
networks from the internet topology zoo [^2] in graphml format.

[extract_interesting_graphs.py](./extract_interesting_graphs.py): Filters the
downloaded topology graphs based on some metrics and stores the filtered graphs
into `./tmp/interesting_graphs.txt`

[simulate_network.py](./simulate_network.py): Takes each graph in
`./tmp/interesting_graphs.txt` and simulates some traffic on it. In the end a
file `./tmp/networks_simulation_results.json` is generated with the calculated
metrics of the paper [^1] and some additional information.

[evaluate_sim_results.py](./evaluate_sim_results.py): Based on the variable
`RESULT_FILENAME` this script evaluates the results produced by
[simulate_networks.py](./simulate_networks.py)

### Example scripts for specific networks

[protect_net_measurements.py](./protect_net_measurements.py): This script
evaluates the metrics based on the network
[dot/logic_flat_connected.dot](./dot/logic_flat_connected.dot).

[^1]: https://ieeexplore.ieee.org/document/9789888
[^2]: http://www.topology-zoo.org/dataset.html
