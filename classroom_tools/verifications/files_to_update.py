import argparse

import github
from colorama import Fore, Style

from classroom_tools import github_utils
from classroom_tools.student_repositories.sync_with_template_repository import get_files_to_update

parser = argparse.ArgumentParser('Validate paths specified in files_to_update.txt')
parser.add_argument(
    '--token',
    required=True,
    help='GitHub personal access token with repo permissions'
)
parser.add_argument(
    '--template_repo_fullname',
    required=True,
    help='Template repo used to create student repositories in format: OrgName/RepoName'
)


def main(args):
    print('\n\n' + 'Verifying files_to_update.txt'.center(80, '='))
    args = parser.parse_args(args)
    print('Args:\n' + ''.join(f'\t{k}: {v}\n' for k, v in vars(args).items()))
    g = github.Github(login_or_token=args.token)
    template_repo = g.get_repo(full_name_or_id=args.template_repo_fullname)
    files_to_update = get_files_to_update(files_to_update=None, template_repo=template_repo)
    print(f'From repository: {template_repo.full_name}')
    missing = []
    repo_files = set(
        map(
            lambda file: file.path,
            github_utils.get_files_from_repo(repo=template_repo, path='')
        )
    )
    for path in files_to_update:
        if path in repo_files:
            print(f'{Fore.GREEN}\tFound: {path}')
        else:
            missing.append(path)
    for path in repo_files.difference(files_to_update):
        print(f'{Fore.YELLOW}\tNot included: {path}')
    if len(missing) > 0:
        for path in missing:
            print(f'{Fore.RED}\tMissing: {path}')
        exit(1)

    print(Style.RESET_ALL)


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
