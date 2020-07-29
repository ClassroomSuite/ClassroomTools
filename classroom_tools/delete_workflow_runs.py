import argparse

import github
import requests

parser = argparse.ArgumentParser()
parser.add_argument(
    '--token',
    required=True,
    help='GitHub personal access token with repo permissions'
)
parser.add_argument(
    '--repo_fullname',
    required=True,
    help='Repository fullname'
)
parser.add_argument(
    '--delete_only_failed_runs',
    default=False,
    action='store_true',
    help='Delete only workflow runs that failed'
)


def delete_workflow_run(workflow_url, token):
    print(f'Deleting: {workflow_url}')
    res = requests.delete(url=workflow_url,
                          headers={'Authorization': f'token {token}'})
    print('Success' if res.ok else 'Failed')


if __name__ == '__main__':
    args = parser.parse_args()
    g = github.Github(login_or_token=args.token)
    repo = g.get_repo(full_name_or_id=args.repo_fullname)

    if args.delete_only_failed_runs:
        workflow_runs = list(
            filter(
                lambda run: run.conclusion == 'failure',
                repo.get_workflow_runs()
            ),
        )
    else:
        workflow_runs = repo.get_workflow_runs()
    for workflow in repo.get_workflow_runs():
        delete_workflow_run(workflow.url, args.token)
