import argparse

import github

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


def delete_file(repo, path):
    try:
        contents = repo.get_contents(path=path)
        repo.delete_file(
            path=path,
            message='Deleted file',
            sha=contents.sha,
            branch='master',
        )
        print(f'Deleted: {path}\n from: {repo.full_name}')
    except github.UnknownObjectException:
        print(f'File doesn\'t exist: {path}')


if __name__ == '__main__':
    args = parser.parse_args()
    if args.token == '':
        raise EmptyToken(permissions='repo')
    g = github.Github(login_or_token=args.token)
    org = g.get_organization(login=args.org_name)
    num_repos = 0
    for repo in org.get_repos():
        if args.repo_filter in repo.name:
            delete_file(repo, args.path)
        num_repos += 1
    print('\nSummary:')
    print(f'\tTotal number of repositories updated: {num_repos}')
