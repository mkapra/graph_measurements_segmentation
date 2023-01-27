#!/usr/bin/env python

from graph import DiGraph, before_after_calculations


def main():
    G_flat = DiGraph.from_dot('dot/logic_flat_connected.dot')

    G_segmentation = DiGraph\
        .from_dot('dot/network.dot')\
        .apply_rules_from_file('rules/allow_all.rules')

    G_before = DiGraph\
        .from_dot('dot/network.dot')\
        .apply_rules_from_file('rules/restricted_http_ssh.rules')

    G_segmentation_attack = DiGraph\
        .from_dot('dot/network.dot')\
        .apply_rules_from_file('rules/restricted_http_ssh_attack.rules')

    print(f"{'*' * 20} From flat network")
    before_after_calculations(
        "Flat & all allowed",
        "Segmentation & all allowed",
        G_flat,
        G_segmentation,
        print_calc=True)
    before_after_calculations(
        "Flat & all allowed",
        "Segmentation & specific allowed",
        G_flat,
        G_before,
        print_calc=True)
    before_after_calculations(
        "Flat & all allowed",
        "Segmentation & specific allowed + attack denied",
        G_flat,
        G_segmentation_attack,
        print_calc=True)

    print(f"\n{'*' * 20} From segmentation & all allowed")
    before_after_calculations(
        "Segmentation & all allowed",
        "Segmentation & specific allowed",
        G_segmentation,
        G_before,
        print_calc=True)
    before_after_calculations(
        "Segmentation & all allowed",
        "Segmentation & specific allowed + attack denied",
        G_segmentation,
        G_segmentation_attack,
        print_calc=True)

    print(f"\n{'*' * 20} From Segmentation & specific allowed")
    before_after_calculations(
        "Segmentation & specific allowed",
        "Segmentation & specific allowed + attack denied",
        G_before,
        G_segmentation_attack,
        print_calc=True)


if __name__ == "__main__":
    main()
