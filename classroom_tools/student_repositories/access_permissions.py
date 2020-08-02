import argparse

from colorama import Fore, Style

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
    help='Prefix to filter repositories for a given assignment or exercise'
)
parser.add_argument(
    '--new_permission_level',
    choices=['pull', 'push'],
    default='pull',
    help='Pull (read-only) or push (read, write)'
)


def confirm_changes(repositories, new_permission):
    num_ok = 0
    num_fail = 0
    for repo in repositories:
        print(f'Repo: {repo.full_name}')
        for col in repo.get_collaborators(affiliation='all'):
            if not col.permissions.admin:
                if col.permissions.pull and new_permission == 'pull':
                    print(f'{Fore.GREEN}\tCollaborator: {col.login}\tPermission: pull')
                    num_ok += 1
                elif col.permissions.push and new_permission == 'push':
                    print(f'{Fore.GREEN}\tCollaborator: {col.login}\tPermission: push')
                    num_ok += 1
                else:
                    print(f'{Fore.RED}\tCollaborator: {col.login}\n{Fore.RED}Permissions: {col.permissions}')
                    num_fail += 1
        for team in repo.get_teams():
            if team.permission == new_permission:
                print(f'{Fore.GREEN}\tTeam: {team.name}\tPermission: {team.permission}')
                num_ok += 1
            else:
                print(f'{Fore.RED}\tTeam: {team.name}\t Permission: {team.permission}')
                num_fail += 1
    print('\nSummary:')
    print(f'\tTotal number of repositories: {len(repositories)}')
    print(f'\tTotal number of successful permission changes: {num_ok}')
    print(f'\tTotal number of failed permission changes: {num_fail}')
    if num_fail != 0:
        raise Exception('Couldn\'t apply permission changes')


def apply_changes(repositories, new_permission):
    for repo in repositories:
        for col in repo.get_collaborators(affiliation='all'):
            if not col.permissions.admin:
                repo.add_to_collaborators(col, permission=new_permission)
        for team in repo.get_teams():
            team.set_repo_permission(repo=repo, permission=new_permission)


def main(args):
    print('\n\n' + 'Changing access permissions'.center(80, '='))
    args = parser.parse_args(args)
    print('Args:\n' + ''.join(f'\t{k}: {v}\n' for k, v in vars(args).items()))
    if args.token == '':
        raise EmptyToken(permissions='repo')
    try:
        repositories = github_utils.get_students_repositories(
            token=args.token,
            org_name=args.org_name,
            repo_filter=args.repo_filter
        )
        apply_changes(repositories=repositories, new_permission=args.new_permission_level)
        confirm_changes(repositories=repositories, new_permission=args.new_permission_level)
    except Exception as e:
        print(e)
        exit(1)


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
    print(Style.RESET_ALL)
