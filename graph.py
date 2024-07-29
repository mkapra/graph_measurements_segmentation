from dataclasses import dataclass
from itertools import product, chain
from random import sample
import copy
import matplotlib.pyplot as plt
import networkx as nx
import random

def calc_diff(first, second):
    """Returns the procentual change between first and second.
    """
    if first == 0:
        return 0
    return round(((second/first) - 1) * 100, 5)

def print_res(name, before, after):
    """Prints a given metric with a before and after value
    """
    diff = calc_diff(before, after)
    print(f"[{name}] Before: {before}, After: {after} => {diff}%")


def before_after_calculations(graph_desc_before,
                              graph_desc_after,
                              G_before,
                              G_after,
                              print_calc=False):
    """Calculate different metrics for two graphs (before and after simulation)
    """
    calcs = {
        'before': {
            'enice': G_before.enice(),
            'tinr': G_before.tinr(),
            'avod': G_before.avod(),
            'ac': G_before.ac(),
            'clustercoeff': nx.transitivity(G_before),
            'cd': G_before.cd(),
            'mpl': G_before.mpl(),
        },
        'after': {
            'enice': G_after.enice(),
            'tinr': G_after.tinr(),
            'avod': G_after.avod(),
            'ac': G_after.ac(),
            'clustercoeff': nx.transitivity(G_after),
            'cd': G_after.cd(),
            'mpl': G_after.mpl(),
        },
    }

    if not print_calc:
        return calcs

    print(f"\nBefore: {graph_desc_before}, After: {graph_desc_after}")
    print_res('ENICE', calcs['before']['enice'], calcs['after']['enice'])
    print_res(
        'Clustering coefficient',
        calcs['before']['clustercoeff'],
        calcs['after']['clustercoeff']
    )
    print_res('TINR', calcs['before']['tinr'], calcs['after']['tinr'])
    print_res('AVOD', calcs['before']['avod'], calcs['after']['avod'])
    print_res('AC', calcs['before']['ac'], calcs['after']['ac'])
    print_res('CD', calcs['before']['cd'], calcs['after']['cd'])
    print_res('MPL', calcs['before']['mpl'], calcs['after']['mpl'])

    return calcs


@dataclass
class Rule:
    src: str
    dst: str
    # Amount of services that are allowed between src and dst
    amount_services: int


