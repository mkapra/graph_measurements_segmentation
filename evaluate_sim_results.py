#!/usr/bin/env python

import json
from statistics import mean
from math import sqrt

from graph import calc_diff


def parse_json():
    with open('tmp/networks_simulation_results_correct.json.2') as fh:
        return json.loads(fh.read())


def calc_enice(results):
    enice = [
        (result['before']['enice'], result['after']['enice'])
        for result in results
    ]
    mean_enice = mean([after - before for before, after in enice])
    diff_enice = mean([calc_diff(before, after) for before, after in enice])
    var_enice_before = (1 / (len(enice) - 1)) * sum([(before - mean_enice)**2 for before, x in enice])
    var_enice_after = (1 / (len(enice) - 1)) * sum([(after - mean_enice)**2 for x, after in enice])
    max_enice_before = max([before for before, _ in enice])
    max_enice_after = max([after for _, after in enice])
    min_enice_before = min([before for before, _ in enice])
    min_enice_after = min([after for _, after in enice])
    print(f"[ENICE_max] Before: {max_enice_before} After: {max_enice_after}")
    print(f"[ENICE_min] Before: {min_enice_before} After: {min_enice_after}")
    print(f"[ENICE_variance] Before: {var_enice_before} After: {var_enice_after}")
    print(f"[ENICE_stdabw] Before: {sqrt(var_enice_before)} After: {sqrt(var_enice_after)}")
    print(f"[ENICE_mean_diff] {mean_enice} => {diff_enice}%")


def main():
    results = parse_json()
    calc_enice(results)


if __name__ == "__main__":
    main()
