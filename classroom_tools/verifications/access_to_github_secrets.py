import argparse
import json
import re

import github
import requests
from colorama import Fore, Style

from classroom_tools import github_utils

parser = argparse.ArgumentParser('Verify that a repo has access to the secrets it needs')
parser.add_argument(
    '--token',
    required=True,
    help='GitHub personal access token with repo and admin:org permissions'
)
parser.add_argument(
    '--repo_fullname',
    required=True,
    help='Repo fullname in format: OrgName/RepoName'
)


def find_secrets(string):
    matches = re.findall(
        pattern='\$\{[ ]*\{[ ]*secrets\.[a-zA-Z0-9\_]*',
        string=string
    )
    for match in matches:
        _, secret = match.split('secrets.')
        yield secret


def _get_available_org_secrets(token, repo):
    org_name = repo.full_name.split('/')[0]
    res = requests.get(
        url=f'https://api.github.com/orgs/{org_name}/actions/secrets',
        headers={'Authorization': f'token {token}'}
    )
    if res.ok:
        available_secrets = set()
        org_secrets = json.JSONDecoder().decode(res.text)['secrets']
        for secret in org_secrets:
            if secret['visibility'] == 'all':
                available_secrets.add(secret['name'])
            elif secret['visibility'] == 'private' and repo.private:
                available_secrets.add(secret['name'])
            elif secret['visibility'] == 'selected':
                res = requests.get(
                    url=secret['selected_repositories_url'],
                    headers={'Authorization': f'token {token}'}
                )
                if res.ok:
                    repositories = json.JSONDecoder().decode(res.text)['repositories']
                    for selected_repo in repositories:
                        if selected_repo['full_name'] == repo.full_name:
                            available_secrets.add(secret['name'])
        return available_secrets
    else:
        raise Exception(f'Could\'t verify organization secrets for: {org_name}')


def _get_available_repo_secrets(token, repo):
    res = requests.get(
        url=f'https://api.github.com/repos/{repo.full_name}/actions/secrets',
        headers={'Authorization': f'token {token}'}
    )
    if res.ok:
        repo_secrets = json.JSONDecoder().decode(res.text)['secrets']
        return set(
            map(
                lambda secret: secret['name'],
                repo_secrets
            )
        )
    else:
        raise Exception(f'Could\'t verify repo secrets for: {repo.full_name}')


def get_available_secrets(token, repo_fullname):
    g = github.Github(login_or_token=token)
    repo = g.get_repo(full_name_or_id=repo_fullname)
    org_secrets = _get_available_org_secrets(token=token, repo=repo)
    repo_secrets = _get_available_repo_secrets(token=token, repo=repo)
    return org_secrets.union(repo_secrets)


def get_required_secrets(token, repo_fullname):
    g = github.Github(login_or_token=token)
    repo = g.get_repo(full_name_or_id=repo_fullname)
    workflow_files = github_utils.get_files_from_repo(repo=repo, path='.github/workflows')
    all_required_secrets = set()
    required_secrets = {}
    for file in workflow_files:
        required_secrets[file.path] = set(find_secrets(str(file.decoded_content)))
        all_required_secrets = all_required_secrets.union(required_secrets[file.path])
    return required_secrets, all_required_secrets


def main(args):
    print('\n\n' + 'Verifying access to secrets'.center(80, '='))
    args = parser.parse_args(args)
    print('Args:\n' + ''.join(f'\t{k}: {v}\n' for k, v in vars(args).items()))
    github_utils.verify_token(args.token)
    available_secrets = get_available_secrets(token=args.token, repo_fullname=args.repo_fullname)
    required_secrets, all_required_secrets = get_required_secrets(token=args.token, repo_fullname=args.repo_fullname)

    print(
        f'\n{Fore.GREEN}Repo {args.repo_fullname}\n'
        f'{Fore.GREEN}has access to:\n\t{Fore.GREEN}'
        + f'\n\t{Fore.GREEN}'.join(available_secrets)
    )
    missing = all_required_secrets.difference(available_secrets)
    if len(missing) > 0:
        print(
            f'\n{Fore.RED}Repo {args.repo_fullname}\n'
            f'{Fore.RED}doesn\'t have access to the following secrets:\n\t{Fore.RED}'
            + f'\n\t{Fore.RED}'.join(missing)
        )
    for path, secrets in required_secrets.items():
        print(f'\nWorkflow {path}\nrequires access to:')
        for secret_ in secrets:
            if secret_ in available_secrets:
                print(f'{Fore.GREEN}\t{secret_}')
            else:
                print(f'{Fore.RED}\t{secret_}')
    print(Style.RESET_ALL)
    if len(missing) > 0:
        exit(1)


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
