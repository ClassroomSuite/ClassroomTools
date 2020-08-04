import argparse

import github
import requests
from colorama import Fore, Style

from classroom_tools import github_utils

parser = argparse.ArgumentParser('Create test repositories')
parser.add_argument(
    '--token',
    required=True,
    help='GitHub personal access token with repo and workflow permissions'
)
parser.add_argument(
    '--template_repo_fullname',
    required=True,
    help='Template repo used to create student repositories in format: OrgName/RepoName'
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
parser.add_argument(
    '--num_repos',
    type=int,
    default=10,
    help='Number of student repositories to create'
)
parser.add_argument(
    '--private',
    type=bool,
    default=False,
    help='Test repositories privacy'
)
parser.add_argument(
    '--admin_collaborators',
    nargs='*',
    default=[],
    help='Collaborator usernames to receive admin access'
)
parser.add_argument(
    '--write_collaborators',
    nargs='*',
    default=[],
    help='Collaborator usernames to receive write access'
)


def student_usernames(n=10):
    return list(
        map(
            lambda i: f'PolyStudent{i}',
            range(1, n + 1)
        )
    )


def create_repo_from_template(token, template_repo_fullname, org_name, repo_name, description='', private=False):
    res = requests.post(
        url=f'https://api.github.com/repos/{template_repo_fullname}/generate',
        headers={
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.baptiste-preview+json'
        },
        json={
            'owner': org_name,
            'name': repo_name,
            'description': description,
            'private': private
        }
    )
    if res.ok:
        print(f'{Fore.GREEN}Created repo: {repo_name}')
    else:
        g = github.Github(login_or_token=token)
        try:
            g.get_repo(full_name_or_id=f'{org_name}/{repo_name}')
            print(f'{Fore.YELLOW}Repo already exists: {repo_name}')
        except github.UnknownObjectException:
            print(f'{Fore.RED}Failed to create repo: {repo_name}')
            raise Exception(res.text)


def main(args):
    print('\n\n' + 'Creating test repositories'.center(80, '='))
    args = parser.parse_args(args)
    print('Args:\n' + ''.join(f'\t{k}: {v}\n' for k, v in vars(args).items()))
    github_utils.verify_token(args.token)
    usernames = student_usernames(n=args.num_repos)
    g = github.Github(login_or_token=args.token)
    for name in usernames:
        repo_name = f'{args.repo_filter}-{name}'
        create_repo_from_template(
            token=args.token,
            template_repo_fullname=args.template_repo_fullname,
            org_name=args.org_name,
            repo_name=repo_name,
            description='Repository for testing classroom features at scale',
            private=args.private
        )
        repo = g.get_repo(full_name_or_id=f'{args.org_name}/{repo_name}')
        for col in args.admin_collaborators:
            repo.add_to_collaborators(col, permission='admin')
        for col in args.write_collaborators:
            repo.add_to_collaborators(col, permission='push')


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
    print(Style.RESET_ALL)