class DiGraph(nx.DiGraph):
    def remove_zero_edges(self):
        """Removes all edges from the graph with weight == 0 and returns it
        """
        G = copy.deepcopy(self)
        edges = [
            (src, dst) for src, dst, attrs in G.edges(data=True)
            if int(attrs["weight"]) == 0
        ]
        le_ids = list(e[:2] for e in edges)
        G.remove_edges_from(le_ids)
        return G

    def simulate_traffic(self,
                         amount_of_rules=10,
                         amount_of_attacks=1,
                         rand_ports=[]):
        """Simulates random rules on a given network graph

        Parameters
        ----------
        amount_of_rules : int
            This number controls the number of paths that are randomly picked
            in the given graph.
        amount_of_attacks : int
            Defines the number of attacks that should be simulated. One attack
            reduces the weights on the paths between the two random picked
            nodes by one.
        rand_ports : [int]
            In each iteration of amount_of_rules there is generated a random
            number which is added to the weights of the edges between the
            random selected nodes. When comparing two graphs it may be
            interesting to test with the same amount of allowed services in the
            network. Because of that this parameter allows to pass some weights
            generated beforehand.
        """
        stats = dict()
        stats['before'] = {}
        stats['after'] = {}
        stats['attack'] = {}
        for src_node, dst_node in self.edges():
            nx.set_edge_attributes(self, {(src_node, dst_node): {"weight": 0}})

        nodes = []
        for i in range(amount_of_rules):
            first, second = sample(list(self.nodes()), 2)
            nodes.append((first, second))
            if len(rand_ports) == 0:
                self.apply_rules([
                    Rule(first, second, random.randrange(1, 65535))
                ])
            else:
                self.apply_rules([
                    Rule(first, second, sample(rand_ports, 1)[0])
                ])
        stats['traffic_nodes'] = nodes
        stats['before']['edgecount_with_zero'] = len(self.edges())
        self = self.remove_zero_edges()
        stats['before']['edgecount'] = len(self.edges())
        stats['before']['edges'] = str(self.edges(data=True))

        G_after = copy.deepcopy(self)
        for i in range(amount_of_attacks):
            rand_nodes = sample(nodes, 1)[0]
            stats['attack']['src'] = rand_nodes[0]
            stats['attack']['dst'] = rand_nodes[1]
            G_after.apply_rules([Rule(rand_nodes[0], rand_nodes[1], -1)])

        stats['after']['edgecount_with_zero'] = len(self.edges())
        G_after = G_after.remove_zero_edges()
        stats['after']['edgecount'] = len(G_after.edges())
        stats['before']['edges'] = str(G_after.edges(data=True))
        return self, G_after, stats

    @staticmethod
    def from_dot(filename):
        return DiGraph(nx.nx_pydot.read_dot(filename))

    @staticmethod
    def from_graphml(filename):
        return DiGraph(nx.read_graphml(filename))

    def apply_rules_from_file(self, filename):
        """Wrapper for parsing rules from a file and applying them to the graph

        The file is parsed line by line. A line should have the following
        format:
            # xxx - comment
            pc1 -> pc2 - One connection between pc1 and pc2 is allowed
            pc1 -> pc2 : 1234 - 1234 connections between pc1 and pc2 are
                                allowed
        """
        with open(filename, 'r') as fh:
            lines = [line.rstrip() for line in fh]

        rules = []
        for line in lines:
            if line.startswith('#') or len(line) == 0:
                continue

            try:
                from_node, rest = line.split(' -> ')
                to_node, weight = rest.split(':')
                rules.append(
                    Rule(from_node, to_node.rstrip(), int(weight.rstrip()))
                )
            except Exception:
                rules.append(Rule(*line.split(' -> '), 1))

        self.apply_rules(rules)
        return self

    def apply_rules(self, rules: [Rule]):
        """Applies given rules on the graph.

        Adds given weight of rule to weight of graph on the paths between the
        two hosts specified in the rule.
        """

        for rule in rules:
            applied_paths = []
            applied_rev_paths = []
            paths = list(nx.all_simple_paths(self, rule.src, rule.dst))
            reverse_paths = [path[::-1] for path in paths]
            for path, reverse_path in zip(paths, reverse_paths):
                for i, (node, rev_node) in enumerate(zip(path, reverse_path)):
                    if i == len(path) - 1:
                        break

                    to_node = path[i + 1]
                    to_rev_node = reverse_path[i + 1]

                    # Do not count up the weight on a edge twice if the
                    # different paths have similar partial paths
                    if (node, to_node) not in applied_paths:
                        applied_paths.append((node, to_node))
                        self[node][to_node]['weight'] = \
                            str(int(self[node][to_node]['weight']) + rule.amount_services)

                    if (rev_node, to_rev_node) not in applied_rev_paths:
                        applied_rev_paths.append((rev_node, to_rev_node))
                        self[rev_node][to_rev_node]['weight'] = \
                            str(int(self[rev_node][to_rev_node]['weight']) + rule.amount_services)

        return self

    def enice(self):
        """Enterprise Network Internal Connectivity Exposure
        """
        return DiGraph._sum_weights(self)

    def mpl(self):
        """Mean of shortest path lengths
        """
        paths = self.lsp()
        return (1/len(paths)) * sum([len(path) for path in paths])

    def tinr(self):
        """Transitive Internal Network Reachability
        """
        g = self.remove_zero_edges()
        transitive_graph = nx.transitive_closure(g, reflexive=None)
        return len(transitive_graph.edges())

    def avod(self):
        """Average Out-Degree
        """
        def calc(len_nodes, out_degrees):
            return (1/len_nodes) * sum(out_degrees)

        G = copy.deepcopy(self)
        # G.remove_zero_edges()

        return calc(
                len(G.nodes()),
                [out for (n, out) in list(G.out_degree())]
        )

    def ac(self):
        """Average Closeness
        """
        return (1/len(self.nodes())) * sum([self.cl(node) for node in self.nodes()])

    def cl(self, src_node):
        """Closeness centrality
        """
        all_nodes = [node for node in self.nodes()]
        node_lens = []
        for node in all_nodes:
            if node == self.nodes(node):
                continue

            try:
                node_lens.append(
                    len(nx.shortest_path(self, source=src_node, target=node))
                )
            except nx.exception.NetworkXNoPath:
                continue

            return 1/sum(node_lens)

    def cd(self):
        """Connectivity Graph Diameter
        """
        return len(max(self.lsp(), key=lambda k: len(k)))

    def lsp(self):
        """List of shortest paths
        """
        res = nx.all_pairs_shortest_path(self)
        return list(chain(*[list(paths.values()) for paths in [dsts for _, dsts in res]]))

    def draw_to_svg(self):
        """Saves the graph to a svg file
        """
        pos = nx.spring_layout(self, seed=7)

        nx.draw_networkx_nodes(self, pos, node_size=700)
        nx.draw_networkx_edges(self,
                               pos,
                               edgelist=[(u, v) for (u, v) in self.edges()],
                               width=3)
        nx.draw_networkx_labels(self, pos)
        edge_labels = nx.get_edge_attributes(self, 'weight')
        nx.draw_networkx_edge_labels(self, pos, edge_labels)

        ax = plt.gca()
        ax.margins(0.08)
        plt.tight_layout()
        plt.savefig('graph.svg')

    def _sum_weights(G):
        return sum(
            [int(x) for x in nx.get_edge_attributes(G, 'weight').values()]
        )
