import argparse
import json

import requests
from colorama import Fore

from classroom_tools import github_utils

parser = argparse.ArgumentParser('Verify that a the repo is a template')
parser.add_argument(
    '--token',
    required=True,
    help='GitHub personal access token with repo permissions'
)
parser.add_argument(
    '--repo_fullname',
    required=True,
    help='Repo fullname in format: OrgName/RepoName'
)


def main(args):
    print('\n\n' + 'Verifying access to secrets'.center(80, '='))
    args = parser.parse_args(args)
    print('Args:\n' + ''.join(f'\t{k}: {v}\n' for k, v in vars(args).items()))
    github_utils.verify_token(args.token)
    res = requests.get(
        url=f'https://api.github.com/repos/{args.repo_fullname}',
        headers={
            'Authorization': f'token {args.token}',
            'Accept': 'application/vnd.github.baptiste-preview+json'
        }
    )
    is_template = json.JSONDecoder().decode(res.text)['is_template']
    if is_template:
        print(f'{Fore.GREEN} Repo is a template: {args.repo_fullname}')
    else:
        raise Exception(f'{Fore.RED} Repo is not a template: {args.repo_fullname}')


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
