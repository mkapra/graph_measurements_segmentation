#!/usr/bin/env python

import json
import sys
from statistics import mean
from math import sqrt

from graph import calc_diff


def parse_json(filename):
    with open(filename) as fh:
        return json.loads(fh.read())

def filter_results(results, key):
    return [
        (result['before'][key], result['after'][key])
        for result, _ in results
    ]

def calculations(results):
    mean_res = mean([after - before for before, after in results])
    var_before = (1 / (len(results) - 1)) * sum([(before - mean_res)**2 for before, _ in results])
    var_after = (1 / (len(results) - 1)) * sum([(after - mean_res)**2 for _, after in results])

    results = {
        'mean': mean_res,
        'mean_diff': mean([calc_diff(before, after) for before, after in results]),
        'before': {
            'variance': var_before,
            'stddeviation': sqrt(var_before),
            'min': min([before for before, _ in results]),
            'max': max([before for before, _ in results]),
        },
        'after': {
            'variance': var_after,
            'stddeviation': sqrt(var_after),
            'min': min([after for _, after in results]),
            'max': max([after for _, after in results]),
        },
    }

    return results


def get_before_after(calcs, key):
    return f"{calcs['before'][key]} {calcs['after'][key]}"


def print_val(metric_name, descr, val):
    print(f"[{metric_name} {descr}]: {val}")


def print_calculations(calcs: dict, metric_name: str):
    print(f"--- {metric_name}")
    print_val(
        metric_name,
        'mean difference',
        f"{calcs['mean']} {calcs['mean_diff']}%"
    )
    print_val(
        metric_name,
        'variance before/after',
        get_before_after(calcs, 'variance')
    )
    print_val(
        metric_name,
        'min value before/after',
        get_before_after(calcs, 'min')
    )
    print_val(
        metric_name,
        'max value before/after',
        get_before_after(calcs, 'max')
    )
    print_val(
        metric_name,
        'standard deviation before/after',
        get_before_after(calcs, 'stddeviation')
    )


def print_means(results):
    print("-- Means of all metrics")
    print(f"ENICE: {calculations(filter_results(results, 'enice'))['mean']}")
    print(f"TINR: {calculations(filter_results(results, 'tinr'))['mean']}")
    print(f"AVOD: {calculations(filter_results(results, 'avod'))['mean']}")
    print(f"AC: {calculations(filter_results(results, 'ac'))['mean']}")
    print(f"Global cluster coefficient: {calculations(filter_results(results, 'clustercoeff'))['mean']}")
    print(f"CD: {calculations(filter_results(results, 'cd'))['mean']}")
    print(f"MPL: {calculations(filter_results(results, 'mpl'))['mean']}")


def calc_metrics(results):
    print_calculations(calculations(filter_results(results, 'enice')), 'ENICE')
    print_calculations(calculations(filter_results(results, 'tinr')), 'TINR')
    print_calculations(calculations(filter_results(results, 'avod')), 'AVOD')
    print_calculations(calculations(filter_results(results, 'ac')), 'AC')
    print_calculations(
        calculations(filter_results(results, 'clustercoeff')),
        'Global Cluster coefficient'
    )
    print_calculations(calculations(filter_results(results, 'cd')), 'CD')
    print_calculations(calculations(filter_results(results, 'mpl')), 'MPL')


def main():
    try:
        results = parse_json(sys.argv[1])
    except IndexError:
        print('Please provide a filename')
        sys.exit(1)

    # results_enice_before = [before for before, _ in filter_results(results, 'enice')[:5]]
    # results_enice_after = [after for _, after in filter_results(results, 'enice')[:5]]
    # print(min(results_enice_before))
    # print(min(results_enice_after))

    # import matplotlib.pyplot as plt # plt = pyplot

    # enices = []
    # for metrics, stats in results:
    #     enice_before, enice_after = metrics['before']['enice'], metrics['after']['enice']
    #     edgecount = stats['before']['edgecount']

    #     enices.append((edgecount, (enice_before, enice_after)))

    # plt.scatter([edgecount for edgecount, _ in enices], [enice_before - enice_after for _, (enice_before, enice_after) in enices])
    # # points = [(i, i) for i in range(0, max(results_enice_before), 1000)]
    # # plt.plot([x for x, _ in points], [y for _, y in points])
    # plt.show()



    # print(enices)

    # plt.plot(results_enice_before, results_enice_after, 'o')
    # points = [(i, i) for i in range(0, max(results_enice_before), 1000)]
    # plt.plot([x for x, _ in points], [y for _, y in points])
    # plt.show()


    calc_metrics(results)
    print_means(results)


if __name__ == "__main__":
    main()
