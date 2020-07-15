import argparse

import requests

parser = argparse.ArgumentParser()
parser.add_argument(
    '--MANAGE_ACCESS_TOKEN',
    required=True,
    help='GitHub personal access token with admin:org and repo permissions'
)
parser.add_argument(
    '--org_name',
    required=True,
    help='GitHub organization name'
)
parser.add_argument(
    '--repo_base_name',
    required=True,
    help='GitHub repo name'
)
parser.add_argument(
    '--new_permission_level',
    choices=['pull', 'push'],
    default='pull',
    help='Pull (read-only) or push (read, write)'
)


def get_repo_names(args):
    res = requests.get(
        url=f'https://api.github.com/orgs/{args.org_name}/repos',
        params={
            'type': 'all'
        },
        headers={'Authorization': f'token {args.MANAGE_ACCESS_TOKEN}'}
    )
    if res.ok:
        repo_names = []
        for repo in res.json():
            if repo['name'].find(args.repo_base_name) != -1 and len(repo['name']) > len(args.repo_base_name):
                repo_names.append(repo['full_name'])
        return repo_names
    else:
        raise Exception(f'Couldn\'t fetch repositories from organization: {args.org_name}\n')

def get_collaborators(args, repo_name):
    res = requests.get(
        url=f'https://api.github.com/repos/{repo_name}/collaborators',
        params={
            'affiliation': 'all'
        },
        headers={'Authorization': f'token {args.MANAGE_ACCESS_TOKEN}'}
    )
    if res.ok:
        return res.json()
    else:
        raise Exception(f'Couldn\'t fetch collaborators from repository: {args.org_name}/{repo_name}\n')


def change_access_permission(args, repo_name, collaborators):
    urls = []
    for collaborator in collaborators:
        if collaborator['permissions']['admin'] == False:
            login = collaborator['login']
            urls.append(f'https://api.github.com/repos/{repo_name}/collaborators/{login}')
    for url in urls:
        res = requests.put(
            url=url,
            json={
                'permission': args.new_permission_level
            },
            headers={'Authorization': f'token {args.MANAGE_ACCESS_TOKEN}'}
        )

def confirm_changes(args, repo_fullnames):
    num_ok = 0
    num_fail = 0
    for repo_fullname in repo_fullnames:
        collaborators = get_collaborators(args, repo_fullname)
        for collaborator in collaborators:
            if collaborator['permissions']['admin'] == False:
                login = collaborator['login']
                if collaborator['permissions']['pull'] and args.new_permission_level == 'pull':
                    print(f'Permission: pull\t {repo_fullname}/{login}')
                    num_ok += 1
                elif collaborator['permissions']['push'] and args.new_permission_level == 'push':
                    print(f'Permission: push\t {repo_fullname}/{login}')
                    num_ok += 1
                else:
                    print(f'\nERROR {repo_fullname}/{login}')
                    print(collaborator['permissions'], end='\n\n')
                    num_fail += 1
    print('\nSummary:')
    print(f'\tTotal number of successful permission changes: {num_ok}')
    print(f'\tTotal number of failed permission changes: {num_fail}')
    if num_fail != 0:
        print('Couldn\'t apply permission changes')
        exit(1)


if __name__ == '__main__':
    args = parser.parse_args()
    try:
        repo_names = get_repo_names(args)
        for name in repo_names:
            collaborators = get_collaborators(args, name)
            change_access_permission(args, name, collaborators)
    except Exception as e:
        print(e)
        print('Verify that your Personal access token is accessible and has the repo and org:admin permissions')
    confirm_changes(args, repo_names)
