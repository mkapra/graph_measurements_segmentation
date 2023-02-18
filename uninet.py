#!/usr/bin/env python

from graph import DiGraph, before_after_calculations


def main():
    G_before = DiGraph.from_dot('./dot/uninet.dot')
    G_before.apply_rules_from_file('./rules/uninet.rules')
    G_after = DiGraph.from_dot('./dot/uninet.dot')
    G_after.apply_rules_from_file('./rules/uninet_attack.rules')
    G_after_complete = DiGraph.from_dot('./dot/uninet.dot')
    G_after_complete.apply_rules_from_file('./rules/uninet_attack_complete.rules')

    before_after_calculations(
        "Uninet",
        "Uninet + Attack",
        G_before,
        G_after,
        print_calc=True
    )

    before_after_calculations(
        "Uninet",
        "Uninet + Attack + Block Complete",
        G_before,
        G_after_complete,
        print_calc=True
    )

    print(G_before.get_edge_data('client1sub1', 'swsub1'))
    print(G_before.get_edge_data('client2sub1', 'swsub1'))
    print(G_before.get_edge_data('server1sub1', 'swsub1'))
    print(G_before.get_edge_data('swsub1', 'gateway'))
    print(G_before.get_edge_data('gateway', 'internet'))
    print('---')
    print(G_after.get_edge_data('client1sub1', 'swsub1'))
    print(G_after.get_edge_data('client2sub1', 'swsub1'))
    print(G_after.get_edge_data('server1sub1', 'swsub1'))
    print(G_after.get_edge_data('swsub1', 'gateway'))
    print(G_after.get_edge_data('gateway', 'internet'))
    print('---')
    print(G_after_complete.get_edge_data('client1sub1', 'swsub1'))
    print(G_after_complete.get_edge_data('client2sub1', 'swsub1'))
    print(G_after_complete.get_edge_data('server1sub1', 'swsub1'))
    print(G_after_complete.get_edge_data('swsub1', 'gateway'))
    print(G_after_complete.get_edge_data('gateway', 'internet'))


if __name__ == "__main__":
    main()
