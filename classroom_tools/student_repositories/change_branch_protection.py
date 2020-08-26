import argparse

from colorama import Fore

from classroom_tools import github_utils

parser = argparse.ArgumentParser(
    'Change branch protection')
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
    help='Prefix to filter repositories for a given assignment or exercise'
)
parser.add_argument(
    '--branch',
    required=True,
    help='Name of protected branch'
)
parser.add_argument(
    '--protect',
    choices=[True, False],
    type=bool,
    required=True,
    help='Protect branch'
)


def main(args):
    print('\n\n' + 'Changing branch protection'.center(80, '='))
    args = parser.parse_args(args)
    print('Args:\n' + ''.join(f'\t{k}: {v}\n' for k, v in vars(args).items()))
    github_utils.verify_token(args.token)
    repositories = github_utils.get_students_repositories(
        token=args.token,
        org_name=args.org_name,
        repo_filter=args.repo_filter
    )
    num_fail = 0
    for repo in repositories:
        print(f'Repo: {repo.full_name}')
        try:
            branch = repo.get_branch(args.branch)
            if args.protect:
                branch.edit_protection(
                    user_push_restrictions=['']
                )
            elif branch.protected:
                branch.remove_protection()
            else:
                pass
        except:
            num_fail += 1
    print('\nSummary:')
    print(f'\tTotal number of repositories: {len(repositories)}')
    print(f'\tTotal number failed: {num_fail}')
    if num_fail > 0:
        raise Exception(f'{Fore.RED}Couldn\'t change branch protections')


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
