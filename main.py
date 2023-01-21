#!/usr/bin/env python

import networkx as nx

from graph import DiGraph


def calc_diff(first, second):
    if first == 0:
        return 0
    return round(((second/first) - 1) * 100, 3)


def print_res(name, before, after):
    diff = calc_diff(before, after)
    print(f"[{name}] Before: {before}, After: {after} => {diff}%")


def before_after_calculations(G_before, G_after):
    print_res('ENICE', G_before.enice(), G_after.enice())
    print_res(
        'Clustering coefficient',
        nx.transitivity(G_before),
        nx.transitivity(G_after)
    )
    print_res('TINR', G_before.tinr(), G_after.tinr())
    print_res('AVOD', G_before.avod(), G_after.avod())
    print_res('AC', G_before.ac(), G_after.ac())


def main():
    G_flat = DiGraph.from_dot('dot/logic_flat_connected.dot')

    G_segmentation = DiGraph\
        .from_dot('dot/network.dot')\
        .apply_rules_from_file('rules/allow_all.rules')
    G_segmentation.apply_rules_from_file('rules/allow_all.rules')

    G_before = DiGraph\
        .from_dot('dot/network.dot')\
        .apply_rules_from_file('rules/restricted_http_ssh.rules')

    G_segmentation_attack = DiGraph\
        .from_dot('dot/network.dot')\
        .apply_rules_from_file('rules/restricted_http_ssh_attack.rules')

    print(f"{'*' * 20} From flat network")
    print("Before: Flat & all allowed, After: Segmentation & all allowed")
    before_after_calculations(G_flat, G_segmentation)
    print("\nBefore: Flat & all allowed, After: Segmentation & specific allowed")
    before_after_calculations(G_flat, G_before)
    print("\nBefore: Flat & all allowed, After: Segmentation & specific allowed + attack denied")
    before_after_calculations(G_flat, G_segmentation_attack)

    print(f"\n{'*' * 20} From segmentation & all allowed")
    print("Before: Segmentation & all allowed, After: Segmentation & specific allowed")
    before_after_calculations(G_segmentation, G_before)
    print("\nBefore: Segmentation & all allowed, After: Segmentation & specific allowed + attack denied")
    before_after_calculations(G_segmentation, G_segmentation_attack)

    print(f"\n{'*' * 20} From Segmentation & specific allowed")
    print("Before: Segmentation & specific allowed, After: Segmentation & specific allowed + attack denied")
    before_after_calculations(G_before, G_segmentation_attack)


if __name__ == "__main__":
    main()
