#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json
import os

import requests

parser = argparse.ArgumentParser()
parser.add_argument(
    '--access_token',
    default='',
    help='Make sure your repository has access to YOUR_ORG\'s Secrets.DB_TOKEN'
)
parser.add_argument(
    '--firebase_real_time_db_url',
    required=True,
    help='Firebase Realtime database url to patch with repo grades'
)
parser.add_argument(
    '--github_repo',
    required=True,
    help='GitHub repo name'
)

if __name__ == '__main__':
    args = parser.parse_args()
    dir_path = os.path.realpath(os.curdir)
    print(dir_path)
    grades_file = os.path.join(dir_path, 'logs/grades.json')
    with open(grades_file, 'r', encoding='UTF-8') as f:
        grades = json.load(f)
        test_names = [result['test_name'] for result in grades]
        test_results = [
            {
                'points': int(result['points']),
                'passing': result['passing']
            } for result in grades
        ]
        payload = {args.github_repo: dict(zip(test_names, test_results))}
        url = f'{args.firebase_real_time_db_url}?access_token={args.access_token}' if args.access_token != '' else args.firebase_real_time_db_url
        res = requests.patch(
            url,
            json=payload
        )
        print(res.text.encode('utf-8'))
