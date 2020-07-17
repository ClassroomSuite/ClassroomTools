import argparse
import os

import git
import github

parser = argparse.ArgumentParser(
    description='Update files in student repositories with files from the template repository'
)
parser.add_argument(
    '--template_repo_fullname',
    required=True,
    default='INF1007-Exercices/TemplateExercise1',
    help='Template repo used to create student repositories in format: "Organization/RepositoryName"'
)
parser.add_argument(
    '--files_to_update',
    required=True,
    nargs='*',
    help='List of file paths to copy from template repository to student repositories'
)
parser.add_argument(
    '--as_student_repo_workflow',
    required=True,
    default=True,
    type=bool,
    help=
    """
    If true, template files will be written to the local student repo and git commmands will be used to
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
    help='GitHub personal access token with repo permissions'
)
parser.add_argument(
    '--org_name',
    help='GitHub organization with student repositories (for multiples student repositories)'
)
parser.add_argument(
    '--repo_filter',
    help='Prefix to filter repositories for as given assignment or exercise (for multiples student repositories)'
)


def get_files_from_repo(repo, path):
    contents = repo.get_contents(path=path)
    for content in contents:
        if content.type == 'dir':
            for _content in get_files_from_repo(repo, content.path):
                yield _content
        else:
            yield content


def get_repo(fullname, g: github.Github):
    try:
        return g.get_repo(full_name_or_id=fullname)
    except Exception as e:
        print(e)
        raise Exception(f'Couldn\'t get repo: {fullname}')


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


def get_students_repositories(args, g: github.Github):
    try:
        org = g.get_organization(login=args.org_name)
        student_repos = list(
            filter(
                lambda repo: args.repo_filter in repo.name,
                org.get_repos()
            )
        )
        return student_repos
    except Exception as e:
        print(e)
        raise Exception(f'Couldn\'t get organization: {args.org_name}')


if __name__ == '__main__':
    args = parser.parse_args()
    files_to_update = set(args.files_to_update)
    g = github.Github(login_or_token=args.token)
    template_repo = get_repo(args.template_repo_fullname, g)
    template_files = list(
        filter(
            lambda file: file.path in files_to_update,
            get_files_from_repo(repo=template_repo, path='')
        )
    )
    if args.as_student_repo_workflow:
        print(f'\nUpdating files in repo with files from:\t{template_repo.full_name}')
        git_repo = git.repo.Repo(path=args.git_repo_path)
        for file in template_files:
            head, tail = os.path.split(file.path)
            fullpath = os.path.abspath(args.git_repo_path + file.path)
            if not os.path.exists(head):
                os.makedirs(head)
            with open(fullpath, 'wb') as f:
                print(f'\tSyncing: {file.path}')
                f.write(file.decoded_content)
            added = git_repo.index.add([fullpath])
            print(added)
        commit = git_repo.index.commit('Auto sync with template repo')
        print(commit)
        fetch_info = git_repo.remote('origin').pull()
        git_repo.remote('origin').push()
        git_repo.heads.master.log()
    else:
        for repo in get_students_repositories(args, g):
            print(f'\nUpdating files in:\t{repo.full_name}\nwith files from:\t{template_repo.full_name}')
            for file in template_files:
                print(f'\tSyncing: {file.path}')
                copy_file_to_repo(file=file, repo=repo)
