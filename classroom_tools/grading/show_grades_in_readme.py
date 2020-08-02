#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os


def readme_head(prev_lines):
    split_index = -1
    for i, line in enumerate(prev_lines):
        if '# ' in line:
            split_index = i
            break
    head = prev_lines[:split_index]
    remaining_lines = prev_lines[split_index:]
    return head, remaining_lines


def results_section(grades):
    lines = [
        '## Résultats\n',
        'Score | Critères\n',
        '--- | ---\n'
    ]
    total_denominator = 0
    total_numerator = 0
    for result in grades:
        points = int(result['points'])
        name = result['test_name']
        total_denominator += points
        if result['passing']:
            total_numerator += points
            lines.append(f'{points}/{points} | {name}\n')
        else:
            lines.append(f'0/{points} | {name}\n')
    lines.append(f'{total_numerator}/{total_denominator} | **Total**\n')
    lines.append('\n')
    lines.append('[Voir détails](./logs/tests_results.txt) | [Rafraîchir](../../)')
    return lines


def readme_tail(remaining_lines, results_section_ending):
    tail = list(remaining_lines)
    for i, line in enumerate(remaining_lines):
        if results_section_ending in line:
            if i + 1 < len(remaining_lines):
                tail = remaining_lines[i + 1:]
    return tail


def update_readme(grades, readme_file):
    f = open(readme_file, encoding='UTF-8', mode='r')
    prev_lines = f.readlines()
    trailing_lines = []
    f.close()
    f = open(readme_file, encoding='UTF-8', mode='w')
    try:
        head, remaining_lines = readme_head(prev_lines)
        new_lines = results_section(grades)
        results_section_ending = new_lines[-1]
        tail = readme_tail(remaining_lines, results_section_ending)

        f.writelines(head + ['\n'] + new_lines + ['\n'] + tail)
    except Exception:
        print('Couldn\'t update README')
        f.writelines(prev_lines)
    f.close()


def main():
    print('\n\n' + 'Showing grades in README'.center(80, '='))
    dir_path = os.path.realpath(os.curdir)
    grades_file = os.path.join(dir_path, 'logs/grades.json')
    readme_file = os.path.join(dir_path, 'README.md')
    with open(grades_file, 'r', encoding='UTF-8') as f:
        grades = json.load(f)
        update_readme(grades, readme_file)


if __name__ == '__main__':
    main()
