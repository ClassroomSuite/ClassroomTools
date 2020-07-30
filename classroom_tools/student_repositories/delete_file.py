import argparse

from classroom_tools import github_utils
from classroom_tools.exceptions import *

parser = argparse.ArgumentParser()
parser.add_argument(
    '--token',
    required=True,
    help='GitHub personal access token with repo permissions'
)
parser.add_argument(
    '--org_name',
    required=True,
    help='GitHub organization name'
)
parser.add_argument(
    '--repo_filter',
    required=True,
    help='Prefix to filter repositories for as given assignment or exercise'
)
parser.add_argument(
    '--path',
    default='',
    help='A path to a file delete from students repositories'
)

if __name__ == '__main__':
    msg = 'Deleting file'
    padding = (50 - len(msg) // 2) * '#' + ' '
    print(4 * '\n' + padding + msg + padding[::-1])
    args = parser.parse_args()
    if args.token == '':
        raise EmptyToken(permissions='repo')
    repositories = github_utils.get_students_repositories(
        token=args.token,
        org_name=args.org_name,
        repo_filter=args.repo_filter
    )
    num_repos = 0
    for repo in repositories:
        if args.repo_filter in repo.name:
            classroom_tools.github_utils.delete_file(repo, args.path)
        num_repos += 1
    print('\nSummary:')
    print(f'\tTotal number of repositories updated: {num_repos}')
