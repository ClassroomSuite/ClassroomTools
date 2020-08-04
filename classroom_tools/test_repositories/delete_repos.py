import argparse

from classroom_tools import github_utils

parser = argparse.ArgumentParser('Create test repositories')
parser.add_argument(
    '--token',
    required=True,
    help='GitHub personal access token with delete_repo permissions'
)
parser.add_argument(
    '--org_name',
    required=True,
    help='GitHub organization with student repositories (for multiples student repositories)'
)
parser.add_argument(
    '--repo_filter',
    required=True,
    help='Prefix to filter repositories for as given assignment or exercise (for multiples student repositories)'
)


def delete_repos(token, org_name, repo_filter):
    repos = github_utils.get_students_repositories(token=token, org_name=org_name, repo_filter=repo_filter)
    for repo in repos:
        print(f'Deleting: {repo.full_name}')
        repo.delete()


def main(args):
    print('\n\n' + 'Deleting test repositories'.center(80, '='))
    args = parser.parse_args(args)
    print('Args:\n' + ''.join(f'\t{k}: {v}\n' for k, v in vars(args).items()))
    delete_repos(
        token=args.token,
        org_name=args.org_name,
        repo_filter=args.repo_filter
    )


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
