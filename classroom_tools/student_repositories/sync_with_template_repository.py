import argparse
import os

import git
from colorama import Fore

from classroom_tools import github_utils

parser = argparse.ArgumentParser(
    description='Update files in student repositories with files from the template repository'
)
parser.add_argument(
    '--template_repo_fullname',
    required=True,
    help='Template repo used to create student repositories in format: OrgName/RepoName'
)
parser.add_argument(
    '--files_to_update',
    nargs='*',
    help='List of file paths to copy from template repository to student repositories.'
         'Defaults to file paths specified within settings/files_to_update.txt that is inside the template repo'
)
parser.add_argument(
    '--as_student_repo_workflow',
    default=False,
    action='store_true',
    help=
    """
    Template files will be written to the local student repo and git commands will be used to
    commit/push changes.
    Otherwise, the GitHub API will be used to create/update the files in all the student repositories
    matching the --repo_filter within --org_name.
    """
)
# For workflows inside a single student repository: as_student_repo_workflow=True
parser.add_argument(
    '--git_repo_path',
    default='',
    help='Used only if --as_student_repo_workflow is True'
)
# For workflows outside of student repositories: as_student_repo_workflow=False
parser.add_argument(
    '--token',
    help='GitHub personal access token with repo and workflow permissions'
)
parser.add_argument(
    '--org_name',
    help='GitHub organization with student repositories (for multiples student repositories)'
)
parser.add_argument(
    '--repo_filter',
    help='Prefix to filter repositories for as given assignment or exercise (for multiples student repositories)'
)


def _get_paths_to_update(files_to_update, template_repo):
    if files_to_update is None:
        try:
            index_file = 'settings/files_to_update.txt'
            file = template_repo.get_contents(index_file)
            return set(file.decoded_content.decode('utf-8').splitlines())
        except Exception as e:
            print(e)
            raise Exception(f'Couldn\'t get file: {index_file}\nfrom template repo: {template_repo.full_name}')
    else:
        return set(files_to_update)


def get_relevant_template_files(files_to_update, template_repo):
    paths_to_update = _get_paths_to_update(files_to_update=files_to_update, template_repo=template_repo)
    template_files = set(github_utils.get_files_from_repo(repo=template_repo, path=''))
    relevant = set()
    for file in template_files:
        if file.path in paths_to_update:
            relevant.add(file)
        else:
            print(f'{Fore.RED}File not found in template repo:\n\t{Fore.RED}{file}')
    return relevant


def update_as_student_repo(files_to_update, template_repo_fullname, git_repo_path):
    template_repo = github_utils.get_repo(fullname=template_repo_fullname)
    template_files = get_relevant_template_files(
        files_to_update=files_to_update,
        template_repo=template_repo
    )
    print(f'\nUpdating files in repo with files from:\t{template_repo.full_name}')
    git_repo = git.repo.Repo(path=git_repo_path)
    for file in template_files:
        print(f'\tSyncing: {file.path}')
        fullpath = os.path.abspath(os.path.join(git_repo_path + file.path))
        head, tail = os.path.split(fullpath)
        if not os.path.exists(head): os.makedirs(head)
        with open(fullpath, 'wb') as f:
            f.write(file.decoded_content)
        git_repo.index.add([fullpath])
    git_repo.index.commit('Auto sync with template repo')
    fetch_info = git_repo.remote('origin').pull()
    git_repo.remote('origin').push()


def update_with_github_api(files_to_update, template_repo_fullname, token, org_name, repo_filter):
    github_utils.verify_token(token)
    template_repo = github_utils.get_repo(fullname=template_repo_fullname, token=token)
    template_files = get_relevant_template_files(
        files_to_update=files_to_update,
        template_repo=template_repo
    )
    repositories = github_utils.get_students_repositories(
        token=token,
        org_name=org_name,
        repo_filter=repo_filter
    )
    for repo in repositories:
        print(f'\nUpdating files in:\t{repo.full_name}\nwith files from:\t{template_repo.full_name}')
        for file in template_files:
            print(f'\tSyncing: {file.path}')
            github_utils.copy_file_to_repo(file=file, repo=repo)
    print('\nSummary:')
    print(f'\tTotal number of repositories updated: {len(repositories)}')


def main(args):
    print('\n\n' + 'Sync with template repository'.center(80, '='))
    args = parser.parse_args(args)
    print('Args:\n' + ''.join(f'\t{k}: {v}\n' for k, v in vars(args).items()))
    if args.as_student_repo_workflow:
        update_as_student_repo(
            files_to_update=args.files_to_update,
            template_repo_fullname=args.template_repo_fullname,
            git_repo_path=args.git_repo_path
        )
    else:
        update_with_github_api(
            files_to_update=args.files_to_update,
            template_repo_fullname=args.template_repo_fullname,
            token=args.token,
            org_name=args.org_name,
            repo_filter=args.repo_filter
        )


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
