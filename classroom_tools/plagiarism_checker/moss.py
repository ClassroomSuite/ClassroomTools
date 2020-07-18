import argparse
import datetime
import os

import git
import github
import mosspy
from classroom_tools import github_utils

parser = argparse.ArgumentParser()
parser.add_argument(
    '--user_id',
    help='Obtain a moss userid by following instructions from http://theory.stanford.edu/~aiken/moss/'
)
parser.add_argument(
    '--report_name',
    default='report',
    help='Obtain a moss userid by following instructions from http://theory.stanford.edu/~aiken/moss/'
)
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
parser.add_argument(
    '--paths',
    default=[],
    nargs='*',
    help='Paths to files in students repositories to subject to Moss'
)


def save_report(report_name, report_url):
    time_str = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
    report_path = f'./reports/{report_name}_{time_str}.html'
    head, tail = os.path.split(report_path)
    if not os.path.exists(os.path.abspath(head)): os.makedirs(head)
    moss.saveWebPage(url=report_url, path=report_path)
    git_repo = git.repo.Repo()
    git_repo.index.add([report_path])
    git_repo.index.commit(f'Moss report: {report_name}')
    fetch_info = git_repo.remote('origin').pull()
    git_repo.remote('origin').push()


if __name__ == '__main__':
    args = parser.parse_args()
    moss = mosspy.Moss(args.user_id, "python")
    g = github.Github(login_or_token=args.token)
    student_repositories = github_utils.get_students_repositories(g=g, org_name=args.org_name,
                                                                  repo_filter=args.repo_filter)
    print(f'Org: {args.org_name}')
    for path in args.paths:
        for repo in student_repositories:
            print(f'\t{repo.name}')
            content_file = repo.get_contents(path=path)
            _, ext = os.path.splitext(path)
            file_path = f'{repo.name}_{content_file.name}{ext}'
            with open(file_path, 'wb') as f:
                f.write(content_file.decoded_content)
            moss.addFile(file_path=file_path, display_name=repo.name)
    report_url = moss.send()
    save_report(args.report_name, report_url)
