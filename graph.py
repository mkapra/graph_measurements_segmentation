from dataclasses import dataclass
from random import sample
import copy
import matplotlib.pyplot as plt
import networkx as nx
import random


def calc_diff(first, second):
    if first == 0:
        return 0
    return round(((second/first) - 1) * 100, 5)


def print_res(name, before, after):
    diff = calc_diff(before, after)
    print(f"[{name}] Before: {before}, After: {after} => {diff}%")


def before_after_calculations(before_msg, after_msg, G_before, G_after, print_calc=False):
    calcs = {
        'before': {
            'enice': G_before.enice(),
            'tinr': G_before.tinr(),
            'avod': G_before.avod(),
            'ac': G_before.ac(),
            'clustercoeff': nx.transitivity(G_before),
        },
        'after': {
            'enice': G_after.enice(),
            'tinr': G_after.tinr(),
            'avod': G_after.avod(),
            'ac': G_after.ac(),
            'clustercoeff': nx.transitivity(G_after),
        },
    }

    if not print_calc:
        return calcs

    print(f"\nBefore: {before_msg}, After: {after_msg}")
    print_res('ENICE', calcs['before']['enice'], calcs['after']['enice'])
    print_res(
        'Clustering coefficient',
        calcs['before']['clustercoeff'],
        calcs['after']['clustercoeff']
    )
    print_res('TINR', calcs['before']['tinr'], calcs['after']['tinr'])
    print_res('AVOD', calcs['before']['avod'], calcs['after']['avod'])
    print_res('AC', calcs['before']['ac'], calcs['after']['ac'])

    return calcs


@dataclass
class Rule:
    src: str
    dst: str
    amount_services: int


class DiGraph(nx.DiGraph):
    def remove_zero_edges(self):
        G = copy.deepcopy(self)
        edges = [(src, dst) for src, dst, attrs in G.edges(data=True) if attrs["weight"] == 0]
        le_ids = list(e[:2] for e in edges)
        G.remove_edges_from(le_ids)
        return G

    def simulate_traffic(self, amount_of_traffic=10, amount_of_attacks=1, rand_ports=[]):
        for src_node, dst_node in self.edges():
            nx.set_edge_attributes(self, {(src_node, dst_node): {"weight": 0}})

        nodes = []
        for i in range(amount_of_traffic):
            first, second = sample(list(self.nodes()), 2)
            nodes.append((first, second))
            if len(rand_ports) == 0:
                self.apply_rules([Rule(first, second, random.randrange(1, 65535))])
            else:
                self.apply_rules([Rule(first, second, sample(rand_ports, 1)[0])])

        self = self.remove_zero_edges()

        G_after = copy.deepcopy(self)
        for i in range(amount_of_attacks):
            rand_nodes = sample(nodes, 1)[0]
            G_after.apply_rules([Rule(rand_nodes[0], rand_nodes[1], -1)])

        return self, G_after

    @staticmethod
    def from_dot(filename):
        return DiGraph(nx.nx_pydot.read_dot(filename))

    @staticmethod
    def from_graphml(filename):
        return DiGraph(nx.read_graphml(filename))

    def apply_rules_from_file(self, filename):
        with open(filename, 'r') as fh:
            lines = [line.rstrip() for line in fh]

        rules = []
        for line in lines:
            if line.startswith('#') or len(line) == 0:
                continue

            try:
                from_node, rest = line.split(' -> ')
                to_node, weight = rest.split(':')
                rules.append(Rule(from_node, to_node.rstrip(), int(weight.rstrip())))
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
            paths = list(nx.all_simple_paths(self, rule.src, rule.dst))
            for path in paths:
                for i, node in enumerate(path):
                    if i == len(path) - 1:
                        break

                    to_node = path[i + 1]

                    # Do not count up the weight on a edge twice if the
                    # different paths have similar partial paths
                    if (node, to_node) not in applied_paths:
                        applied_paths.append((node, to_node))
                        self[node][to_node]['weight'] = \
                            str(int(self[node][to_node]['weight']) + rule.amount_services)

        return self

    def enice(self):
        """Enterprise Network Internal Connectivity Exposure
        """
        return DiGraph._sum_weights(self)

    def mpl(self):
        """Mean of shortest paths
        """
        pass

    def tinr(self):
        """Transitive Internal Network Reachability
        """
        return DiGraph._sum_weights(nx.transitive_closure(self))

    def avod(self):
        """Average Out-Degree
        """
        def calc(len_nodes, out_degrees):
            return (1/len_nodes) * sum(out_degrees)

        G = copy.deepcopy(self)
        G.remove_zero_edges()

        return calc(
                len(G.nodes()),
                [out for (n, out) in list(G.out_degree())]
        )

    def ac(self):
        """Average closeness
        """
        def cl(start_node):
            sum_vertices_between = 0
            for end in list(filter(lambda n: start_node != n, self.nodes)):
                try:
                    sum_vertices_between += \
                        len([nx.shortest_path(self, start_node, end)][0]) - 2
                except nx.exception.NetworkXNoPath:
                    pass

            if sum_vertices_between == 0:
                return 0

            return 1 / sum_vertices_between

        return 1/len(self.nodes) * sum([cl(n) for n in self.nodes])

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
