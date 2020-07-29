import argparse
import os

import git
import github

from classroom_tools import github_utils
from classroom_tools.exceptions import *

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
         'Defaults to file paths specified within files_to_update.txt that is inside the template repo'
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


def get_files_to_update(files_to_update, template_repo):
    if files_to_update is None:
        try:
            index_file = 'scripts/files_to_update.txt'
            file = template_repo.get_contents(index_file)
            return set(file.decoded_content.decode('utf-8').splitlines())
        except Exception as e:
            print(e)
            raise Exception(f'Couldn\'t get file: {index_file}\nfrom template repo: {template_repo.full_name}')
    else:
        return set(files_to_update)


def copy_file_to_repo(file, repo):
    try:
        old_file = repo.get_contents(path=file.path)
        repo.update_file(
            path=file.path,
            message='Auto sync with template repo',
            content=file.decoded_content,
            sha=old_file.sha,
            branch='master'
        )
    except github.UnknownObjectException:
        repo.create_file(
            path=file.path,
            message='Auto sync with template repo',
            content=file.decoded_content,
            branch='master'
        )


if __name__ == '__main__':
    args = parser.parse_args()
    template_repo = github_utils.get_repo(args.template_repo_fullname, args.token)
    files_to_update = get_files_to_update(args.files_to_update, template_repo)
    template_files = list(
        filter(
            lambda file: file.path in files_to_update,
            github_utils.get_files_from_repo(repo=template_repo, path='')
        )
    )
    if args.as_student_repo_workflow:
        print(f'\nUpdating files in repo with files from:\t{template_repo.full_name}')
        git_repo = git.repo.Repo(path=args.git_repo_path)
        for file in template_files:
            print(f'\tSyncing: {file.path}')
            fullpath = os.path.abspath(os.path.join(args.git_repo_path + file.path))
            head, tail = os.path.split(fullpath)
            if not os.path.exists(head): os.makedirs(head)
            with open(fullpath, 'wb') as f:
                f.write(file.decoded_content)
            git_repo.index.add([fullpath])
        git_repo.index.commit('Auto sync with template repo')
        fetch_info = git_repo.remote('origin').pull()
        git_repo.remote('origin').push()
    else:
        if args.token == '':
            raise EmptyToken(permissions='repo, workflow')
        num_repos = 0
        repositories = github_utils.get_students_repositories(
            token=args.token,
            org_name=args.org_name,
            repo_filter=args.repo_filter
        )
        for repo in repositories:
            num_repos += 1
            print(f'\nUpdating files in:\t{repo.full_name}\nwith files from:\t{template_repo.full_name}')
            for file in template_files:
                print(f'\tSyncing: {file.path}')
                copy_file_to_repo(file=file, repo=repo)
        print('\nSummary:')
        print(f'\tTotal number of repositories updated: {num_repos}')
