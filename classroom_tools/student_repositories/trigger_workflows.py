import argparse

from colorama import Fore

from classroom_tools import github_utils

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


def main(args):
    print('\n\n' + 'Triggering workflows'.center(80, '='))
    args = parser.parse_args(args)
    print('Args:\n' + ''.join(f'\t{k}: {v}\n' for k, v in vars(args).items()))
    github_utils.verify_token(args.token)
    num_success = 0
    num_fail = 0
    repositories = github_utils.get_students_repositories(
        token=args.token,
        org_name=args.org_name,
        repo_filter=args.repo_filter
    )
    print('Triggering workflows in repos:')
    for repo in repositories:
        success = repo.create_repository_dispatch(event_type=args.event_type)
        if success:
            num_success += 1
            print(f'{Fore.GREEN}\t{repo.name}')
        else:
            num_fail += 1
            print(f'{Fore.RED}\tFAILED {repo.name}')

    print('\nSummary:')
    print(f'\tNumber of successful repository_dispatch events: {num_success}')
    print(f'\tNumber of failed: {num_fail}')
    if num_fail != 0:
        raise Exception(f'{Fore.RED}Couldn\'t trigger all workflows')


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
