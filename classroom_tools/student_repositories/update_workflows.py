import argparse
import os

import github

parser = argparse.ArgumentParser()
parser.add_argument(
    '--TOKEN',
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
    '--delete_previous_workflows',
    default=False,
    type=bool,
    choices=[True, False],
    help='Delete all workflows from each selected student repositories (to prevent cheating)'
)
parser.add_argument(
    '--new_workflow_files',
    default=[],
    nargs='*',
    help='Paths to %workflow%.yml files to add in students repositories'
)


def delete_workflow(repo, path):
    print(f'\t\tRemoving: {path}')
    contents = repo.get_contents(path=path)
    repo.delete_file(
        path=path,
        message='Auto deleted workflow',
        sha=contents.sha,
        branch='master',
    )


def delete_all_workflows(repo):
    try:
        contents = repo.get_contents(path='.github/workflows/')
        for content_file in contents:
            delete_workflow(repo, path=content_file.path)
    except github.UnknownObjectException:
        pass


def get_workflow(src_path):
    with open(src_path, 'r') as f:
        content = f.read()
    if '.github/workflows/' not in src_path:
        head, tail = os.path.split(src_path)
        destination_path = '.github/workflows/' + tail
    return destination_path, content


def add_workflow(repo, path, content):
    print(f'\t\tAdding: {path}')
    try:
        old_file = repo.get_contents(path=path)
        repo.update_file(
            path=path,
            message='Auto added workflow',
            content=content,
            sha=old_file.sha,
            branch='master'
        )
    except github.UnknownObjectException:
        repo.create_file(
            path=path,
            message='Auto added workflow',
            content=content,
            branch='master'
        )


if __name__ == '__main__':
    args = parser.parse_args()
    g = github.Github(login_or_token=args.TOKEN)
    org = g.get_organization(login=args.org_name)
    print('Updating workflows\n')
    student_repos = org.get_repos()
    for repo in student_repos:
        if args.repo_filter in repo.name:
            print(f'\t{repo.full_name}:')
            if args.delete_previous_workflows:
                delete_all_workflows(repo)
            for src_path in args.new_workflow_files:
                destination_path, content = get_workflow(src_path)
                add_workflow(repo=repo, path=destination_path, content=content)
    print('\nSummary:')
    print(f'\tTotal number of repositories updated: {len(student_repos)}')
