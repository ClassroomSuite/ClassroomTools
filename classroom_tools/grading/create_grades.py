#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os


def get_tests_results(log_file):
    f = open(log_file)
    results = []
    for line in f.readlines():
        test_fn_name, *_ = line.split(' ')
        if line.find('FAIL') != -1:
            results.append({'func_name': test_fn_name, 'passing': False})
        elif line.find('ok') != -1:
            results.append({'func_name': test_fn_name, 'passing': True})
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


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    log_file = os.path.join(dir_path, '../logs/tests_results.txt')
    grades_file = os.path.join(dir_path, '../logs/grades.json')
    tests_associations_file = os.path.join(dir_path, '../scripts/test_associations.json')
    readme_file = os.path.join(dir_path, '../README.md')
    results = get_tests_results(log_file)
    add_tests_info(results, tests_associations_file)
    with open(grades_file, 'w', encoding='UTF-8') as f:
        json.dump(results, f)
