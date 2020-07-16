import argparse

import github

parser = argparse.ArgumentParser(
    description='Update files in student repositories with files from the template repository'
)
parser.add_argument(
    '--token',
    required=True,
    help='GitHub personal access token with repo permissions'
)
parser.add_argument(
    '--org_name',
    help='GitHub organization with student repositories'
)
parser.add_argument(
    '--repo_filter',
    required=True,
    help='Prefix to filter repositories for as given assignment or exercise'
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


def get_files_from_repo(repo, path):
    contents = repo.get_contents(path=path)
    for content in contents:
        if content.type == 'dir':
            for _content in get_files_from_repo(repo, content.path):
                yield _content
        else:
            yield content


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
    files_to_update = set(args.files_to_update)
    g = github.Github(login_or_token=args.token)
    template_repo = g.get_repo(full_name_or_id=args.template_repo_fullname)
    template_files = list(
        filter(
            lambda file: file.path in files_to_update,
            get_files_from_repo(repo=template_repo, path='')
        )
    )
    org = g.get_organization(login=args.org_name)
    student_repos = list(
        filter(
            lambda repo: args.repo_filter in repo.name,
            org.get_repos()
        )
    )
    for repo in student_repos:
        print(f'\nUpdating files in:\t{repo.full_name}\nwith files from:\t{template_repo.full_name}')
        for file in template_files:
            print(f'\tSyncing: {file.path}')
            copy_file_to_repo(file=file, repo=repo)
