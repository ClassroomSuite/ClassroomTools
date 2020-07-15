import argparse

import github

parser = argparse.ArgumentParser()
parser.add_argument(
    '--TOKEN',
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
    '--new_permission_level',
    choices=['pull', 'push'],
    default='pull',
    help='Pull (read-only) or push (read, write)'
)


def get_repositories(args):
    g = github.Github(login_or_token=args.TOKEN)
    org = g.get_organization(login=args.org_name)
    for repo in org.get_repos():
        if repo.name.find(args.repo_filter) != -1:
            yield repo


def confirm_changes(args):
    num_ok = 0
    num_fail = 0
    for repo in get_repositories(args):
        for col in repo.get_collaborators(affiliation='all'):
            permission = repo.get_collaborator_permission(col)
            if permission != 'admin':
                if permission == 'read' and args.new_permission_level == 'pull':
                    print(f'Permission: pull\t {repo.name}/{col.login}')
                    num_ok += 1
                elif permission == 'write' and args.new_permission_level == 'push':
                    print(f'Permission: push\t {repo.name}/{col.login}')
                    num_ok += 1
                else:
                    print(f'\nERROR {repo.name}/{col.login}')
                    print(permission, end='\n\n')
                    num_fail += 1
    print('\nSummary:')
    print(f'\tTotal number of successful permission changes: {num_ok}')
    print(f'\tTotal number of failed permission changes: {num_fail}')
    if num_fail != 0:
        raise Exception('Couldn\'t apply permission changes')


def apply_changes(args):
    for repo in get_repositories(args):
        for col in repo.get_collaborators(affiliation='all'):
            prev_permission = repo.get_collaborator_permission(col)
            if prev_permission == 'read' or prev_permission == 'write':
                repo.add_to_collaborators(col, permission=args.new_permission_level)


if __name__ == '__main__':
    args = parser.parse_args()
    if args.TOKEN == '':
        print(f'TOKEN is empty')
    try:
        apply_changes(args)
        confirm_changes(args)
    except Exception as e:
        print('Verify that your personal access token is accessible and has repo permissions')
        raise e