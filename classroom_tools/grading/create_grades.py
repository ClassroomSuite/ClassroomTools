#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json
import os

parser = argparse.ArgumentParser()
parser.add_argument(
    '--test_associations_path',
    required=True,
    help='Path to test_associations.json'
)


def get_tests_results(log_file):
    f = open(log_file)
    results = []
    for line in f.readlines():
        test_fn_name, *_ = line.split(' ')
        if ' ok' in line:
            results.append({'func_name': test_fn_name, 'passing': True})
        elif ' ERROR' in line or ' FAIL' in line:
            results.append({'func_name': test_fn_name, 'passing': False})
        else:
            break
    f.close()
    return results


def add_tests_info(results, tests_associations_file):
    f = open(tests_associations_file, encoding='UTF-8')
    tests_associations = json.load(f)
    for result in results:
        test = tests_associations[result['func_name']]
        result['test_name'] = test['name']
        result['points'] = test['points']
    f.close()


def main(args):
    print('\n\n' + 'Creating grades'.center(80, '='))
    args = parser.parse_args(args)
    print('Args:\n' + ''.join(f'\t{k}: {v}\n' for k, v in vars(args).items()))
    dir_path = os.path.realpath(os.curdir)
    log_file = os.path.join(dir_path, 'logs/tests_results.txt')
    grades_file = os.path.join(dir_path, 'logs/grades.json')
    tests_associations_file = os.path.join(dir_path, args.test_associations_path)

    results = get_tests_results(log_file)
    add_tests_info(results, tests_associations_file)
    with open(grades_file, 'w', encoding='UTF-8') as f:
        json.dump(results, f)


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
