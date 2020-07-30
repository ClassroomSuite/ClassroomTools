import argparse

from classroom_tools import github_utils
from classroom_tools.exceptions import *

parser = argparse.ArgumentParser()
parser.add_argument(
    '--token',
    required=True,
    help='GitHub personal access token with repo and workflow permissions'
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
    '--template_repo_fullname',
    help='Add workflows from template repo used to create student repositories in format: OrgName/RepoName'
)
parser.add_argument(
    '--workflow_paths_to_ignore',
    nargs='*',
    help='List of workflow file paths to ignore from template repository'
)

if __name__ == '__main__':
    print('\n\n' + 'Updating workflows'.center(80, '='))
    args = parser.parse_args()
    print('Args:\n' + ''.join(f'\t{k}: {v}\n' for k, v in vars(args).items()))
    if args.token == '':
        raise EmptyToken(permissions='repo, workflow')
    template_workflow_files = []
    if args.template_repo_fullname is not None:
        template_repo = github_utils.get_repo(args.template_repo_fullname, args.token)
        template_workflow_files = list(
            github_utils.get_files_from_repo(repo=template_repo, path='.github/workflows/')
        )
    repositories = github_utils.get_students_repositories(
        token=args.token,
        org_name=args.org_name,
        repo_filter=args.repo_filter
    )
    num_repos = 0
    print('Updating workflows')
    for repo in repositories:
        print(f'\t{repo.full_name}:')
        if args.delete_previous_workflows:
            github_utils.delete_all_workflows(repo)
        to_ignore = set(args.workflow_paths_to_ignore)
        for file in template_workflow_files:
            if file.path not in to_ignore:
                github_utils.add_workflow(repo=repo, path=file.path, content=file.decoded_content)
        num_repos += 1
    print('\nSummary:')
    print(f'\tTotal number of repositories updated: {num_repos}')
