import argparse

import github
from colorama import Fore

from classroom_tools import github_utils

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
    github_utils.verify_token(args.token)
    g = github.Github(login_or_token=args.token)
    template_repo = g.get_repo(full_name_or_id=args.template_repo_fullname)
    file = template_repo.get_contents('settings/files_to_update.txt')
    paths_to_update = set(file.decoded_content.decode('utf-8').splitlines())
    template_files = list(github_utils.get_files_from_repo(repo=template_repo, path=''))
    template_paths = set(
        map(
            lambda file: file.path,
            template_files
        )
    )
    print(f'From repository: {template_repo.full_name}')
    for path in paths_to_update.intersection(template_paths):
        print(f'{Fore.GREEN}\tFound: {path}')
    for path in template_paths.difference(paths_to_update):
        print(f'{Fore.YELLOW}\tNot included: {path}')
    for path in paths_to_update.difference(template_paths):
        print(f'{Fore.RED}\tMissing: {path}')
        raise Exception(f'{Fore.RED}Missing or incorrect paths')


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
