import argparse

from colorama import Fore

from classroom_tools import github_utils

parser = argparse.ArgumentParser(
    'Create a protected branch and pull request to grade student assignments')
parser.add_argument(
    '--token',
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
    help='Prefix to filter repositories for a given assignment or exercise'
)
parser.add_argument(
    '--head',
    required=True,
    help='Name branch of protected branch with all of the student\'s commits'
)
parser.add_argument(
    '--base',
    required=True,
    help='Name of protected branch on which to merge changes (this branch will only have the initial commit)'
)
parser.add_argument(
    '--pull_request_title',
    default='Grading',
    help='Pull request title'
)
parser.add_argument(
    '--pull_request_body',
    default='',
    help='Pull request title'
)


def get_first_commit(repo, branch_name='master'):
    commit = repo.get_branch(branch_name).commit
    while len(commit.parents) > 0:
        commit = commit.parents[0]
    return commit


def create_or_update_ref(repo, base):
    commit = get_first_commit(repo)
    try:
        ref = repo.get_git_ref(f'heads/{base}')
        ref.edit(sha=commit.sha, force=True)
    except:
        repo.create_git_ref(f'refs/heads/{base}', sha=commit.sha)


def add_push_restrictions(repo, base):
    branch = repo.get_branch(base)
    branch.edit_protection(
        user_push_restrictions=['']
    )


def main(args):
    print('\n\n' + 'Creating grading branches and pull requests'.center(80, '='))
    args = parser.parse_args(args)
    print('Args:\n' + ''.join(f'\t{k}: {v}\n' for k, v in vars(args).items()))
    github_utils.verify_token(args.token)
    repositories = github_utils.get_students_repositories(
        token=args.token,
        org_name=args.org_name,
        repo_filter=args.repo_filter
    )
    num_fail = 0
    for repo in repositories:
        print(f'Repo: {repo.full_name}')
        try:
            create_or_update_ref(repo=repo, base=args.base)
            add_push_restrictions(repo=repo, base=args.base)
        except:
            num_fail += 1
        try:
            repo.create_pull(
                title=args.pull_request_title,
                body=args.pull_request_body,
                base=args.base,
                head=args.head,
                maintainer_can_modify=False,
                draft=False
            )
        except Exception as e:
            print(f'\t{Fore.RED}Pull request already exists')
            for pull in repo.get_pulls():
                print(f'\t{pull}')
            print(e)
    print('\nSummary:')
    print(f'\tTotal number of repositories: {len(repositories)}')
    print(f'\tTotal number failed: {num_fail}')
    if num_fail > 0:
        raise Exception(f'{Fore.RED}Couldn\'t create protected branches')


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
