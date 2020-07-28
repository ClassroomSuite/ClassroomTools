import argparse

import github

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
    '--event_type',
    default='Manual trigger',
    help='Event name'
)

if __name__ == '__main__':
    args = parser.parse_args()
    g = github.Github(login_or_token=args.token)
    org = g.get_organization(login=args.org_name)
    num_success = 0
    num_fail = 0
    for repo in org.get_repos():
        if args.repo_filter in repo.name:
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
