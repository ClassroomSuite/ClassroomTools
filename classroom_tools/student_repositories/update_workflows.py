import argparse

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
    choices=[True, False],
    help='Delete all workflows from each selected student repositories (to prevent cheating)'
)
parser.add_argument(
    '--new_workflow_file',
    default='',
    help='A path to a %workflow%.yml file to add in students repositories'
)


def delete_workflow(repo, path):
    contents = repo.get_contents(path=path)
    repo.delete_file(
        path=path,
        message='Auto deleted workflow',
        sha=contents.sha,
        branch='master',
    )


def delete_all_workflows(repo):
    contents = repo.get_contents('.github/workflows/')
    for content_file in contents:
        delete_workflow(repo, path=content_file.path)


def add_workflow(repo, path):
    with open(path, 'r') as f:
        repo.create_file(
            path=path,
            message='Auto added workflow',
            content=f.read(),
            branch='master',
        )


if __name__ == '__main__':
    args = parser.parse_args()
    g = github.Github(login_or_token=args.TOKEN)
    org = g.get_organization(login=args.org_name)
    for repo in org.get_repos():
        if repo.name.find(args.repo_filter) != -1:
            if args.delete_previous_workflows:
                delete_all_workflows(repo)
            if args.new_workflow_file != '':
                add_workflow(repo, path=args.new_workflow_file)
