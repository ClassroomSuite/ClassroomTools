import argparse

from classroom_tools import github_utils
from classroom_tools.exceptions import *

parser = argparse.ArgumentParser()
parser.add_argument(
    '--token',
    required=True,
    help='GitHub personal access token with repo and workflow permissions'
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
    '--event_type',
    default='Manual trigger',
    help='Event name'
)

if __name__ == '__main__':
    msg = 'Triggering workflows'
    padding = (50 - len(msg) // 2) * '#' + ' '
    print(4 * '\n' + padding + msg + padding[::-1])
    args = parser.parse_args()
    if args.token == '':
        raise EmptyToken(permissions='repo, workflow')
    num_success = 0
    num_fail = 0
    repositories = github_utils.get_students_repositories(
        token=args.token,
        org_name=args.org_name,
        repo_filter=args.repo_filter
    )
    for repo in repositories:
        success = repo.create_repository_dispatch(event_type=args.event_type)
        if success:
            num_success += 1
        else:
            num_fail += 1
        status = 'Succes' if success else 'Failed'
        print(f'{status}\t\t{repo.name}')
    print('\nSummary:')
    print(f'\tNumber of successful repository_dispatch events: {num_success}')
    print(f'\tNumber of failed: {num_fail}')
    if num_fail != 0:
        raise Exception('Couldn\'t trigger all workflows')
